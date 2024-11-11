import os
import cv2
import xml.etree.ElementTree as ET

folder_path = 'Nome_da_Pasta' # Nome da Pasta com as imagens
annotation = 'annotations.xml' # Modifique o nome do xml, caso necessário
output = 'recortadas_x'

os.makedirs(output, exist_ok=True)

def process_annotations(folder_path, annotation, output):
    tree = ET.parse(annotation)
    root = tree.getroot()

    arquivos_gerados = []

    for image in root.findall('image'):
        image_name = image.get('name')
        width = int(image.get('width'))
        height = int(image.get('height'))
        
        image_path = os.path.join(folder_path, image_name)
        
        image_file = cv2.imread(image_path)
        
        if image_file is None:
            print(f"Erro ao carregar a imagem: {image_path}")
            continue

        # Procura pela caixa com o label "cabeca"
        for box in image.findall('box'):
            label = box.get('label')
            if label == "cabeca":
                xtl = int(float(box.get('xtl')))
                ytl = int(float(box.get('ytl')))
                xbr = int(float(box.get('xbr')))
                ybr = int(float(box.get('ybr')))

                xtl_adj = max(0, xtl - 100)
                ytl_adj = max(0, ytl - 100)
                xbr_adj = min(width, xbr + 100)
                ybr_adj = min(height, ybr + 100)

                if xtl_adj >= xbr_adj or ytl_adj >= ybr_adj:
                    xtl_adj = xtl
                    ytl_adj = ytl
                    xbr_adj = xbr
                    ybr_adj = ybr

                imagem_reduzida = image_file[ytl_adj:ybr_adj, xtl_adj:xbr_adj]
                
                # Ajustar o contraste e o brilho
                alpha = 1  # Contraste
                beta = 15    # Brilho
                imagem_ajustada = cv2.convertScaleAbs(imagem_reduzida, alpha=alpha, beta=beta)

                imagem_output_base = os.path.join(output, f"{os.path.splitext(image_name)[0]}_x.png")

                imagem_output = imagem_output_base

                imagem_redimensionada = cv2.resize(imagem_ajustada, (128, 128))

                i = 1
                while imagem_output in arquivos_gerados:
                    imagem_output = os.path.join(output, f"{os.path.splitext(image_name)[0]}_{i}_x.png")
                    i += 1
                
                cv2.imwrite(imagem_output, imagem_redimensionada)
                print(f"{image_name} em {imagem_output}")

                arquivos_gerados.append(imagem_output)

process_annotations(folder_path, annotation, output)
