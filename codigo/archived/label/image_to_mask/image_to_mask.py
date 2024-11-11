from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
import numpy as np
import os

# Função para converter string de pontos em uma lista de tuplas
def parse_points(points_str):
    points = []
    for point in points_str.split(';'):
        x, y = map(float, point.split(','))
        points.append((x, y))
    return points

# Função para criar uma máscara a partir dos pontos
def create_mask(image_size, points):
    mask = Image.new('L', image_size, 0)  # Fundo preto
    ImageDraw.Draw(mask).polygon(points, outline=1, fill=1)  # Polígono branco
    return np.array(mask)

# Função para processar uma única imagem e salvar as máscaras
def process_image(image_path, xml_path):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image_dir = os.path.dirname(image_path)
    
    # Carregar o XML a partir do arquivo
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Carregar a imagem
    image = Image.open(image_path)
    
    # Iterar sobre as polilinhas e criar as máscaras
    for i, polyline in enumerate(root.iter('polyline')):
        label = polyline.attrib['label']
        points = parse_points(polyline.attrib['points'])
        mask = create_mask(image.size, points)
        
        # Inverter as cores da máscara para que a área externa fique preta e a interna branca
        final_mask = Image.fromarray(np.where(mask == 1, 255, 0).astype(np.uint8))  # Branco dentro do polígono e preto fora
        
        # Criar uma imagem preta de fundo
        final_image = Image.new('RGB', image.size, (0, 0, 0))  # Fundo preto
        
        # Colar a máscara branca na imagem preta
        final_image.paste((255, 255, 255), mask=final_mask)
        
        # Salvar a imagem mascarada com o nome apropriado na mesma pasta da imagem original
        final_image.save(os.path.join(image_dir, f"{image_name}_y{i+1}.png"))

# Função para processar todas as imagens em uma pasta
def process_images_in_folder(image_folder, xml_path):
    for image_file in os.listdir(image_folder):
        if image_file.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_file)
            process_image(image_path, xml_path)

# Definir os diretórios de entrada
image_folder = "./images"  # Pasta contendo as imagens
xml_path = "./annotations/annotations_example.xml"  # Caminho para o único arquivo XML de anotação

# Processar todas as imagens na pasta
process_images_in_folder(image_folder, xml_path)
