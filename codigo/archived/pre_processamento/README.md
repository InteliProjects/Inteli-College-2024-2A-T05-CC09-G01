# Pré-processamento de Imagens

Este subdiretório contém os scripts e informações relacionadas ao pré-processamento das imagens utilizadas no projeto de segmentação de imagens de bovinos.

## Visão Geral

O processo de pré-processamento é crucial para preparar as imagens de todos os grupos, tanto as imagens originais dos bovinos (X) quanto as suas respectivas segmentações (Y). O objetivo principal é padronizar e otimizar os dados para as etapas subsequentes do projeto.

## Etapas do Pré-processamento

1. **Extração de Imagens**: 
   - Utilizamos o script `/extrair_imagens_grupos` para adaptar as nomenclaturas das imagens de cada grupo.
   - As imagens extraídas são salvas em um arquivo `.h5` para facilitar e acelerar a manipulação dos dados em iterações futuras.

2. **Otimização do Código**:
   - Realizamos ajustes adicionais no código para melhor se adequar às restrições de nomenclatura de imagens de cada grupo no drive.

3. **Processamento de Imagens**:
   - Aplicamos técnicas de data augmentation para enriquecer nosso conjunto de dados. Isso inclui:
     - [Liste aqui as técnicas específicas de data augmentation utilizadas]
   - Padronizamos as imagens para 3 canais de cor, visando melhorar o desempenho do modelo e reduzir o espaço amostral.

4. **Armazenamento Final**:
   - Todos os dados processados são salvos em um arquivo `.h5` para fácil acesso e manipulação nas etapas subsequentes do projeto.

## Estrutura do Diretório

- `extrair_imagens_grupos/`: Contém o script para extração e padronização inicial das imagens.
- `otimizacao_preprocessamento/`: Scripts atualizados com otimizações adicionais.
- `data_augmentation/`: Códigos relacionados às técnicas de aumento de dados aplicadas.
- `dados_processados.h5`: Arquivo final contendo todas as imagens pré-processadas.

## Uso

Para utilizar os scripts de pré-processamento:

1. Execute primeiro o script em `extrair_imagens_grupos/`
2. Em seguida, utilize os scripts em `otimizacao_preprocessamento/`
3. Por fim, aplique as técnicas de data augmentation com os scripts em `data_augmentation/`

O resultado final será o arquivo `dados_processados.h5` contendo todas as imagens prontas para uso nos modelos de segmentação.

## Notas Adicionais

- Certifique-se de ter todas as dependências necessárias instaladas antes de executar os scripts.
- O processo pode ser computacionalmente intensivo, dependendo do tamanho do conjunto de dados.
- Recomenda-se o uso de GPUs para acelerar o processamento, especialmente nas etapas de data augmentation.