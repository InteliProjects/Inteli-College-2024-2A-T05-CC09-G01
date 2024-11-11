import os
import cv2
import xml.etree.ElementTree as ET

folder_path = 'frames'
annotation = 'annotations.xml'
output = 'recortadas_x'

os.makedirs(output, exist_ok=True)

def process_annotations(folder_path, annotation, output):
    tree = ET.parse(annotation)
    root = tree.getroot()

    arquivos_gerados = []

    for track in root.findall('track'):
        label = track.get('label')
        if label == "cabeca":
            first_box = track.find('box')
            if first_box is not None:
                frame = first_box.get('frame')
                xtl = int(float(first_box.get('xtl')))
                ytl = int(float(first_box.get('ytl')))
                xbr = int(float(first_box.get('xbr')))
                ybr = int(float(first_box.get('ybr')))

                image_file = f"frame_{frame.zfill(6)}.png"
                image_path = os.path.join(folder_path, image_file)
                
                image = cv2.imread(image_path)
                
                if image is None:
                    print(f"Erro ao carregar a imagem: {image_path}")
                    continue

                numero_frame = os.path.splitext(os.path.basename(image_path))[0].split('_')[1]
                if numero_frame != frame.zfill(6):
                    print(f"Frame number mismatch: {numero_frame} vs {frame.zfill(6)}")
                    continue

                height, width, _ = image.shape
                xtl_adj = max(0, xtl - 100)
                ytl_adj = max(0, ytl - 100)
                xbr_adj = min(width, xbr + 100)
                ybr_adj = min(height, ybr + 100)

                if xtl_adj >= xbr_adj or ytl_adj >= ybr_adj:
                    xtl_adj = xtl
                    ytl_adj = ytl
                    xbr_adj = xbr
                    ybr_adj = ybr

                imagem_reduzida = image[ytl_adj:ybr_adj, xtl_adj:xbr_adj]
                
                # Ajustar o contraste e o brilho
                alpha = 1.5 # contraste
                beta = 15    # Brilho
                imagem_ajustada = cv2.convertScaleAbs(imagem_reduzida, alpha=alpha, beta=beta)

                imagem_output_base = os.path.join(output, f"01-08-2024_video_00000000205000400_{frame.zfill(6)}_1_x.png") # Modifique a data e o nome do vídeo, conforme necessário

                imagem_output = imagem_output_base

                imagem_redimensionada = cv2.resize(imagem_ajustada, (128, 128))

                i = 1
                while imagem_output in arquivos_gerados:
                    imagem_output = os.path.join(output, f"01-08-2024_video_00000000205000400_{frame.zfill(6)}_{i}_1_x.png") # Modifique a data e o  nome do vídeo, conforme necessário
                    i += 1
                
                cv2.imwrite(imagem_output, imagem_redimensionada)
                print(f"Processed frame {frame} and saved to {imagem_output}")

                arquivos_gerados.append(imagem_output)

process_annotations(folder_path, annotation, output)
