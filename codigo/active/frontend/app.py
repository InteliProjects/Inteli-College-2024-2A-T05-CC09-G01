import base64
import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import pandas as pd
import tensorflow as tf
import os
from collections import defaultdict

temperature_model = tf.keras.models.load_model('temperature_model.h5')

def preprocess_digit(digit):
    digit_resized = cv2.resize(digit, (16, 21))
    digit_normalized = digit_resized.astype('float32') / 255.0
    digit_ready = np.expand_dims(np.expand_dims(digit_normalized, axis=0), axis=-1)
    return digit_ready

def recognize_digit(digit):
    preprocessed_digit = preprocess_digit(digit)
    prediction = temperature_model.predict(preprocessed_digit, verbose=0)
    predicted_class = np.argmax(prediction)
    class_mapping = {
        0: '0', 1: '1', 2: '2', 3: '3', 4: '4',
        5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10: 'minus', 11: 'nothing'
    }
    return class_mapping.get(predicted_class, 'unknown')

def extract_temperature(image, x1, y1, x2, y2):
    roi = image[y1:y2, x1:x2]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    digit1 = gray_roi[:, :16]
    digit2 = gray_roi[:, 16:32]
    digit3 = gray_roi[:, 48:64]
    recognized_digit1 = recognize_digit(digit1)
    recognized_digit2 = recognize_digit(digit2)
    recognized_digit3 = recognize_digit(digit3)
    if recognized_digit1 == 'minus':
        recognized_number = f"-{recognized_digit2}.{recognized_digit3}"
    else:
        recognized_number = f"{recognized_digit1}{recognized_digit2}.{recognized_digit3}"
    try:
        return float(recognized_number)
    except ValueError:
        return None

def process_thermal_image(img, x1, y1, x2, y2):
    if img is None:
        return None
    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
    height, width = img.shape[:2]
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))
    temp_high = extract_temperature(img, 510, 67, 575, 88)
    temp_low = extract_temperature(img, 510, 403, 575, 424)
    if temp_high is None or temp_low is None:
        return None
    roi = img[y1:y2, x1:x2, 0].astype(np.float32)
    temp_range = temp_high - temp_low
    pixel_temps = temp_low + (roi / 255.0 * temp_range)
    sorted_temps = np.sort(pixel_temps.flatten())
    threshold_index = int(0.9 * sorted_temps.size)
    final_temp = np.mean(sorted_temps[threshold_index:])
    if final_temp == None:
        final_temp = 0.0
    return final_temp

