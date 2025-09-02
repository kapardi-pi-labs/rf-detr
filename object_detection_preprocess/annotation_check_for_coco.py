import os
import json
import cv2
import csv
from collections import defaultdict


def process_coco_annotation(image_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Find JSON file in the current subfolder
    json_files = [f for f in os.listdir(image_dir) if f.endswith('.json')]
    if not json_files:
        print(f"⚠️ No annotation JSON found in {image_dir}")
        return
    coco_json_path = os.path.join(image_dir, json_files[0])

    # Load COCO data
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)

    # Build image and annotation maps
    image_id_map = {img['id']: img['file_name'] for img in coco_data['images']}
    file_name_to_id = {img['file_name']: img['id'] for img in coco_data['images']}
    category_id_to_name = {cat['id']: cat['name'] for cat in coco_data['categories']}

    anns_by_image = defaultdict(list)
    for ann in coco_data['annotations']:
        anns_by_image[ann['image_id']].append(ann)

    # Lists to track annotated and not-annotated images
    annotated_files = []
    not_annotated_files = []

    for file_name in os.listdir(image_dir):
        if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(image_dir, file_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"⚠️ Warning: Couldn't load image {file_name}")
            continue

        image_id = file_name_to_id.get(file_name)
        anns = anns_by_image.get(image_id, [])

        if image_id is None or not anns:
            not_annotated_files.append(file_name)
            continue

        annotated_files.append(file_name)

        # Draw bounding boxes
        for ann in anns:
            x, y, width, height = ann['bbox']
            x1, y1, x2, y2 = int(x), int(y), int(x + width), int(y + height)
            label = category_id_to_name.get(ann['category_id'], "Unknown")

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            label_size = cv2.getTextSize(label, font, font_scale, thickness)[0]

            # Draw label background and text
            cv2.rectangle(image, (x1, y1 - label_size[1] - 5), (x1 + label_size[0], y1), (0, 255, 0), cv2.FILLED)
            cv2.putText(image, label, (x1, y1 - 5), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

        # Save annotated image
        output_path = os.path.join(output_dir, file_name)
        cv2.imwrite(output_path, image)
        print(f"✅ Saved annotated: {output_path}")

    # Save not_annotated.csv
    if not_annotated_files:
        csv_path = os.path.join(output_dir, "not_annotated.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["filename"])
            for name in not_annotated_files:
                writer.writerow([name])
        print(f"📝 Wrote not_annotated.csv to: {csv_path}")
    else:
        print(f"✅ All images in {image_dir} had annotations.")

    # Save annotated.csv
    if annotated_files:
        csv_path = os.path.join(output_dir, "annotated.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["filename"])
            for name in annotated_files:
                writer.writerow([name])
        print(f"📝 Wrote annotated.csv to: {csv_path}")


def process_all_annotation_folders(root_dir):
    """
    Traverses each folder under the root_dir (e.g., Rahul/),
    and processes 'train', 'valid', 'test' subfolders individually.
    """
    # for folder in os.listdir(root_dir):
        # folder_path = os.path.join(root_dir, folder)
    folder_path = root_dir
    # if not os.path.isdir(folder_path):
    #     # folder_path = root_dir
    #     continue

    # print(f"\n📁 Found annotation set: {folder_path}")
    # folder_path = root_dir
    # for subfolder in ['train', 'valid', 'test']:
    #     subfolder_path = os.path.join(folder_path, subfolder)
    #     if not os.path.isdir(subfolder_path):
    #         continue

    output_subdir = os.path.join(folder_path, f"{folder_path}_annotated")
    print(f"🔍 Processing: {folder_path}")
    process_coco_annotation(folder_path, output_subdir)


# ======= MAIN =======
if __name__ == "__main__":
    root_dir = "/data/kapardi/models/rf-detr/object_detection_preprocess/all_frames"
    process_all_annotation_folders(root_dir)
