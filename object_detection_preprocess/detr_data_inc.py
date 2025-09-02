import json
import os
import cv2
import shutil

def main():
    main_dir = input("Enter the main directory path: ")
    train_coco_file = input("Enter the training data annotation JSON path: ")
    valid_coco_file = input("Enter the validation data annotation JSON path: ")
    test_coco_file = input("Enter the test data annotation JSON path: ")
    dataset_main = "dataset_custom_new_upd"

    os.makedirs(f"{dataset_main}/train", exist_ok=True)
    os.makedirs(f"{dataset_main}/valid", exist_ok=True)
    os.makedirs(f"{dataset_main}/test", exist_ok=True)

    subdirs = [d for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d))]
    if not subdirs:
        print("No subdirectories found in the main directory.")
        return

    print("Available subdirectories:")
    for i, subdir in enumerate(subdirs, 1):
        print(f"{i}. {subdir}")
    
    selected_indices = input("Enter the numbers of the subdirectories to process (comma-separated): ")
    selected_subdirs = [subdirs[int(i) - 1] for i in selected_indices.split(",") if i.isdigit() and 1 <= int(i) <= len(subdirs)]

    for dataset_type, coco_file, updated_coco_file in zip(
        ["train", "valid", "test"],
        [train_coco_file, valid_coco_file, test_coco_file],
        ["updated_train.json", "updated_valid.json", "updated_test.json"]
    ):
        copied_coco_file = os.path.join(dataset_main, updated_coco_file)
        shutil.copy(coco_file, copied_coco_file)
        coco_data = load_coco_data(copied_coco_file)
        
        for category in selected_subdirs:
            mapped_category = map_category(category)
            if mapped_category is None:
                print(f"Skipping unknown category: {category}")
                continue

            image_dir = os.path.join(main_dir, category, dataset_type, "images")
            label_dir = os.path.join(main_dir, category, dataset_type, "labels")
            output_dir = os.path.join(dataset_main, dataset_type, "images")
            
            category_id = add_category(coco_data, mapped_category, "weapons")
            try:
                process_images(coco_data, image_dir, label_dir, output_dir, category_id)
            except Exception as e:
                pass
            save_coco_data(coco_data, copied_coco_file)

        print(f"Updated {dataset_type} COCO file saved at: {copied_coco_file}")

def map_category(original_name):
    category_mapping = {
        # "shotgun": "shotgun",
        "sword": "sword",
        "bombs": "bomb",
        "liquorbottle": "liquor_bottle",
        "rifle": "rifle",
        # "grenade": "grenade",
        "handgun": "pistol",
        "desikatta": "pistol",
        "gun": "pistol",
        "knife": "knife",
        # "dagger": "dagger",
        "cocaine": "cocaine",
        "cigar": "cigar",
        "licenseplate": "license_plate",
        # "switchblades": "switchblade",
        "molotov": "molotov",
        "rifle": "rifle",
        "pistol": "pistol"
    }
    return category_mapping.get(original_name, None)

def load_coco_data(coco_file_path):
    if not os.path.exists(coco_file_path):
        raise FileNotFoundError(f"COCO file not found at {coco_file_path}")
    with open(coco_file_path, "r") as f:
        return json.load(f)

