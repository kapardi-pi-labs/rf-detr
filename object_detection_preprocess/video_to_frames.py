import cv2
import os

# Input and output directories
video_dir = "/data/kapardi/utils/Testing_model_videos/syn_videos_2"  # Change this to your video directory
output_dir = "/data/kapardi/utils/Testing_model_videos/syn_videos_2/frames"  # Change this to where frames should be saved

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get all video files in the directory
video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]

for video_file in video_files:
    video_path = os.path.join(video_dir, video_file)
    
    # Create a directory for frames of this video
    video_name = os.path.splitext(video_file)[0]  # Remove extension
    frame_dir = os.path.join(output_dir, video_name)
    os.makedirs(frame_dir, exist_ok=True)
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # Break when video ends
        
        frame_filename = os.path.join(frame_dir, f"frame_{frame_count:04d}.jpg")  # Save frame
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

    cap.release()
    print(f"Extracted {frame_count} frames from {video_file}")

print("Frame extraction complete!")
