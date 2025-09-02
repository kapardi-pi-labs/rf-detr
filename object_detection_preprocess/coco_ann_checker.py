import json

ann_file = "/shared/kapardi/object_detection_data/data_corpus_240725/train/_annotations.coco.json"  # update path
with open(ann_file, "r") as f:
    data = json.load(f)

bad_anns = [ann for ann in data["annotations"] if "category_id" not in ann]
print(f"Found {len(bad_anns)} annotations without category_id")

if bad_anns:
    print("Example:", bad_anns[0])
