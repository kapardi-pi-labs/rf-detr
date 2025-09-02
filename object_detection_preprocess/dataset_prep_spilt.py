import os
import json
import shutil

# Set the directory where all the files and JSONs are located
base_dir = '/shared/kapardi/object_detection_data/bag6k'  # Change this!

# Map of JSON filename to destination folder
json_to_folder = {
    'instances_train.json': 'train',
    'instances_val.json': 'val',
    'instances_test.json': 'test'
}

for json_file, folder_name in json_to_folder.items():
    json_path = os.path.join("/shared/kapardi/object_detection_data/annotations", json_file)
    
    # Create the destination folder if it doesn't exist
    dest_folder = os.path.join(base_dir, folder_name)
    os.makedirs(dest_folder, exist_ok=True)
    
    # Load filenames from JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
        file_list = [img['file_name'] for img in data.get('images', [])]
    
    for filename in file_list:
        src = os.path.join(base_dir, filename)
        dst = os.path.join(dest_folder, filename)

        if os.path.exists(src):
            shutil.move(src, dst)
        else:
            print(f"[Warning] File not found: {src}")

