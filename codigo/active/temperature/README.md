# Documentação Técnica para Processamento de Imagens Térmicas e Reconhecimento de Dígitos

## Introdução

Este projeto utiliza técnicas avançadas de processamento de imagem e aprendizado de máquina para processar imagens térmicas e reconhecer dígitos presentes em displays de temperatura. A aplicação processa imagens de uma sequência de vídeos térmicos e identifica os dígitos de temperatura exibidos em cada frame. O sistema é composto por módulos para o pré-processamento de imagens, detecção de contornos e reconhecimento de dígitos usando redes neurais convolucionais (CNNs) otimizadas.

## Metodologia

A metodologia pode ser dividida em três fases principais:

1. **Pré-processamento e Segmentação de Imagens**: As imagens térmicas são convertidas para escala de cinza, e a região de interesse (ROI) correspondente aos dígitos de temperatura é isolada.
2. **Reconhecimento de Dígitos**: Os dígitos são reconhecidos por meio de uma CNN otimizada.
3. **Estimativa de Temperatura**: A partir dos dígitos identificados, as temperaturas são extraídas e uma estimativa robusta de temperatura é calculada utilizando os 90% dos pixels com a maior temperatura.

## Estrutura do Código

### 1. Preparação dos Dados

Os dados são normalizados e divididos em conjuntos de treino e teste.

```python
X = X_train_augmented
y = y_train_augmented
X = X.astype('float32') / 255.0
```

### 2. Codificação dos Rótulos

Utiliza-se LabelEncoder para codificar os rótulos.

```
le = LabelEncoder()
y = le.fit_transform(y)
```

### 3. Modelo CNN Otimizado

A estrutura da CNN foi otimizada para melhor desempenho e eficiência.

```
model = models.Sequential([
    layers.Conv2D(2, (3, 3), activation='relu', padding='same', input_shape=(21, 16, 1),
                  kernel_regularizer=regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.MaxPooling2D((4, 4)),
    layers.Conv2D(4, (3, 3), activation='relu', padding='same',
                  kernel_regularizer=regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.GlobalAveragePooling2D(),
    layers.Dense(7, activation='relu', kernel_regularizer=regularizers.l2(0.001)),
    layers.Dense(len(le.classes_), activation='softmax')
])
```

### 4. Treinamento do Modelo

Utiliza-se EarlyStopping para prevenir overfitting.

```
early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = model.fit(X_train, y_train, epochs=300, validation_split=0.2, batch_size=32, callbacks=[early_stopping])
```

### 5. Treinamento do Modelo

A função recognize_digits foi otimizada para processar múltiplos dígitos de uma vez.

```
def recognize_digits(digits):
    digits_resized = np.array([cv2.resize(digit, (16, 21)) for digit in digits])
    digits_normalized = digits_resized.astype('float32') / 255.0
    digits_ready = np.expand_dims(digits_normalized, axis=-1)
    
    predictions = model.predict(digits_ready)
    predicted_classes = np.argmax(predictions, axis=1)
    
    return [CLASS_MAPPING[cls] for cls in predicted_classes]
```

### 6. Extração e Processamento de Temperatura

A função process_thermal_image extrai as temperaturas de referência e calcula a temperatura final robusta.

```
def process_thermal_image(image_path, x1, y1, x2, y2):
    img = cv2.imread(image_path)
    temp_high = extract_temperature(img, 510, 67, 575, 88)
    temp_low = extract_temperature(img, 510, 403, 575, 424)

    roi = img[y1:y2, x1:x2, 0].astype(np.float32)
    temp_range = temp_high - temp_low
    pixel_temps = temp_low + (roi / 255.0 * temp_range)

    sorted_temps = np.sort(pixel_temps.flatten())
    threshold_index = int(0.9 * sorted_temps.size)
    final_temp = np.mean(sorted_temps[threshold_index:])

    print(f"Final robust temperature: {final_temp:.2f}°C")
```

## Conclusão

Este projeto implementa um pipeline otimizado de reconhecimento de dígitos em imagens térmicas, utilizando uma CNN eficiente e técnicas de processamento de imagem para reconhecimento robusto de temperaturas. A abordagem é eficiente e precisa, permitindo o processamento rápido de imagens térmicas e a extração confiável de informações de temperatura.