def process_video(uploaded_file):
    output_dir = 'output_videos'
    os.makedirs(output_dir, exist_ok=True)
    CLASS_HEAD = 0
    CLASS_EYE = 1
    head_ids = set()
    eye_ids = set()
    eye_count = defaultdict(int)
    eye_temperatures = {}
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())
    tfile.flush()
    input_video_path = tfile.name
    video_filename = "processed_video.mp4"
    csv_filename = "temperature_data.csv"
    output_video_path = os.path.join(output_dir, video_filename)
    csv_output_path = os.path.join(output_dir, csv_filename)
    model_path = 'best2.pt'
    model = YOLO(model_path)
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Não foi possível abrir o vídeo: {input_video_path}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    data_records = []
    progress_bar = st.progress(0)
    results = model.track(source=input_video_path, conf=0.2, persist=True, save=False)
    total_frames = len(results)
    frame_count = 0
    for result in results:
        frame = result.orig_img
        boxes = result.boxes
        timestamp = frame_count / fps
        timestamp_formatted = f"{int(timestamp // 60):02}:{int(timestamp % 60):02}:{int((timestamp % 1) * 1000):03}"
        head_id = None
        for box in boxes:
            if box.id is None:
                continue
            bbox = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = bbox
            conf = box.conf[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            track_id = int(box.id[0].cpu().numpy())
            if cls == CLASS_HEAD:
                head_ids.add(track_id)
                head_id = track_id
                color = (0, 255, 255)
                label = f'Cabeca ID {track_id}'
            elif cls == CLASS_EYE:
                eye_count[track_id] += 1
                if track_id not in eye_temperatures or eye_count[track_id] >= 10:
                    eye_temp = process_thermal_image(frame, x1, y1, x2, y2)
                    if track_id not in eye_temperatures or eye_temperatures[track_id] != eye_temp:
                        eye_temperatures[track_id] = eye_temp
                        data_records.append([head_id, track_id, eye_temp, timestamp_formatted])
                    eye_count[track_id] = 0
                else:
                    eye_temp = eye_temperatures[track_id]
                eye_ids.add(track_id)
                color = (255, 0, 255)
                if eye_temp is not None:
                    label = f'Olho ID {track_id}, {eye_temp:.2f}'
                else:
                    label = f'Olho ID {track_id}, temperatura não disponível'
            else:
                color = (0, 255, 0)
                label = f'ID {track_id}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        out.write(frame)
        frame_count += 1
        progress_bar.progress(frame_count / total_frames)
    df = pd.DataFrame(data_records, columns=["ID Cabeça", "ID Olho", "Temperatura", "Timestamp(min:seg:miliseg)"])
    df.to_csv(csv_output_path, index=False)
    out.release()
    cv2.destroyAllWindows()
    return output_video_path, csv_output_path

def process_video_with_yolo(uploaded_file):
    output_dir = 'output_videos'
    os.makedirs(output_dir, exist_ok=True)
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    input_video_path = tfile.name
    video_filename = "processed_video.avi"
    csv_filename = "temperature_data.csv"
    output_video_path = os.path.join(output_dir, video_filename)
    csv_output_path = os.path.join(output_dir, csv_filename)
    model_path = 'best2.pt'
    model = YOLO(model_path)
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
    CLASS_HEAD = 0
    CLASS_EYE = 1
    data_records = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress_bar = st.progress(0)
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        for box in results[0].boxes:
            bbox_array = box.xyxy.cpu().numpy().flatten()
            x1, y1, x2, y2 = bbox_array.astype(int)
            conf = box.conf.cpu().numpy()[0]
            cls = int(box.cls.cpu().numpy()[0])
            track_id = int(box.id[0].cpu().numpy()) if box.id is not None else None
            if conf > 0.2:
                if cls == CLASS_HEAD:
                    color = (0, 255, 255)
                    label = f'Cabeca: {conf:.2f}'
                elif cls == CLASS_EYE:
                    eye_temp = process_thermal_image(frame, x1, y1, x2, y2)
                    color = (255, 0, 255)
                    label = f'Olho: {conf:.2f}, Temp: {eye_temp:.2f}' if eye_temp is not None else f'Olho: {conf:.2f}'
                    data_records.append([track_id, eye_temp])
                else:
                    color = (0, 255, 0)
                    label = f'Classe {cls}: {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        out.write(frame)
        frame_count += 1
        progress_bar.progress(frame_count / total_frames)
    df = pd.DataFrame(data_records, columns=["Object ID", "Temperature"])
    df.to_csv(csv_output_path, index=False)
    cap.release()
    out.release()
    return output_video_path, csv_output_path

logo = './images/betterbeef.webp'

st.sidebar.image(logo)

pagina = st.sidebar.radio("Navegação", ["Introdução", "Como Funciona?", "Processamento"])

st.markdown("""
    <style>
    .fixed-bottom-right {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 100;
    }
    </style>
    <div class="fixed-bottom-right">
        <a href="https://github.com/Inteli-College/2024-2A-T05-CC09-G01" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" width="30"/>
        </a>
    </div>
    """, unsafe_allow_html=True)

if pagina == "Introdução":
    st.markdown("# Introdução")
    st.markdown('---')
    st.markdown("## Ferramenta Para Detecção de Temperatura de Bovinos.")
    st.markdown("""O manejo adequado da saúde animal é essencial para
 a produtividade e sustentabilidade na pecuária moderna. A detecção precoce de doenças em bovinos, em particular, desempenha um papel crucial na melhoria
 do bem-estar animal e na eficiência operacional. Tradicionalmente, o monitoramento da saúde dos animais é
 realizado por meio de medições manuais, um método
 comum, mas que apresenta limitações significativas
 quando aplicado a grandes rebanhos.""")
    st.write("Com isso, optamos por uma abordagem mais moderna, utilizando Visão computacional para identificar a região do olhos e em seguida a temperatura dos bovinos.")
    st.write("Nossa ferramenta busca facilitar a Empresa Better Beef na identificação de bovinos doentes, por meio do calculo da temperatura interna através dos olhos. O propósito da ferramenta é que seja intuitiva, de fácil manejo e entendimento, permitindo que a Better Beef utilize-a diariamente para encontrar bovinos doentes com uma maior facilidade.")
    st.markdown('---')
    st.image('./images/vaca_azul.png', caption='Imagem ilustrativa', use_column_width=True)
    st.markdown('---')
    st.markdown("### Resultados")
    VIDEO_URL = "https://youtu.be/dmpB8QxTLdo"
    st.video(VIDEO_URL)
    st.markdown('---')
    st.markdown("### Membros")
    st.markdown("""
        <div style='display: flex; justify-content: space-around;'>
            <a href="https://www.linkedin.com/in/arthur-tsukamoto/" target="_blank">Arthur Tsukamoto</a>
            <a href="https://www.linkedin.com/in/bruno-wasserstein/" target="_blank">Bruno Wasserstein</a>
            <a href="https://www.linkedin.com/in/estherhikari/" target="_blank">Esther Hikari Kimura Nunes</a>
            <a href="https://www.linkedin.com/in/henrique-godoy-879138252/" target="_blank">Henrique Godoy</a>
            <a href="https://www.linkedin.com/in/fabio-piemonte-823a65211/" target="_blank">Fábio Piemonte</a>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("### Stakeholders")
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center;'>
            <a href="https://www.betterbeef.com.br/" target="_blank">
                <img src='data:image/png;base64,{}' alt='Better Beef' style='height: 80px; margin-right: 60px;'/>
            </a>
            <a href="https://www.betterbeef.com.br/" target="_blank">
                <img src='data:image/png;base64,{}' alt='Vista Alegre' style='height: 80px; margin-right: 60px;'/>
            </a>
            <a href="https://www.inteli.edu.br/" target="_blank">
                <img src='data:image/png;base64,{}' alt='Inteli' style='height: 80px; margin-right: 60px;'/>
            </a>
            <a href="https://www.linkedin.com/in/raphaelgarciamoreira/" target="_blank">
                <img src='data:image/png;base64,{}' alt='Raphael' style='height: 80px; margin-right: 60px;'/>
            </a>
        </div>
        """.format(
            base64.b64encode(open('./images/betterbeef.webp', 'rb').read()).decode('utf-8'),
            base64.b64encode(open('./images/vista_alegre.png', 'rb').read()).decode('utf-8'),
            base64.b64encode(open('./images/inteli.png', 'rb').read()).decode('utf-8'),
            base64.b64encode(open('./images/raphael.jpeg', 'rb').read()).decode('utf-8')
        ),
        unsafe_allow_html=True)

elif pagina == 'Como Funciona?':
        st.markdown("## COMO FUNCIONA?")
        st.markdown('---')
        st.markdown("#### Passo 1:")
        st.markdown("- Acesse a página de Processamento, que se encontra na Sidebar.")
        st.image('./images/pagina_processamento.png', caption='Processamento', use_column_width=True)
        st.markdown("#### Passo 2:")
        st.markdown("- Na página de Processamento, clique em 'Browser Files' e selecione um vídeo para ser processado.")
        st.image('./images/browser_files.png', caption='Seleção de Imagens', use_column_width=True)
        st.image('./images/escolha_do_video.png', caption='Escolha do Vídeo', use_column_width=True)
        st.markdown("#### Passo 3:")
        st.markdown("- Depois da Escolha, o vídeo será processado e retornado.")
        st.image('./images/processando.png', caption='Seleção de Imagens', use_column_width=True)
        st.markdown("- É possível visualizar o andamento do processamento por meio da barra de carregamento")
        st.image('./images/processamento_carregando.png', caption='Carregando Vídeo', use_column_width=True)
        st.markdown("- Com a barra completa, um display do vídeo será apresentado, além de uma tabela csv, a qual é possível baixar.")
        st.image('./images/video.png', caption='Vídeo', use_column_width=True)
        st.markdown('---')
else: 
    st.title("Processamento do Vídeo")
    st.markdown('---')
    uploaded_file = st.file_uploader("Carregue um vídeo", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_file is not None:
        if 'processed_video_bytes' not in st.session_state:
            st.write("Processando o vídeo, por favor aguarde...")
            output_video_path, csv_path = process_video(uploaded_file)
            st.session_state['csv_path'] = csv_path
            with open(output_video_path, 'rb') as video_file:
                    st.session_state['processed_video_bytes'] = video_file.read()
            st.write("Vídeo Processado:")
            st.video(st.session_state['processed_video_bytes'])
            st.download_button(
                label="Baixar Vídeo Processado",
                data=st.session_state['processed_video_bytes'],
                file_name="video_processado.mp4",
                mime="video/mp4"
            ) 
            st.write("Resultados de Temperatura:")
            with open(st.session_state['csv_path'], 'rb') as csv_file:
                st.download_button(
                    label="Baixar CSV de Temperaturas",
                    data=csv_file,
                    file_name="temperature_data.csv",
                    mime="text/csv"
                )