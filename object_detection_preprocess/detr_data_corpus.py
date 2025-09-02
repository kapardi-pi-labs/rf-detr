# import json
# import os
# import shutil

# def merge_json(file1, file2, output_file):
#     try:
#         # Load JSON data from both files
#         with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
#             data1 = json.load(f1)
#             data2 = json.load(f2)

#         # Fix duplicate annotation IDs
#         merged_data = fix_annotation_ids(data1, data2)

#         # Save merged JSON
#         with open(output_file, 'w', encoding='utf-8') as out:
#             json.dump(merged_data, out, indent=4, ensure_ascii=False)

#         print(f"Merged JSON saved: {output_file}")
#     except Exception as e:
#         print(f"Error merging JSON files: {e}")

# def fix_annotation_ids(data1, data2):
#     """Ensures unique annotation and image IDs while keeping correct references"""
    
#     # Find the max existing IDs in data1
#     max_ann_id = max([ann["id"] for ann in data1.get("annotations", [])], default=0)
#     max_img_id = max([img["id"] for img in data1.get("images", [])], default=0)

#     # Create a new merged dictionary
#     merged = data1.copy()

#     # Map old image IDs from data2 to new IDs
#     existing_images = {img["file_name"]: img for img in merged.get("images", [])}
#     image_id_map = {}  # Maps old image_id to new image_id

#     for img in data2.get("images", []):
#         old_img_id = img["id"]
#         if img["file_name"] not in existing_images:
#             max_img_id += 1  # Assign new unique image ID
#             img["id"] = max_img_id
#             merged.setdefault("images", []).append(img)
#             existing_images[img["file_name"]] = img
#             image_id_map[old_img_id] = max_img_id  # Store mapping
#         else:
#             image_id_map[old_img_id] = existing_images[img["file_name"]]["id"]

#     # Merge annotations while updating IDs and correcting image references
#     for ann in data2.get("annotations", []):
#         max_ann_id += 1  # Assign new unique annotation ID
#         ann["id"] = max_ann_id

#         # Update image_id to match the new ID assigned
#         if ann["image_id"] in image_id_map:
#             ann["image_id"] = image_id_map[ann["image_id"]]

#         merged.setdefault("annotations", []).append(ann)

#     # Merge categories (ensuring uniqueness)
#     existing_categories = {cat["id"]: cat for cat in merged.get("categories", [])}
#     for cat in data2.get("categories", []):
#         if cat["id"] not in existing_categories:
#             merged["categories"].append(cat)
#             existing_categories[cat["id"]] = cat

#     return merged

# def merge_dicts(d1, d2):
#     """Recursively merge two dictionaries, properly handling lists."""
#     if isinstance(d1, dict) and isinstance(d2, dict):
#         merged = d1.copy()
#         for key, value in d2.items():
#             if key in merged:
#                 merged[key] = merge_dicts(merged[key], value)  # Recursively merge
#             else:
#                 merged[key] = value
#         return merged
#     elif isinstance(d1, list) and isinstance(d2, list):
#         # Merge lists, avoiding duplicates for non-dictionaries
#         merged_list = []
#         seen = set()

#         for item in d1 + d2:
#             if isinstance(item, dict):
#                 merged_list.append(item)  # Keep dicts without deduplication
#             else:
#                 if item not in seen:
#                     seen.add(item)
#                     merged_list.append(item)

#         return merged_list
#     else:
#         return d2 if d1 != d2 else d1  # Keep unique values


# def merge_directories(source1, source2, destination):
#     os.makedirs(destination, exist_ok=True)
    
#     for subdir in ['train', 'valid', 'test']:
#         src1_path = os.path.join(source1, subdir)
#         src2_path = os.path.join(source2, subdir)
#         dest_path = os.path.join(destination, subdir)
#         os.makedirs(dest_path, exist_ok=True)
        
#         # Helper function to copy files safely
#         def copy_files(src, dest):
#             if os.path.exists(src):
#                 for item in os.listdir(src):
#                     src_item = os.path.join(src, item)
#                     dest_item = os.path.join(dest, item)
                    
#                     if os.path.isdir(src_item):  # Handle directories
#                         shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
#                     else:  # Handle files
#                         count = 1
#                         while os.path.exists(dest_item):
#                             base, ext = os.path.splitext(item)
#                             dest_item = os.path.join(dest, f"{base}_copy{count}{ext}")
#                             count += 1
#                         shutil.copy2(src_item, dest_item)
        
#         # Copy from both sources
#         copy_files(src1_path, dest_path)
#         copy_files(src2_path, dest_path)

