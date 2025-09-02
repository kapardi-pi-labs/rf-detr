import json

# Input and output file paths
input_file = "output.json"
output_file = "output_new.json"

# Category id to change
old_id = 2
new_id = 100003

def strip_temp_ids(data):
    """
    Recursively strip '1000xx' prefix → keep only 'xx' for category_id fields.
    Example: 100022 -> 22
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "category_id" and isinstance(value, int) and value >= 100000:
                data[key] = value % 100000
            else:
                strip_temp_ids(value)
    elif isinstance(data, list):
        for item in data:
            strip_temp_ids(item)

def update_category_id(data, old_id, new_id):
    """
    Recursively update all occurrences of 'category_id': old_id to new_id
    inside JSON-like structures (dicts/lists).
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "category_id" and value == old_id:
                data[key] = new_id
            else:
                update_category_id(value, old_id, new_id)
    elif isinstance(data, list):
        for item in data:
            update_category_id(item, old_id, new_id)

# Load JSON
with open(input_file, "r") as f:
    data = json.load(f)

# Update category_id
# update_category_id(data, old_id, new_id)

strip_temp_ids(data)

# Save updated JSON
with open(output_file, "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ Updated all 'category_id': {old_id} to {new_id} in {output_file}")
