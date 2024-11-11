# Exemplo

import cv2
import numpy as np
from keras.models import load_model

# Função para aplicar o sliding window
def sliding_window(image, step_size, window_size):
    # Itera pelas janelas da imagem
    for y in range(0, image.shape[0] - window_size[1], step_size):
        for x in range(0, image.shape[1] - window_size[0], step_size):
            # Extraindo a janela atual
            yield (x, y, image[y:y + window_size[1], x:x + window_size[0]])

# Função para reconstruir a imagem com as detecções
def draw_boxes(image, boxes):
    for (x, y, w, h) in boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return image

# Carregar o modelo de object detection previamente treinado
model = load_model('meu_modelo.h5')

# Parâmetros
window_size = (100, 100)  # Tamanho da janela
stride = 50  # Stride ou deslocamento da janela
image = cv2.imread('frame_boi.jpg')  # Carregar imagem

detected_boxes = []  # Lista para armazenar as detecções

# Aplicar sliding window na imagem
for (x, y, window) in sliding_window(image, stride, window_size):
    # Preprocessar a janela para o modelo
    window_resized = cv2.resize(window, (300, 300))  # Redimensionar para o tamanho que o modelo espera
    window_normalized = window_resized / 255.0  # Normalizar a imagem
    window_reshaped = np.expand_dims(window_normalized, axis=0)  # Adicionar dimensão para batch

    # Fazer a predição
    prediction = model.predict(window_reshaped)

    # Se o modelo detectar um objeto (ajuste o threshold conforme necessário)
    if prediction[0][0] > 0.5:  # Supondo que o modelo retorne uma probabilidade
        detected_boxes.append((x, y, window_size[0], window_size[1]))

# Desenhar as caixas detectadas na imagem original
output_image = draw_boxes(image, detected_boxes)

# Salvar ou exibir a imagem de saída com as detecções
cv2.imwrite('output_image.jpg', output_image)
cv2.imshow("Detections", output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