# def main():
#     # Get user input for directories and JSON files
#     source_dir1 = input("Enter first source directory: ")
#     source_dir2 = input("Enter second source directory: ")
#     training_json1 = input("Enter first training JSON file: ")
#     training_json2 = input("Enter second training JSON file: ")
#     # validation_json1 = input("Enter first validation JSON file: ")
#     # validation_json2 = input("Enter second validation JSON file: ")
#     # test_json1 = input("Enter first test JSON file: ")
#     # test_json2 = input("Enter second test JSON file: ")
#     output_dir = input("Enter output directory: ")
    
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Merge JSON files and store in output directory
#     merge_json(training_json1, training_json2, os.path.join(output_dir, 'merged_training_2.json'))
#     # merge_json(validation_json1, validation_json2, os.path.join(output_dir, 'merged_validation.json'))
#     # merge_json(test_json1, test_json2, os.path.join(output_dir, 'merged_test.json'))
    
#     # Merge directories
#     merge_directories(source_dir1, source_dir2, output_dir)
    
#     print(f"Merged JSON and directory structure created successfully in {output_dir}!")

# if __name__ == "__main__":
#     main()
import json
import os
import shutil
import hashlib
import copy

def merge_json(file1, file2, output_file):
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        merged_data = fix_annotation_ids(data1, data2)

        with open(output_file, 'w', encoding='utf-8') as out:
            json.dump(merged_data, out, indent=4, ensure_ascii=False)

        print(f"Merged JSON saved: {output_file}")
    except Exception as e:
        print(f"Error merging JSON files: {e}")

def fix_annotation_ids(data1, data2):
    """Ensures unique annotation and image IDs while keeping correct references"""
    data1 = copy.deepcopy(data1)

    max_ann_id = max([ann["id"] for ann in data1.get("annotations", [])], default=0)
    max_img_id = max([img["id"] for img in data1.get("images", [])], default=0)

    merged = data1
    existing_images = {img["file_name"]: img for img in merged.get("images", [])}
    image_id_map = {}

    for img in data2.get("images", []):
        old_img_id = img["id"]
        if img["file_name"] not in existing_images:
            max_img_id += 1
            img["id"] = max_img_id
            merged.setdefault("images", []).append(img)
            existing_images[img["file_name"]] = img
            image_id_map[old_img_id] = max_img_id
        else:
            image_id_map[old_img_id] = existing_images[img["file_name"]]["id"]

    for ann in data2.get("annotations", []):
        max_ann_id += 1
        ann["id"] = max_ann_id
        if ann["image_id"] in image_id_map:
            ann["image_id"] = image_id_map[ann["image_id"]]
        merged.setdefault("annotations", []).append(ann)

    existing_categories = {cat["id"]: cat for cat in merged.get("categories", [])}
    for cat in data2.get("categories", []):
        if cat["id"] not in existing_categories:
            merged["categories"].append(cat)
            existing_categories[cat["id"]] = cat

    return merged

def safe_copy(src, dest):
    """Copies file safely, renaming if too long or duplicate"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    base, ext = os.path.splitext(os.path.basename(dest))

    # If filename is too long, shorten with hash
    if len(base) > 100:
        base = hashlib.md5(base.encode()).hexdigest()[:16]
        dest = os.path.join(os.path.dirname(dest), base + ext)

    count = 1
    while os.path.exists(dest):
        dest = os.path.join(os.path.dirname(dest), f"{base}_copy{count}{ext}")
        count += 1

    shutil.copy2(src, dest)

def merge_directories(source1, source2, destination):
    os.makedirs(destination, exist_ok=True)

    for subdir in ['train', 'valid', 'test']:
        for src in [source1, source2]:
            src_path = os.path.join(src, subdir)
            dest_path = os.path.join(destination, subdir)
            os.makedirs(dest_path, exist_ok=True)

            if os.path.exists(src_path):
                for item in os.listdir(src_path):
                    src_item = os.path.join(src_path, item)
                    dest_item = os.path.join(dest_path, item)

                    if os.path.isdir(src_item):
                        shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
                    else:
                        safe_copy(src_item, dest_item)

def main():
    source_dir1 = input("Enter first source directory: ")
    source_dir2 = input("Enter second source directory: ")
    training_json1 = input("Enter first training JSON file: ")
    training_json2 = input("Enter second training JSON file: ")
    output_dir = input("Enter output directory: ")

    os.makedirs(output_dir, exist_ok=True)

    merge_json(training_json1, training_json2,
               os.path.join(output_dir, 'merged_training_11.json'))
    # merge_directories(source_dir1, source_dir2, output_dir)

    print(f"Merged JSON and directory structure created successfully in {output_dir}!")

if __name__ == "__main__":
    main()
