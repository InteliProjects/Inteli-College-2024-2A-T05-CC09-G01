import os
import cv2
import xml.etree.ElementTree as ET
import numpy as np

image_folder = 'frames' # Path das Imagens
annotation_file = 'annotations.xml'
output_folder = 'recortadas_y' # Output

os.makedirs(output_folder, exist_ok=True)

def process_annotations_with_square(image_folder, annotation_file, output_folder):
    tree = ET.parse(annotation_file)
    root = tree.getroot()
    processed_frames = {}

    for track in root.findall('track'):
        label = track.get('label')

        # Processar apenas o primeiro box de cada track
        first_box = track.find('box')
        if first_box is not None:
            frame = first_box.get('frame')
            
            xtl = int(float(first_box.get('xtl')))
            ytl = int(float(first_box.get('ytl')))
            xbr = int(float(first_box.get('xbr')))
            ybr = int(float(first_box.get('ybr')))

            # Construir o nome da imagem com base no número do frame
            image_file = f"frame_{frame.zfill(6)}.png"
            image_path = os.path.join(image_folder, image_file)
            
            # Pinta a imagem de preto
            if frame not in processed_frames:
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Erro ao carregar a imagem: {image_path}")
                    continue
                height, width, _ = image.shape
                processed_frames[frame] = np.zeros((height, width, 3), dtype=np.uint8)  # Imagem preta

            # Desenho do quadrado branco(cabeça) e quadrados vermelhos(Olhos)
            if label == "cabeca":
                # Desenhe o quadrado branco sobre a área da cabeça
                cv2.rectangle(processed_frames[frame], (xtl, ytl), (xbr, ybr), (255, 255, 255), -1)
            elif label == "olho":
                # Desenhe o quadrado vermelho sobre a área do olho
                cv2.rectangle(processed_frames[frame], (xtl, ytl), (xbr, ybr), (0, 0, 255), -1)

    arquivos_gerados = set()

    for frame, imagem_final in processed_frames.items():
        cabeca_label = root.find(f".//track[@label='cabeca']/box[@frame='{frame}']")
        if cabeca_label is not None:
            xtl_cabeca = int(float(cabeca_label.get('xtl')))
            ytl_cabeca = int(float(cabeca_label.get('ytl')))
            xbr_cabeca = int(float(cabeca_label.get('xbr')))
            ybr_cabeca = int(float(cabeca_label.get('ybr')))
            
            # Adicionar as margens necessárias
            xtl_cabeca_adj = max(0, xtl_cabeca - 50)
            ytl_cabeca_adj = max(0, ytl_cabeca - 50)
            xbr_cabeca_adj = min(imagem_final.shape[1], xbr_cabeca + 100)
            ybr_cabeca_adj = min(imagem_final.shape[0], ybr_cabeca + 100)

            # Se as coordenadas ajustadas ultrapassarem os limites da imagem, use as coordenadas originais
            if (xtl_cabeca_adj >= xbr_cabeca_adj) or (ytl_cabeca_adj >= ybr_cabeca_adj):
                xtl_cabeca_adj = xtl_cabeca
                ytl_cabeca_adj = ytl_cabeca
                xbr_cabeca_adj = xbr_cabeca
                ybr_cabeca_adj = ybr_cabeca
            
            # Imagem Recortada
            imagem_cortada = imagem_final[ytl_cabeca_adj:ybr_cabeca_adj, xtl_cabeca_adj:xbr_cabeca_adj]

            # Redimensionamento 128x128
            imagem_redimensionada = cv2.resize(imagem_cortada, (128, 128))

            imagem_output_base = os.path.join(output_folder, f"01-08-2024_video_00000000205000400_{frame.zfill(6)}_1_x.png") # Modifique a data e o nome do vídeo, conforme necessário
            imagem_output = imagem_output_base
            i = 1
            while imagem_output in arquivos_gerados:
                imagem_output = os.path.join(output_folder, f"01-08-2024_video_00000000205000400_{frame.zfill(6)}_{i}_1_x.png") # Modifique a data e o nome do vídeo, conforme necessário
                i += 1
            
            # Salvando a imagem
            cv2.imwrite(imagem_output, imagem_redimensionada)
            print(f"Processed frame {frame} and saved to {imagem_output}")
            arquivos_gerados.add(imagem_output)

process_annotations_with_square(image_folder, annotation_file, output_folder)
