import os
import json
import shutil

# Paths - Change these!
json_dir = '/data/kapardi/soda_corpus'        # Folder with train.json, val.json, test.json
images_dir = '/data/kapardi/soda_corpus/soda-driving'          # Folder where all images are located
output_dir = '/data/kapardi/soda_corpus/soda_dm'   # Folder to create train/, val/, test/

# Map JSON filenames to their corresponding split
split_map = {
    'train': 'train copy.json',
    'val': 'val copy.json',
    'test': 'test copy.json'
}

for split_name, json_file in split_map.items():
    json_path = os.path.join(json_dir, json_file)
    
    if not os.path.exists(json_path):
        print(f"⚠️ JSON file not found: {json_path}")
        continue
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        image_files = [img['file_name'] for img in data.get('images', [])]

    split_folder = os.path.join(output_dir, split_name)
    os.makedirs(split_folder, exist_ok=True)

    for file_name in image_files:
        src = os.path.join(images_dir, file_name)
        dst = os.path.join(split_folder, file_name)

        if os.path.exists(src):
            shutil.copy2(src, dst)  # use shutil.move if you want to move instead of copy
        else:
            print(f"⚠️ Image not found: {src}")

print("✅ All images copied to respective train/val/test folders.")
