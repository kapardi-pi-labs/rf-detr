import os
import json
import cv2

# Define paths
json_file = "/data/kapardi/detr_pi_sense/data/dataset_corpus/merged_training.json"  # Path to your JSON file
image_dir = "/data/kapardi/detr_pi_sense/data/dataset_corpus/train"  # Folder containing images
save_dir = "/data/kapardi/detr_pi_sense/data/dataset_corpus/train/verify_train_data"  # Output folder for processed images

# Ensure save directory exists
os.makedirs(save_dir, exist_ok=True)

# Load JSON data
with open(json_file, "r") as f:
    data = json.load(f)

# Mapping image IDs to filenames
image_info = {img["id"]: img["file_name"] for img in data["images"]}

# Mapping category IDs to labels
category_id_to_label = {
    16: "ambulance", 17: "auto", 18: "bicycle", 19: "bike", 20: "bulldozer", 21: "bus", 22: "car", 23: "crane",
    24: "excavator", 25: "human_powered_vehicle", 26: "mixer_truck", 27: "pickup", 28: "roller", 29: "tanker",
    30: "tractor", 31: "truck", 32: "van", 1: "person", 3: "pistol", 4: "knife", 5: "rifle", 6: "sword",
    7: "dagger", 8: "switchblade", 9: "cigar", 10: "cocaine", 11: "bomb", 12: "grenade", 13: "liquor_bottle",
    14: "molotov"
}

# Group annotations by image_id
annotations_by_image = {}
for annotation in data.get("annotations", []):
    image_id = annotation["image_id"]
    bbox = annotation["bbox"]  # [x, y, width, height]
    category_id = annotation["category_id"]
    label = category_id_to_label.get(category_id, "unknown")
    
    if image_id not in annotations_by_image:
        annotations_by_image[image_id] = []
    
    annotations_by_image[image_id].append((bbox, label))

# Process each image
for image_id, annotations in annotations_by_image.items():
    if image_id in image_info:
        image_path = os.path.join(image_dir, image_info[image_id])
        save_path = os.path.join(save_dir, image_info[image_id])

        if os.path.exists(image_path):
            # Read image once
            img = cv2.imread(image_path)
            
            # Draw bounding boxes and labels
            for bbox, label in annotations:
                x, y, w, h = map(int, bbox)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red box
                cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Green text
            
            # Save modified image
            cv2.imwrite(save_path, img)
        else:
            print(f"Image not found: {image_path}")
