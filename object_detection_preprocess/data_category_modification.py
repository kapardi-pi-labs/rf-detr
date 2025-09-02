import json

def update_category_ids(file_paths):

    category_mapping = {1:34, 2: 35, 3: 36, 4: 37}

    for file_path in file_paths:
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Update category_id values
            def update_category(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "category_id" and value in category_mapping:
                            obj[key] = category_mapping[value]
                        else:
                            update_category(value)
                elif isinstance(obj, list):
                    for item in obj:
                        update_category(item)
            
            update_category(data)
            
            # Add categories field

            data["categories"] = [{ "id":34, "name": "backpack", "supercategory": "none" },
                { "id": 35, "name": "satchel", "supercategory": "none" },
                {"id":36,"name":"trolley case","supercategory":"none"},
                {"id":37,"name":"tote bag","supercategory":"none"}]
 
            # Write the updated data back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            
            print(f"Updated {file_path} successfully.")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")


# Example usage:
file_paths = [#"/shared/kapardi/object_detection_data/bag6k/instances_test.json",
                # "/shared/kapardi/object_detection_data/bag6k/instances_train.json",
                "/shared/kapardi/object_detection_data/bag6k/instances_val.json"]
update_category_ids(file_paths)