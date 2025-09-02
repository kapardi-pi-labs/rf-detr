import os
import zipfile
import json
import subprocess
from pathlib import Path

# ---------------- CONFIG ----------------
VIDEO_DIR = "/data/data/video_annotation/INTERNS/CCTV_Video_Annotation_Done_LOT-1/Arundhati" # directory containing .mp4 and .zip
OUTPUT_FRAMES_DIR = "/shared/kapardi/object_detection_data/cctv_footage"    # directory where all extracted frames will go
MERGED_JSON_PATH = "/shared/kapardi/object_detection_data/cctv_footage/arundhati_cctv.json"
FAILED_LOG_PATH = "failed_logs_arundhati_cctv.txt"
FPS = 30
# ----------------------------------------

os.makedirs(OUTPUT_FRAMES_DIR, exist_ok=True)

merged = {
    "images": [],
    "annotations": [],
    "categories": None  # will keep from the first JSON
}

image_id_counter = 1
ann_id_counter = 1

def log_failure(name, reason):
    """Append failed filename and reason to log file."""
    with open(FAILED_LOG_PATH, "a") as logf:
        logf.write(f"{name} --> {reason}\n")
    print(f"[ERROR] {name}: {reason}")

for file in os.listdir(VIDEO_DIR):
    if file.endswith(".mp4"):
        try:
            video_path = os.path.join(VIDEO_DIR, file)
            base_name = Path(file).stem

            # --- extract zip file ---
            zip_path = os.path.join(VIDEO_DIR, base_name + ".zip")
            if not os.path.exists(zip_path):
                log_failure(file, "Zip not found")
                continue

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(VIDEO_DIR, base_name))
            except Exception as e:
                log_failure(file, f"Failed to unzip: {e}")
                continue

            # find json inside extracted folder
            extracted_folder = os.path.join(VIDEO_DIR, base_name)
            extracted_subfolder = os.path.join(extracted_folder, "annotations")

            if not os.path.exists(extracted_subfolder):
                log_failure(file, "Annotations folder not found inside zip")
                continue

            json_files = [f for f in os.listdir(extracted_subfolder) if f.endswith(".json")]
            if len(json_files) == 0:
                log_failure(file, "No JSON file found in annotations folder")
                continue

            json_path = os.path.join(extracted_subfolder, json_files[0])
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                log_failure(file, f"Failed to read JSON: {e}")
                continue

            # categories only from first JSON
            if merged["categories"] is None:
                merged["categories"] = data["categories"]

            # --- extract frames ---
            frame_prefix = f"{base_name}_"
            frame_out_pattern = os.path.join(OUTPUT_FRAMES_DIR, frame_prefix + "frame_%06d.jpg")

            try:
                cmd = [
                    "ffmpeg", "-i", video_path,
                    "-vf", f"fps={FPS}",
                    "-start_number", "0",
                    frame_out_pattern
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                log_failure(file, f"FFmpeg failed: {e}")
                continue

            # get list of frames actually extracted
            frames = sorted([f for f in os.listdir(OUTPUT_FRAMES_DIR) if f.startswith(frame_prefix)])

            if not frames:
                log_failure(file, "No frames extracted")
                continue

            # --- update images and annotations ---
            oldid2newid = {}
            for img in data["images"]:
                old_id = img["id"]
                new_id = image_id_counter
                image_id_counter += 1

                # assume frames are in same order as json "images"
                if frames:
                    filename = frames.pop(0)
                else:
                    filename = img["file_name"]  # fallback

                merged["images"].append({
                    **img,
                    "id": new_id,
                    "file_name": filename
                })
                oldid2newid[old_id] = new_id

            for ann in data["annotations"]:
                old_img_id = ann["image_id"]
                new_ann_id = ann_id_counter
                ann_id_counter += 1
                merged["annotations"].append({
                    **ann,
                    "id": new_ann_id,
                    "image_id": oldid2newid.get(old_img_id, -1)  # fallback -1 if missing
                })

        except Exception as e:
            log_failure(file, f"Unexpected error: {e}")
            continue

# --- save merged json ---
with open(MERGED_JSON_PATH, "w") as f:
    json.dump(merged, f, indent=2)

print(f"[DONE] Merged JSON saved at {MERGED_JSON_PATH}")
print(f"[DONE] Frames saved at {OUTPUT_FRAMES_DIR}")
print(f"[LOG] Failures saved at {FAILED_LOG_PATH}")
