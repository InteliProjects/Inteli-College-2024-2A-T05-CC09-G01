# Relatório: Processamento e Seleção de Imagens de Olhos Bovinos

## 1. Análise dos Vídeos

Começamos baixando e analisando cuidadosamente os vídeos fornecidos. Nosso foco era identificar seções que contivessem olhos de bovinos claros e nítidos. Essa etapa manual foi crucial para garantir que estávamos trabalhando com o material mais relevante.

## 2. Extração de Frames

Desenvolvemos um [script](../codigo/data_pre_processing/main.py) utilizando a biblioteca OpenCV para converter os vídeos em frames. Optamos pelo OpenCV devido à sua eficiência e facilidade de uso. Nosso script extraiu frames a uma taxa de X frames por segundo, equilibrando entre capturar detalhes suficientes e evitar redundância excessiva.

## 3. Processamento das Imagens

Após a extração, processamos cada imagem aplicando técnicas de cropping e redimensionamento. Utilizamos algoritmos de detecção de objetos para localizar os olhos nas imagens e fazer o cropping preciso. Em seguida, redimensionamos as imagens para um tamanho padrão de 128x128, garantindo consistência no conjunto de dados.

## 4. Garantia de Diversidade

Para assegurar a diversidade das imagens, implementamos uma [abordagem sofisticada](../codigo/data_pre_processing/rank.ipynb):

### Extração de características
Usamos um modelo VGG16 pré-treinado para extrair características de alto nível de cada frame, resultando em um vetor de características $f_i$ para cada imagem $i$.

### Redução de dimensionalidade
Aplicamos PCA para reduzir o espaço de características, mantendo 95% da variância. O número de componentes principais $k$ foi determinado pela equação:

$$\sum_{i=1}^k \lambda_i \geq 0.95 \sum_{i=1}^n \lambda_i$$

onde $\lambda_i$ são os autovalores da matriz de covariância ordenados de forma decrescente.

### Agrupamento
Utilizamos o algoritmo K-Means para agrupar imagens similares em 6 clusters, minimizando a soma dos quadrados das distâncias:

$$\arg\min_S \sum_{i=1}^k \sum_{x \in S_i} \|x - \mu_i\|^2$$

onde $S = \{S_1, S_2, ..., S_k\}$ são os k clusters e $\mu_i$ é o centroide do cluster $S_i$.

### Pontuação de diversidade
Desenvolvemos um método personalizado para pontuar a diversidade de cada imagem, baseado na sua distância média aos centroides dos clusters:

$$D(x_i) = \frac{1}{k} \sum_{j=1}^k \sqrt{\sum_{l=1}^m (x_{il} - c_{jl})^2}$$

onde $x_i$ é o vetor de características da imagem $i$, $c_j$ é o centroide do cluster $j$, $k$ é o número de clusters, e $m$ é o número de dimensões após a redução por PCA.

### Seleção final
Escolhemos as 5000 imagens com as maiores pontuações de diversidade, ordenadas de forma decrescente:

$$\text{Imagens Selecionadas} = \{x_i | D(x_i) \geq D(x_{5000})\}$$

Esta abordagem nos permitiu selecionar frames não sequenciais e garantir uma ampla variedade de ângulos, iluminações e características dos olhos bovinos.

## 5. Sistema de Rotulagem Personalizado

Desenvolvemos uma aplicação web interativa utilizando Flask (Python) e JavaScript para facilitar o processo de rotulagem manual. Este sistema permite:

1. Upload e visualização de vídeos
2. Extração de frames em intervalos específicos
3. Recorte (cropping) interativo das regiões de interesse
4. Segmentação manual das áreas relevantes (olhos dos bovinos)
5. Aplicação de máscaras para isolamento das características desejadas

O sistema gera dois conjuntos de imagens:
- Imagens "x": Recortes originais das regiões de interesse
- Imagens "y": Máscaras correspondentes, onde as áreas dos olhos são destacadas

#### Tecnologias Utilizadas:
- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript (com jQuery UI)
- Processamento de Imagem: OpenCV, PIL

## 6. Integração com CVAT (Computer Vision Annotation Tool)

Além disso, utilizamos o CVAT para uma anotação mais estruturada. Após a anotação, desenvolvemos um script Python para processar o arquivo annotations.xml:

Parsing do XML de anotações
Extração e processamento das coordenadas das caixas delimitadoras
Aplicação de máscaras baseadas nas anotações
Geração de imagens recortadas e mascaradas
O script processa três tipos de anotações:

'area': Região geral de interesse
'cabeca': Área da cabeça do bovino
'olho': Localização precisa dos olhos
O resultado final inclui pares de imagens "x" (recortes originais) e "y" (máscaras) com resolução de 128x128 pixels.