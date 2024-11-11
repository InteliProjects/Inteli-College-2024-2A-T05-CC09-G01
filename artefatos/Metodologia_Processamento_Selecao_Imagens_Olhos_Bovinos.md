Metodologia:
Como foi feita a aquisição das imagems?
Seleção dos olhos - referencia godoy
label - cvat + criação das mascaras
Pré-processamento: data augmentaion, filtros (clah e contraste no x)





# Metodologia: Processamento e Seleção de Imagens de Olhos Bovinos

Nossa metodologia seguiu três etapas principais: (1) aquisição e pré-processamento de dados, (2) seleção de imagens diversas, e (3) anotação e criação de máscaras. Essas etapas permitiram construir um conjunto de dados robusto e variado para o treinamento de modelos de detecção de olhos bovinos em imagens térmicas.

## 1. Aquisição e Pré-processamento de Dados

As imagens foram extraídas de vídeos utilizando a biblioteca OpenCV, conhecida por sua eficiência e versatilidade. A função de extração é definida por:

$$E : V \times \mathbb{{R}}^+ \to \mathcal{{P}}(I)$$
$$E(v, f) = \{{I_t \in I \mid t = \lfloor n \cdot f \rfloor, n \in \mathbb{{N}}, 0 \leq n < \lfloor L/f \rfloor\}}$$

onde $V$ representa o espaço de vídeos, $I$ o espaço de imagens, e $\mathcal{P}(I)$ o conjunto potência de $I$ [1].

## 2. Seleção de Imagens Diversas

### 2.1 Extração de Características

Características de alto nível foram extraídas usando a arquitetura VGG16 pré-treinada, processadas em lotes para otimizar a performance [2].

### 2.2 Redução de Dimensionalidade

A Análise de Componentes Principais (PCA) foi utilizada para reduzir a dimensionalidade dos vetores de características, preservando 95% da variância [3]. O número ótimo de componentes principais foi determinado por:

$$k^* = \arg\min_{{k \in \mathbb{{N}}}} \left\{k \mid \frac{{\sum_{{i=1}}^k \lambda_i}}{{\text{{tr}}(\Sigma)}} \geq 0.95\right\}$$

### 2.3 Clusterização

O algoritmo K-Means foi aplicado para agrupar imagens similares. O número ótimo de clusters foi determinado pelo método do cotovelo [4].

### 2.4 Seleção Final

Desenvolvemos um algoritmo de diversidade que maximiza a distância média aos centróides dos clusters, assegurando a seleção de imagens representativas da variabilidade do conjunto de dados [5].

## 3. Anotação e Criação de Máscaras

Utilizamos a ferramenta CVAT para a anotação das imagens, com foco na identificação de cabeças e olhos bovinos. As anotações foram exportadas em formato XML, que permitiu uma categorização eficiente e precisa. Um script personalizado foi desenvolvido para converter essas anotações em máscaras binárias, padronizando as imagens para 128x128 pixels, prontas para o treinamento de modelos de IA [6][7].

### Processo de Criação das Máscaras

O processo de criação das máscaras envolveu as seguintes etapas:

1. **Processamento das Anotações:** As anotações foram processadas para identificar as regiões de interesse (ROIs) das cabeças e olhos bovinos.
2. **Redimensionamento das Imagens:** As imagens foram recortadas e redimensionadas para 128x128 pixels para garantir a padronização do banco de dados.
3. **Geração das Máscaras:** As máscaras foram criadas destacando as ROIs e foram convertidas em formato binário, apropriadas para o treinamento de modelos de IA.

O pseudocódigo a seguir descreve o processo:

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
```

![Frame com as labels](/artefatos/img/box_label.png)
*Figura 1: Exemplo de um frame com as labels adicionadas.*

![Processo de criação das máscaras](/artefatos/img/process.png)
*Figura 2: Exemplo do processo de anotação até a criação da máscara.*

## Referências

