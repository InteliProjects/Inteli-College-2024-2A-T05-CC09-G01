import cv2
import os

video_path = 'Nome_do_video'
output_folder = 'frames'

os.makedirs(output_folder, exist_ok=True)

def divide_video_into_frames(video_path, output_folder):
    video_capture = cv2.VideoCapture(video_path)
    
    # Verifica se o vídeo foi carregado corretamente
    if not video_capture.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}")
        return
    
    frame_count = 0
    
    while True:
        # Leitura do próximo frame
        ret, frame = video_capture.read()
        
        # Se acabar os frames, finaliza a leitura.
        if not ret:
            break
        
        # Nome das imagens geradas.
        frame_file = os.path.join(output_folder, f"frame_{frame_count:06d}.png")
        
        # Salvando os frames
        cv2.imwrite(frame_file, frame)
        print(f"Salvou {frame_file}")
        
        frame_count += 1
    
    # Finalizando o Vídeo
    video_capture.release()
    print(f"Processamento concluído. {frame_count} frames foram extraídos.")

divide_video_into_frames(video_path, output_folder)
