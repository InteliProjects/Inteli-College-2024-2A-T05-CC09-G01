# Metodologia: Processamento e Seleção de Imagens de Olhos Bovinos

Nossa abordagem metodológica seguiu três etapas principais: (1) aquisição e pré-processamento de dados, (2) seleção de imagens diversas, e (3) anotação e criação de máscaras. Este processo viabilizou a obtenção de um conjunto de dados de alta qualidade e diversidade para o treinamento de modelos de detecção de olhos bovinos em imagens térmicas.

## 1. Aquisição e Pré-processamento de Dados

A extração de quadros foi realizada utilizando um algoritmo baseado na biblioteca OpenCV, selecionada por sua eficiência computacional e versatilidade[4]. O algoritmo de extração é definido pela função:

$$E : V \times \mathbb{R}^+ \to \mathcal{P}(I)$$
$$E(v, f) = \{I_t \in I \mid t = \lfloor n \cdot f \rfloor, n \in \mathbb{N}, 0 \leq n < \lfloor L/f \rfloor\}$$
onde $V$ é o espaço de vídeos, $I$ é o espaço de imagens, e $\mathcal{P}(I)$ é o conjunto potência de $I$.

## 2. Análise de Diversidade e Seleção de Amostras

Após a extração dos frames, implementamos um processo de seleção para garantir a diversidade das imagens. Este processo envolveu três etapas principais:

### 2.1 Extração de Características de Alto Nível

Utilizamos uma arquitetura VGG16 [1] pré-treinada para extrair vetores de características de alto nível das imagens. O processo foi realizado em lotes para otimizar o desempenho.

```
Função ExtrairCaracteristicasEmLotes(caminho_pasta, tamanho_lote):
    caminhos_imagens = ListarImagensNaPasta(caminho_pasta)

    caracteristicas = []
    Para cada lote em caminhos_imagens com tamanho tamanho_lote:

        imagens_lote = CarregarEPreprocessarImagens(lote)
        caracteristicas_lote = modelo.Prever(imagens_lote)
        Adicionar caracteristicas_lote a caracteristicas

        Retornar caracteristicas, caminhos_imagens
```

### 2.2 Redução de Dimensionalidade via PCA

Aplicamos Análise de Componentes Principais (PCA) [2] para reduzir a dimensionalidade dos vetores de características, mantendo 95% da variância total. O número ótimo de componentes principais $k^*$ foi determinado por:

Seja $\Sigma \in \mathbb{R}^{n \times n}$ a matriz de covariância dos dados e $\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_n$ seus autovalores. Definimos o número ótimo de componentes principais $k^*$ como:
   $$k^* = \arg\min_{k \in \mathbb{N}} \left\{k \mid \frac{\sum_{i=1}^k \lambda_i}{\text{tr}(\Sigma)} \geq 0.95\right\}$$
   onde $\text{tr}(\Sigma) = \sum_{i=1}^n \lambda_i$ é o traço da matriz $\Sigma$.

O processo de determinação do número ótimo de componentes é realizado da seguinte forma:

```
Função DeterminarComponentesOtimos(caracteristicas):
    pca = InicializarPCA()
    pca.Ajustar(caracteristicas)
    variancia_explicada = CalcularVarianciaExplicadaAcumulada(pca)

    Para i de 1 até Tamanho(variancia_explicada):
        Se variancia_explicada[i] >= 0.95:
        Retornar i

    Retornar Tamanho(variancia_explicada)
```

![Variância Explicada vs. Número de Componentes](/artefatos/img/PCA.png)

*Figura 1: Gráfico da variância explicada acumulada em função do número de componentes principais.*

### 2.3 Clusterização por K-Means

Implementamos o algoritmo K-Means [3] para agrupar imagens similares, utilizando o método do cotovelo para determinar o número ótimo de clusters. A seleção final das imagens foi baseada em uma métrica de diversidade que maximiza a distância euclidiana média aos centróides dos clusters:

$$J = \sum_{j=1}^k \sum_{i=1}^{n_j} \|x_i^{(j)} - \mu_j\|^2$$

onde $k$ é o número de clusters, $n_j$ é o número de pontos no cluster $j$, $x_i^{(j)}$ é o i-ésimo ponto no cluster $j$, e $\mu_j$ é o centróide do cluster $j$.

Para determinar o número ótimo de clusters, utilizamos o método do cotovelo:

```
Função CalcularWCSS(caracteristicas, max_clusters):
    wcss = []

    Para k de 1 até max_clusters:
        kmeans = InicializarKMeans(k)
        kmeans.Ajustar(caracteristicas)
        Adicionar kmeans.Inercia a wcss
        Retornar wcss
        
    Função PlotarMetodoCotovelo(wcss):
    Plotar(range(1, Tamanho(wcss) + 1), wcss)
    ExibirGrafico()
```

![Método do Cotovelo para Número Ótimo de Clusters](/artefatos/img/ElbowMethod.png)

*Figura 2: Gráfico do método do cotovelo para determinar o número ótimo de clusters.*

### 2.4 Métrica de Diversidade e Seleção Final

E finalmente desenvolvemos um algoritmo de diversidade baseado na distância euclidiana média aos centróides dos clusters:

```
Função SelecionarImagensDiversas(caracteristicas_reduzidas, clusters, caminhos_imagens, n_selecionar=5000):
    clusters_unicos = ObterValoresUnicos(clusters)
    centroides = []
    
    Para cada cluster em clusters_unicos:
        pontos_do_cluster = ObterPontosDoCluster(caracteristicas_reduzidas, clusters, cluster)
        centroide = CalcularMedia(pontos_do_cluster)
        Adicionar centroide a centroides
    
    distancias = CalcularDistanciasEuclidianas(caracteristicas_reduzidas, centroides)
    scores_diversidade = CalcularMediaPorLinha(distancias)
    
    indices_ordenados = OrdenarIndicesDecrescente(scores_diversidade)
    indices_selecionados = ObterPrimeirosN(indices_ordenados, n_selecionar)
    
    imagens_selecionadas = []
    Para cada indice em indices_selecionados:
        Adicionar caminhos_imagens[indice] a imagens_selecionadas
    
    Retornar imagens_selecionadas
```
A seleção final maximiza a diversidade global:
$$\text{Imagens Selecionadas} = {x_i \mid D(x_i) \geq D(x_{5000})}$$
Esta abordagem assegura uma seleção de imagens que representa adequadamente a variabilidade do conjunto de dados.

## 3. Sistema de Anotação e Criação de Máscaras

Com o conjunto diversificado de imagens selecionado, foi iniciado o processo de anotação manual para a identificação da cabeça e dos olhos dos gados. Para isso, utilizou-se a ferramenta Computer Vision Annotation Tool (CVAT) [4], escolhida por sua facilidade de uso, independência de bibliotecas externas, e eficácia comprovada [5].

Para a anotação, foram utilizadas caixas de seleção no formato retangular. Labels específicas foram definidas para categorizar e identificar cada retângulo, com o objetivo de identificar as cabeças e os olhos dos bovinos, que constituem as regiões de interesse (ROIs) para a segmentação das imagens. A anotação foi realizada quadro a quadro no conjunto de imagens selecionado, gerando uma visualização dos retângulos de seleção e seus respectivos IDs. Uma visualização combinada dos IDs, caixas delimitadoras e anotações é apresentada na figura 3.

![Frame com as labels](/artefatos/img/box_label.png)
Figura 3: Exemplo de um frame com as labels adicionadas.

Através dessa ferramenta, tivemos a possibilidade de exportar as anotações para diversos formatos diferentes, dependendo do input necessário para a criação das máscaras. Para este caso, escolhemos o formato XML, por permitir uma classificação e categorização eficiente e precisa, além de manter a integridade dos dados. Para a criação das máscaras das ROIs, desenvolvemos um script personalizado para processar as anotações exportadas do CVAT, redimensionando as imagens para 128x128 pixels para padronizar o banco de dados e convertendo-as em máscaras binárias apropriadas para o treinamento de modelos de IA. O processo é descrito no pseudocódigo a seguir:

```
Função ProcessarAnotacoesCVAT(arquivo_xml, pasta_saida_x, pasta_saida_y):
    CriarPastas(pasta_saida_x, pasta_saida_y)
    anotacoes = AnalisarXML(arquivo_xml)
    Para cada imagem em anotacoes:
        imagem_original = CarregarImagem(ObterNomeImagem(imagem))
        areas, cabecas, olhos = ClassificarCaixas(imagem.caixas)
        
        Para cada idx, area em Enumerar(areas):
            nome_x, nome_y = GerarNomesArquivos(imagem.nome, idx)
            
            imagem_recortada = RecortarERedimensionar(imagem_original, area, 128, 128)
            SalvarImagem(imagem_recortada, pasta_saida_x, nome_x)
            
            cabeca_rel = EncontrarElementoRelevante(area, cabecas)
            olhos_rel = EncontrarElementosRelevantes(area, olhos)
            
            mascara = CriarMascara(imagem_original.tamanho, area, cabeca_rel, olhos_rel)
            mascara_processada = ProcessarMascara(mascara, area, 128, 128)
            SalvarImagem(mascara_processada, pasta_saida_y, nome_y)

Função CriarMascara(tamanho, area, cabeca, olhos):
    mascara = CriarImagemVazia(tamanho)
    DesenharRetangulo(mascara, area, PRETO)
    
    Se cabeca: DesenharRetangulo(mascara, cabeca, BRANCO)
    Para cada olho em olhos: DesenharRetangulo(mascara, olho, VERMELHO)
    
    Retornar mascara

    Função EncontrarElementoRelevante(area, elementos):
        Retornar Primeiro(elemento for elemento in elementos if ElementoDentroDeArea(elemento, area))

    Função EncontrarElementosRelevantes(area, elementos):
    Retornar [elemento for elemento in elementos if ElementoDentroDeArea(elemento, area)]
```

Este processo assegura a conversão eficiente das anotações do CVAT em um formato otimizado para o treinamento de modelos de segmentação, preservando a integridade das informações originais e facilitando o pareamento entre imagens e máscaras durante o treinamento. A abordagem de segmentação hierárquica (área, cabeça, olhos) permite uma análise detalhada e precisa dos olhos bovinos em imagens térmicas, fundamental para o sucesso do modelo.

![Processo de criação das máscaras](/artefatos/img/process.png)

Figura 4: Exemplo do processo de anotação até a criação da máscara.



## Referências
[1] Shaha M, Pawar M. Transfer Learning for Image Classification. In: 2018 Second International Conference on Electronics, Communication and Aerospace Technology (ICECA); 2018 Mar 29-31; Coimbatore, India. IEEE; 2018. p. 656-60. doi: 10.1109/ICECA.2018.8474802.

[2] Aslam S, Rabie TF. Principal Component Analysis in Image Classification: A review. In: 2023 Advances in Science and Engineering Technology International Conferences (ASET); 2023 Feb 6-9; Dubai, United Arab Emirates. IEEE; 2023. p. 1-7. doi: 10.1109/ASET56582.2023.10180847.

[3] Dehariya VK, Shrivastava SK, Jain RC. Clustering of Image Data Set Using K-Means and Fuzzy K-Means Algorithms. In: 2010 International Conference on Computational Intelligence and Communication Networks (CICN); 2010 Nov 26-28; Bhopal, India. IEEE; 2010. p. 386-91. doi: 10.1109/CICN.2010.80.

[4] “CVAT Overview.” CVAT. Available from: https://docs.cvat.ai/docs/getting_started/overview/. Accessed August 15, 2024.

[5] Musleh A, AlRyalat SA, Qasem A. Image Annotation Software for Artificial Intelligence Applications. High Yield Med Rev. 2023 Dec;1(2).




