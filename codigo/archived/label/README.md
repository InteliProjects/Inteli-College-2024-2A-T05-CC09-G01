### 1. Label

Esta pasta contém códigos e ferramentas para otimizar o processo de labeling, que serão utilizados posteriormente no pré-processamento e nos modelos.

#### 1.1 divisao_frames

- **Objetivo**: Separar frames de vídeo com maior diversidade para melhorar a generalização dos modelos.
- **Tecnologias**: VGG16 + PCA + KMEANS
- **Funcionalidade**: Este algoritmo seleciona frames diversos de um vídeo, agregando mais valor para os modelos subsequentes ao garantir uma variedade de contextos.

#### 1.2 image_to_mask

- **Objetivo**: Criar máscaras a partir de anotações em XML.
- **Funcionalidade**: 
  - Converte anotações de polígonos em XML para máscaras de imagem.
  - Cria máscaras binárias onde a área dentro do polígono é branca e o exterior é preto.
  - Salva as máscaras como novas imagens.

#### 1.3 web_label_optimizer

- **Objetivo**: Fornecer uma interface web para facilitar o processo de labeling.
- **Funcionalidades**:
  - Upload de vídeos
  - Configuração de parâmetros (FPS, tamanho do frame)
  - Segmentação de imagens
  - Criação de máscaras
  - Recorte de regiões de interesse

**Como usar**:
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute a aplicação: `python app.py`
3. Acesse a interface web através do navegador

### 2. Processamento de Imagens e Vídeos

Esta seção explica como utilizar os códigos para fazer o processamento de imagens e vídeos usando a ferramenta CVAT (Computer Vision Annotation Tool).

#### 2.1 Preparação no CVAT

1. Crie um Project e adicione os labels necessários: "cabeca", "olho".
2. Crie uma Task e adicione as imagens ou vídeos.
3. Crie um Job para realizar as anotações.
4. Faça as anotações nas imagens ou vídeos.
5. Exporte o dataset do Job no formato adequado (CVAT for Images 1.1 ou CVAT for Video 1.1).

#### 2.2 Processamento de Imagens

1. Adicione as imagens e o arquivo XML exportado do CVAT na pasta `export_imagem`.
2. Execute os scripts:
```
python imagens_x.py
python imagens_y.py
```

3. As imagens recortadas serão geradas em novas pastas.

#### 2.3 Processamento de Vídeos

1. Adicione o vídeo e o arquivo XML exportado do CVAT na pasta `export_video`.
2. Execute os scripts:

```
python frame.py
python imagens_x.py
python imagens_y.py
```

3. Os frames do vídeo serão extraídos e as imagens recortadas serão geradas em novas pastas.

## Fluxo de Trabalho Sugerido

1. Use `divisao_frames` para selecionar frames representativos de seus vídeos.
2. Utilize a ferramenta `web_label_optimizer` para fazer anotações iniciais e criar máscaras.
3. Se necessário, use `image_to_mask` para converter anotações XML em máscaras de imagem.
4. Use o CVAT para fazer anotações detalhadas.
5. Execute os scripts em `processamento_imagem_e_video` para processar as imagens ou vídeos anotados.

## Observações Importantes

- Certifique-se de ajustar os caminhos (paths) nos scripts conforme necessário.
- As imagens processadas são redimensionadas para 128x128 pixels.
- Verifique as dependências necessárias em cada diretório e instale-as usando `pip install -r requirements.txt`.