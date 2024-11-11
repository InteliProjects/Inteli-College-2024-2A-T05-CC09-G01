import os
import cv2
import xml.etree.ElementTree as ET
import numpy as np

image_folder = 'Nome_da_pasta' # Pasta com as imagens
annotation_file = 'annotations.xml' # Modifique o nome do xml, caso necessário
output_folder = 'recortadas_y'

os.makedirs(output_folder, exist_ok=True)

def process_annotations_with_square(image_folder, annotation_file, output_folder):
    tree = ET.parse(annotation_file)
    root = tree.getroot()
    processed_frames = {}

    for image in root.findall('image'):
        image_name = image.get('name')
        image_path = os.path.join(image_folder, image_name)

        image_file = cv2.imread(image_path)
        if image_file is None:
            print(f"Erro ao carregar a imagem: {image_path}")
            continue

        height, width, _ = image_file.shape
        processed_frames[image_name] = np.zeros((height, width, 3), dtype=np.uint8)  

        for box in image.findall('box'):
            label = box.get('label')
            xtl = int(float(box.get('xtl')))
            ytl = int(float(box.get('ytl')))
            xbr = int(float(box.get('xbr')))
            ybr = int(float(box.get('ybr')))

            if label == "cabeca":
                # Branco
                cv2.rectangle(processed_frames[image_name], (xtl, ytl), (xbr, ybr), (255, 255, 255), -1)
            elif label == "olho":
                # Vermelho
                cv2.rectangle(processed_frames[image_name], (xtl, ytl), (xbr, ybr), (0, 0, 255), -1)

    arquivos_gerados = set()

    for image_name, imagem_final in processed_frames.items():
        cabeca_label = root.find(f".//image[@name='{image_name}']/box[@label='cabeca']")
        if cabeca_label is not None:
            xtl_cabeca = int(float(cabeca_label.get('xtl')))
            ytl_cabeca = int(float(cabeca_label.get('ytl')))
            xbr_cabeca = int(float(cabeca_label.get('xbr')))
            ybr_cabeca = int(float(cabeca_label.get('ybr')))

            xtl_cabeca_adj = max(0, xtl_cabeca - 100)
            ytl_cabeca_adj = max(0, ytl_cabeca - 100)
            xbr_cabeca_adj = min(imagem_final.shape[1], xbr_cabeca + 100)
            ybr_cabeca_adj = min(imagem_final.shape[0], ybr_cabeca + 100)

            if (xtl_cabeca_adj >= xbr_cabeca_adj) or (ytl_cabeca_adj >= ybr_cabeca_adj):
                xtl_cabeca_adj = xtl_cabeca
                ytl_cabeca_adj = ytl_cabeca
                xbr_cabeca_adj = xbr_cabeca
                ybr_cabeca_adj = ybr_cabeca

            imagem_cortada = imagem_final[ytl_cabeca_adj:ybr_cabeca_adj, xtl_cabeca_adj:xbr_cabeca_adj]

            imagem_redimensionada = cv2.resize(imagem_cortada, (128, 128))

            imagem_output_base = os.path.join(output_folder, f"{os.path.splitext(image_name)[0]}_y.png")
            imagem_output = imagem_output_base
            i = 1
            while imagem_output in arquivos_gerados:
                imagem_output = os.path.join(output_folder, f"{os.path.splitext(image_name)[0]}_{i}_y.png")
                i += 1

            cv2.imwrite(imagem_output, imagem_redimensionada)
            print(f"{image_name} em {imagem_output}")
            arquivos_gerados.add(imagem_output)

process_annotations_with_square(image_folder, annotation_file, output_folder)
