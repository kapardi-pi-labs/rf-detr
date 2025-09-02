import json

# Path to your COCO annotation JSON file
json_path = "/data/kapardi/utils/data_custom/annotations/instances_train2017.json"
output_file = "category_image_counts_train.txt"

# Load JSON data
with open(json_path, "r") as f:
    coco_data = json.load(f)

# Extract categories and annotations
categories = {cat["id"]: cat["name"] for cat in coco_data["categories"]}
category_image_counts = {cat: set() for cat in categories.values()}

# Count unique images per category
for ann in coco_data["annotations"]:
    category_name = categories[ann["category_id"]]
    category_image_counts[category_name].add(ann["image_id"])

# Save results to a text file
with open(output_file, "w") as f:
    for category, images in category_image_counts.items():
        f.write(f"{category}: {len(images)} images\n")

print(f"Image count per category saved to {output_file}")
