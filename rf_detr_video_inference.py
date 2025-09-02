import os
import cv2
import supervision as sv
from rfdetr import RFDETRLarge

CATEGORY_ID_TO_NAME = {0: "People",1: "person", 2: "weapons", 3: "pistol",  4: "rifle", 5: "sword" , 6: "cigar", 7: "cocaine", 8: "bomb",
        9: "liquor_bottle", 10: "molotov", 11: "vehicles", 12: "four_wheeler", 13: "three_wheeler", 14: "two_wheeler", 
        15: "heavy_wheeler",16:"license_plate",17:"accessories",18:"smartphone",19:"purse",20:"bill",21:"card",22:"backpack",
        23: "satchel", 24: "trolley case", 25:"tote bag"}

# Initialize the model
model = RFDETRLarge(pretrain_weights='/data/kapardi/models/rf-detr/output_31072025/checkpoint0009.pth')
model.optimize_for_inference()

def callback(frame, index):
    detections = model.predict(frame, threshold=0.5)
    labels = [
        f"{CATEGORY_ID_TO_NAME.get(class_id, 'Unknown')} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]
    annotated_frame = frame.copy()
    annotated_frame = sv.BoxAnnotator().annotate(annotated_frame, detections)
    annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels)
    return annotated_frame

def process_video(source_path, target_path, callback):
    print(f"[✓] Processing video: {source_path} -> {target_path}")
    cap = cv2.VideoCapture(source_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {source_path}.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(target_path, fourcc, fps, (frame_width, frame_height))

    index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame = callback(frame, index)
        out.write(annotated_frame)
        index += 1

    cap.release()
    out.release()
    print(f"[✓] Saved: {target_path}")

def process_directory(input_dir, output_dir, callback):
    try:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.mp4'):
                    input_video_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, input_dir)
                    output_video_dir = os.path.join(output_dir, relative_path)
                    output_video_path = os.path.join(output_video_dir, file)

                    os.makedirs(output_video_dir, exist_ok=True)
                    process_video(input_video_path, output_video_path, callback)
    except Exception as e:
        print(f"[!] Error processing directory {input_dir}: {e}")


# Example usage
# source_video_dir = "/shared/kapardi/object_detection_data/dataset/SPHAR-Dataset/videos"
source_video_dir = "/data/kapardi/Test"
output_video_dir = "/data/kapardi/output_videos"
process_directory(source_video_dir, output_video_dir, callback)
