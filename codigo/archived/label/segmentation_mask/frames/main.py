import cv2
import os

def video_to_frames(video_path, output_folder, start_minute, end_minute):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS)) 
    start_frame = start_minute * 60 * fps 
    end_frame = end_minute * 60 * fps  

    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if start_frame <= frame_count <= end_frame:
            if frame_count % fps == 0:  
                frame_filename = os.path.join(output_folder, f'01-08-24_video1_00000000205000400_{frame_count:04d}.png')
                cv2.imwrite(frame_filename, frame)
                print(f"Frame {frame_count} salvo como {frame_filename}")
                saved_frame_count += 1

        frame_count += 1

    cap.release()
    print(f"Extração de frames concluída! {saved_frame_count} frames (1 por segundo) foram salvos na pasta {output_folder} do minuto {start_minute} até {end_minute}")


video_path = './00000000205000400.mp4'
output_folder = './output'
start_minute = 20
end_minute = 40

video_to_frames(video_path, output_folder, start_minute, end_minute)