def save_coco_data(coco_data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(coco_data, f, indent=4)
    print(f"COCO file updated at: {output_path}")

def get_next_ids(coco_data):
    return (max((img["id"] for img in coco_data["images"]), default=0) + 1,
            max((ann["id"] for ann in coco_data["annotations"]), default=0) + 1)

def add_category(coco_data, category_name, supercategory_name="weapons"):
    """Ensures category is added to COCO data, but retains ID 1 for 'person'."""

    # Ensure 'people' and 'person' exist and keep 'person' as ID 1
    if category_name.lower() == "person":
        if not any(c["name"].lower() == "people" for c in coco_data["categories"]):
            coco_data["categories"].append({"id": 0, "name": "people", "supercategory": "none"})
        if not any(c["name"].lower() == "person" for c in coco_data["categories"]):
            coco_data["categories"].append({"id": 1, "name": "person", "supercategory": "people"})
        print("Default categories 'people' and 'person' ensured in dataset.")
        return 1  # Always return 1 for 'person'

    if not any(c["id"] == 2 and c["name"].lower() == "weapons" for c in coco_data["categories"]):
        coco_data["categories"].append({"id": 2, "name": "weapons", "supercategory": "none"})

    # Check if the category already exists
    existing_category = next((c for c in coco_data["categories"] if c["name"].lower() == category_name.lower()), None)
    if existing_category:
        return existing_category["id"]  # Use existing category ID

    # Assign next available ID (excluding 1)
    existing_ids = {c["id"] for c in coco_data["categories"]}
    category_id = max(existing_ids) + 1 if existing_ids else 2  # Ensure first non-person category starts from 2

    coco_data["categories"].append({
        "id": category_id,
        "name": category_name,
        "supercategory": supercategory_name
    })
    print(f"New category '{category_name}' added with ID {category_id}")
    return category_id

def process_images(coco_data, image_dir, label_dir, output_dir, category_id):
    """Processes images and annotations, ensuring correct COCO format."""
    os.makedirs(output_dir, exist_ok=True)
    next_image_id = max((img["id"] for img in coco_data["images"]), default=0) + 1
    next_annotation_id = max((ann["id"] for ann in coco_data["annotations"]), default=0) + 1

    for filename in os.listdir(image_dir):
        if filename.endswith((".jpg", ".png")):
            image_path = os.path.join(image_dir, filename)
            label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + ".txt")
            output_image_path = os.path.join(output_dir, filename)

            # Copy image to dataset_main/train, valid, or test
            shutil.copy(image_path, output_image_path)

            image = cv2.imread(image_path)
            if image is None:
                print(f"Skipping {filename}: Cannot read image")
                continue

            original_height, original_width = image.shape[:2]

            # Add image metadata to COCO JSON
            coco_data["images"].append({
                "id": next_image_id,
                "license": 1,
                "file_name": filename,
                "height": original_height,
                "width": original_width,
                "date_captured": "2025-02-20T12:00:00+00:00"
            })

            # Process labels if they exist
            if os.path.exists(label_path):
                with open(label_path, "r") as label_file:
                    for line in label_file:
                        values = line.strip().split()
                        class_id, x_min, y_min, bbox_width, bbox_height = map(float, values)

                        # Ensure "person" (ID 1) remains unchanged
                        if class_id == 1:
                            final_category_id = 1
                        else:
                            final_category_id = category_id

                        coco_data["annotations"].append({
                            "id": next_annotation_id,
                            "image_id": next_image_id,
                            "category_id": final_category_id,  # Keeps 1 unchanged
                            "bbox": [x_min, y_min, bbox_width, bbox_height],
                            "area": bbox_width * bbox_height,
                            "iscrowd": 0
                        })
                        next_annotation_id += 1

            next_image_id += 1

def merge_coco_annotations(coco_file, merged_coco_data):
    new_data = load_coco_data(coco_file)

    # Merge images
    existing_filenames = {img["file_name"] for img in merged_coco_data["images"]}
    new_images = [img for img in new_data["images"] if img["file_name"] not in existing_filenames]
    merged_coco_data["images"].extend(new_images)

    # Merge annotations
    existing_annotation_ids = {ann["id"] for ann in merged_coco_data["annotations"]}
    new_annotations = [ann for ann in new_data["annotations"] if ann["id"] not in existing_annotation_ids]
    merged_coco_data["annotations"].extend(new_annotations)

    # Merge categories
    existing_category_ids = {cat["id"] for cat in merged_coco_data["categories"]}
    new_categories = [cat for cat in new_data["categories"] if cat["id"] not in existing_category_ids]
    merged_coco_data["categories"].extend(new_categories)

if __name__ == "__main__":
    main()
