import json

ann_file = "/shared/kapardi/object_detection_data/data_corpus_240725/train/_annotations.coco.json"

with open(ann_file, "r") as f:
    data = json.load(f)

# Remove annotations without category_id
before = len(data["annotations"])
data["annotations"] = [ann for ann in data["annotations"] if "category_id" in ann]
after = len(data["annotations"])

with open(ann_file, "w") as f:
    json.dump(data, f)

print(f"Removed {before - after} bad annotations. File updated: {ann_file}")
