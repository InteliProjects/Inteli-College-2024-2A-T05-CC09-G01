# Demonstração do Vídeo Processado

<div align="center">
  <a href="https://www.youtube.com/watch?v=IxmxRGC3t1M">
    <img src="https://img.youtube.com/vi/IxmxRGC3t1M/0.jpg" width="560" height="315">
  </a>
</div>

# Explicação da Pipeline

Este arquivo `.ipynb` contém um script Python executado no Google Colab, onde diversas operações, como treinamento de modelo, reconhecimento de dígitos e processamento de imagens térmicas, são realizadas usando bibliotecas como YOLO, TensorFlow, OpenCV e SORT. Abaixo está a explicação detalhada de cada etapa do código:

## 1. Montando o Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```
Este código monta o Google Drive no ambiente do Colab, permitindo que o script acesse arquivos armazenados lá.

## 2. Instalando YOLO e SORT
```python
!pip install ultralytics
!pip install simple-online-realtime-tracking
```
YOLOv8 é utilizado para detecção de objetos, e SORT é um rastreador que realiza rastreamento em tempo real. Essas bibliotecas são instaladas para permitir a detecção e o rastreamento de objetos no vídeo.

## 3. Baixando o Conjunto de Dados do Roboflow
```python
!curl -L "https://app.roboflow.com/ds/VqxrxMpvQL?key=KL0dyge979" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip
```
Este comando baixa um conjunto de dados do Roboflow, descompacta o arquivo e, em seguida, remove o arquivo zip.

## 4. Treinando o Modelo YOLO
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')

model.train(
    data='/content/data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    workers=4
)
```
O modelo YOLOv8 é carregado e treinado em um conjunto de dados definido no arquivo data.yaml. O treinamento ocorre por 50 épocas com um tamanho de imagem de 640 e um batch size de 16.

## 5. Validação do Modelo
```python
metrics = model.val()
```
Após o treinamento, o modelo é validado para avaliar seu desempenho.

## 6. Reconhecimento de Dígitos com CNN
```python
temperature_model = tf.keras.models.load_model('/content/drive/MyDrive/temperature_digits/temperature_model.h5')
```
Um modelo CNN pré-treinado é carregado para reconhecer dígitos em leituras de temperatura. O script define funções para pré-processar imagens e prever os dígitos.

## 7. Pré-processamento e Reconhecimento de Dígitos
```python
def preprocess_digit(digit):
    ...
def recognize_digit(digit):
    ...
```
Essas funções realizam o pré-processamento de uma imagem de dígito e a passam pelo modelo CNN para reconhecer o dígito. Os dígitos representam valores de temperatura nas imagens.

## 8. Cálculo da Perda Huber para Estimativa Robusta de Temperatura
```python
def huber_loss(residual, delta=1.0):
    ...
def robust_temperature_mean(temperatures, delta=1.0):
    ...
```
A perda Huber é utilizada para calcular uma estimativa robusta da temperatura, minimizando o impacto de outliers.

## 9. Extração e Processamento de Dados de Temperatura
```python
def extract_temperature(image, x1, y1, x2, y2):
    ...
def process_thermal_image(image_path, x1, y1, x2, y2):
    ...
```
Essas funções extraem valores de temperatura de regiões específicas da imagem. A imagem é processada para reconhecer os dígitos e a temperatura final é calculada com base nos valores de pixels, usando a perda Huber.

## 10. Rastreamento de Objetos no Vídeo com YOLO e SORT
```python
from sort import Sort
from ultralytics import YOLO

# Carregar o modelo YOLO
model = YOLO(model_path)

# Inicializar o rastreador SORT
tracker = Sort()
```
Um modelo YOLO é usado para detectar objetos (cabeças e olhos), e o SORT é usado para rastrear esses objetos ao longo dos frames do vídeo. Dois rastreadores separados são inicializados para cabeças e olhos.

## 11. Processamento de Vídeo
```python
cap = cv2.VideoCapture(input_video_path)
out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
```
O script processa cada frame do vídeo, aplica o YOLOv8 para detecção e rastreia os objetos usando o SORT. Cabeças e olhos detectados são desenhados no frame com caixas delimitadoras, e o resultado é gravado em um novo arquivo de vídeo.

## 12. Detecção e Rastreamento de Objetos
```python
results = model(frame)
dets = np.array(detections)
tracked_heads = tracker_heads.update(dets_heads)
tracked_eyes = tracker_eyes.update(dets_eyes)
```
O YOLO detecta objetos em cada frame, e as coordenadas das caixas delimitadoras são rastreadas usando o algoritmo SORT. O rastreamento de cabeças e olhos é feito separadamente para manter IDs de rastreamento distintos.

## 13. Saída Final
```python
print(f'Total de cabeças detectadas: {total_cabecas}')
print(f'Total de olhos detectados: {total_olhos}')
```
Após processar todos os frames, o total de cabeças e olhos detectados e rastreados é impresso.

Este notebook demonstra múltiplas técnicas de visão computacional, incluindo detecção de objetos com YOLO, reconhecimento de dígitos com CNN, estimativa robusta de temperatura usando perda Huber e rastreamento de objetos com SORT.
