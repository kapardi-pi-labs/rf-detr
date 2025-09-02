import json

def check_and_prettify_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)  # Step 1: Load and check for syntax errors
        
        print("✅ JSON is valid!")

        # Step 2: Prettify the JSON and write to a new file
        pretty_path = file_path.replace(".json", "_pretty.json")
        with open(pretty_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"📄 Prettified JSON saved to: {pretty_path}")

    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
    except FileNotFoundError:
        print("❌ File not found.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

# Example usage:
check_and_prettify_json("/data/kapardi/rf-detr/data_corpus_soda/valid/_annotations.coco.json")
