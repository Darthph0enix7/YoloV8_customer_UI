import PySimpleGUI as sg
from ultralytics import YOLO
from layouts import first_page_layout
import subprocess
import os
import yaml
from google_drive_downloader import GoogleDriveDownloader as gdd
import shutil
from PIL import Image
import random



def load_yaml(file_path):
    with open(file_path, 'r') as read_file:
        return yaml.safe_load(read_file)

def save_yaml(data, file_path):
    with open(file_path, 'w') as dump_file:
        yaml.dump(data, dump_file)

def ensure_paths_exist(paths_dict):
    for path in paths_dict.values():
        if not os.path.exists(path):
            os.mkdir(path)

def convert_jpg_to_png(image_path):
    if image_path.lower().endswith('.jpg'):
        im = Image.open(image_path)
        png_path = image_path.rsplit('.', 1)[0] + '.png'
        im.save(png_path, 'PNG')
        os.remove(image_path)  # Remove the original jpg file
        return png_path
    return image_path

def apply_yolo_on_image(image_path):
    model = YOLO(model_path)
    results = model(source=image_path, save=True, project=result_dir, exist_ok=True)
    return os.path.join(result_dir, 'predict', os.path.basename(image_path))

def next_or_prev_file(curr_file_path, direction="next"):
    folder, current_file = os.path.split(curr_file_path)
    valid_extensions = ['.png', '.gif', '.jpg']
    file_list = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and any(f.lower().endswith(ext) for ext in valid_extensions)]
    index = file_list.index(current_file)
    new_index = (index + 1) if direction == "next" else (index - 1)
    new_index = max(0, min(new_index, len(file_list)-1))
    return os.path.join(folder, file_list[new_index])

def result_exists(original_file_path):
    """Check if the result for the given image exists."""
    image_name = os.path.basename(original_file_path)
    result_path = os.path.join(result_dir, 'predict', image_name)
    return os.path.exists(result_path)

def distribute_images(raw_images_path, train_images_path, val_images_path):
    # List all images in raw_images_path
    all_images = [f for f in os.listdir(raw_images_path) if os.path.isfile(os.path.join(raw_images_path, f)) and f.lower().endswith(('.png', '.jpg', '.gif'))]
    
    # Shuffle the list to ensure random distribution
    random.shuffle(all_images)
    
    # Calculate number of images for training
    num_train = int(0.7 * len(all_images))
    
    # Move the images to their respective directories
    for idx, image in enumerate(all_images):
        source_path = os.path.join(raw_images_path, image)
        if idx < num_train:
            shutil.move(source_path, os.path.join(train_images_path, image))
        else:
            shutil.move(source_path, os.path.join(val_images_path, image))

