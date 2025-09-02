import os
import json
import cv2
import csv
from collections import defaultdict


def process_coco_annotation(all_files_dir, json_path, output_dir,
                            global_not_annotated, global_annotated):
    os.makedirs(output_dir, exist_ok=True)

    # Load COCO data
    with open(json_path, 'r') as f:
        coco_data = json.load(f)

    # Build image and annotation maps
    file_name_to_id = {img['file_name']: img['id'] for img in coco_data['images']}
    category_id_to_name = {cat['id']: cat['name'] for cat in coco_data['categories']}

    anns_by_image = defaultdict(list)
    for ann in coco_data['annotations']:
        anns_by_image[ann['image_id']].append(ann)

    annotated_files = []
    not_annotated_files = []

    for file_name in os.listdir(all_files_dir):
        if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(all_files_dir, file_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"⚠️ Warning: Couldn't load image {file_name}")
            continue

        image_id = file_name_to_id.get(file_name)
        anns = anns_by_image.get(image_id, [])

        if image_id is None or not anns:
            not_annotated_files.append(file_name)
            global_not_annotated.add(file_name)
            continue

        annotated_files.append(file_name)
        global_annotated.add(file_name)

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
            cv2.rectangle(image,
                          (x1, y1 - label_size[1] - 5),
                          (x1 + label_size[0], y1),
                          (0, 255, 0), cv2.FILLED)
            cv2.putText(image, label, (x1, y1 - 5), font,
                        font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

        # Save annotated image in the common output dir
        output_path = os.path.join(output_dir, file_name)
        cv2.imwrite(output_path, image)

    # Save per-JSON annotated.csv (inside output_dir for reference)
    if annotated_files:
        csv_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(json_path))[0]}_annotated.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["filename"])
            for name in sorted(annotated_files):
                writer.writerow([name])
        print(f"📝 Wrote {csv_path}")


def process_all_jsons(folder, final_output_dir):
    """
    folder: contains both images (.jpg) and multiple JSONs
    final_output_dir: common directory where all annotated images go
    """
    os.makedirs(final_output_dir, exist_ok=True)

    global_not_annotated = set()
    global_annotated = set()

    for json_file in os.listdir(folder):
        if not json_file.endswith(".json"):
            continue

        json_path = os.path.join(folder, json_file)
        print(f"🔍 Processing {json_file} ...")
        process_coco_annotation(folder, json_path, final_output_dir,
                                global_not_annotated, global_annotated)

    # Save cumulative not_annotated.csv
    if global_not_annotated:
        csv_path = os.path.join(final_output_dir, "not_annotated.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["filename"])
            for name in sorted(global_not_annotated):
                writer.writerow([name])
        print(f"📝 Wrote cumulative not_annotated.csv ({len(global_not_annotated)} files)")

    # Save cumulative annotated.csv
    if global_annotated:
        csv_path = os.path.join(final_output_dir, "annotated.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["filename"])
            for name in sorted(global_annotated):
                writer.writerow([name])
        print(f"📝 Wrote cumulative annotated.csv ({len(global_annotated)} files)")


# ======= MAIN =======
if __name__ == "__main__":
    folder = "/shared/kapardi/object_detection_data/cctv_footage"  # contains JPGs + JSONs
    final_output_dir = "/shared/kapardi/object_detection_data/cctv_annotated_validation"
    process_all_jsons(folder, final_output_dir)