def copy_file_to_directory(src_file_path, dest_dir):
    """
    Copies a file to a specified directory.

    Parameters:
    - src_file_path: Path to the source file.
    - dest_dir: Path to the destination directory.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)  # Create the destination directory if it doesn't exist
    shutil.copy(src_file_path, dest_dir)

# Load Configuration
config = load_yaml('config.yaml')
data = load_yaml('data.yaml')
# Step 1: Extract the file ID from the Google Drive link
file_id = "1ArTd0tbsx5GCYzLz0yLT_HOWwjukwPuc"

# Step 2: Define the destination path including the pre-trained_model folder
destination_path = os.path.join(os.getcwd(), 'pre-trained_model', 'yolov8n.pt')

# Step 3: Download the file from Google Drive directly into the pre-trained_model folder
gdd.download_file_from_google_drive(file_id=file_id, dest_path=destination_path, unzip=False)

# Step 4: Define the model path in the code
model_path = destination_path
data['model_path'] = model_path
save_yaml(data, 'data.yaml')

# Paths
PROJECT_PATHS = {
    'PROJECT_PATH': os.path.join(os.getcwd(), config['Project_Name']),
    'MODEL_PATH': os.path.join(os.getcwd(), config['Project_Name'], 'pre-trained_model'),
    'LOGO_PATH': os.path.join(os.getcwd(), config['Project_Name'], 'logo'),
    'RESULTS_PATH': os.path.join(os.getcwd(), config['Project_Name'], 'results'),
    'LABELING_PATH': os.path.join(os.getcwd(), config['Project_Name'], 'labeling'),
    'DATA_PATH': os.path.join(os.getcwd(), 'data'),
    'TRAIN_PATH': os.path.join(os.getcwd(), 'data', 'train'),
    'RAW_IMAGES_PATH' : os.path.join(os.getcwd(), 'data', 'raw_images'),
    'VAL_PATH': os.path.join(os.getcwd(), 'data', 'val'),
    'TRAIN_IMG_PATH': os.path.join(os.getcwd(), 'data', 'train', 'images'),
    'TLABELS_PATH': os.path.join(os.getcwd(), 'data', 'train', 'labels'),
    'VAL_IMG_PATH': os.path.join(os.getcwd(), 'data', 'val', 'images'),
    'VLABELS_PATH': os.path.join(os.getcwd(), 'data', 'val', 'labels')
}
with open('config.yaml','r') as read_file:
    contents = yaml.safe_load(read_file)
    Model_typ = contents['Model_typ']
# Ensure Path Exists
# Check Model_typ and download the GitHub project if necessary
if  Model_typ.lower() in ['detection', 'segmentation']:
    project_directory = os.path.join(os.getcwd(), config['Project_Name'], 'labeling')
    
    

    
elif config['Model_typ'] == 'Classification':
    ensure_paths_exist({k: v for k, v in PROJECT_PATHS.items() if 'IMG_PATH' not in k and 'LABELS_PATH' not in k})

if not os.path.exists(config['Logo_Link']):
    gdd.download_file_from_google_drive(file_id=config['Logo_Link'], dest_path=PROJECT_PATHS['LOGO_PATH'])

result_dir = PROJECT_PATHS['RESULTS_PATH']
layout = first_page_layout()
window = sg.Window(config['Company_Name'], layout, resizable=True)

# Event Loop
while True:
    try:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            if config['Model_typ'] == 'Classification':
                raw_images_path = os.path.join(os.getcwd(), 'data', 'raw_images')
                train_images_path = os.path.join(os.getcwd(), 'data', 'train')
                val_images_path = os.path.join(os.getcwd(), 'data', 'val')
                distribute_images(raw_images_path, train_images_path, val_images_path)
                break
            else:
                raw_images_path = os.path.join(os.getcwd(), 'data', 'raw_images')
                train_images_path = os.path.join(os.getcwd(), 'data', 'train', 'images')
                val_images_path = os.path.join(os.getcwd(), 'data', 'val', 'images')
                distribute_images(raw_images_path, train_images_path, val_images_path)
                break
        if event == 'label':
            LABELIMG_PATH = os.path.join(project_directory, 'labeling')
            compile_command = f"cd {LABELIMG_PATH} && pyrcc5 -o libs/resources.py resources.qrc"
            subprocess.run(compile_command, shell=True)

        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            file_list = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", ".gif"))]
            window["-FILE LIST-"].update(file_list)

        elif event == "-FILE LIST-":
            file_path = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
            file_path = convert_jpg_to_png(file_path)
            result_image_path = apply_yolo_on_image(file_path)
            window["-TOUT-"].update(result_image_path)
            window["-IMAGE-"].update(filename=result_image_path)

        elif event == 'upload':
            raw_images_path = os.path.join(PROJECT_PATHS['RAW_IMAGES_PATH'], os.path.basename(file_path))
            if not os.path.exists(raw_images_path):
                shutil.copy(file_path, raw_images_path)

        
        elif event in ['next', 'Next_img', 'Prev']:
            file_path = next_or_prev_file(file_path, direction="next" if event in ['next', 'Next_img'] else "prev")
            original_file_path = file_path
            file_path = convert_jpg_to_png(file_path)
            
            if not result_exists(original_file_path):
                result_image_path = apply_yolo_on_image(file_path)
            else:
                image_name = os.path.basename(original_file_path)
                result_image_path = os.path.join(result_dir, 'predict', image_name)

            window["-TOUT-"].update(result_image_path)
            window["-IMAGE-"].update(filename=result_image_path)

            file_list = window["-FILE LIST-"].get_list_values()
            current_index = file_list.index(os.path.basename(original_file_path))
            window["-FILE LIST-"].update(set_to_index=current_index)
    except:
        pass



window.close()