import os
import cv2
import random

def get_images_from_directory(directory):
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(('png', 'jpg', 'jpeg'))]
    images.sort()  # Sort to maintain order
    return images

def create_video(images, output_path, frame_size, fps=30, frames_per_image=30):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    
    for img_path in images:
        frame = cv2.imread(img_path)
        frame = cv2.resize(frame, frame_size)
        for _ in range(frames_per_image):  # Repeat the same image for multiple frames
            video_writer.write(frame)
    
    video_writer.release()

def generate_videos(input_directory, output_directory, num_videos=5, num_images=100, fps=30):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    images = get_images_from_directory(input_directory)
    
    if len(images) < num_images:
        raise ValueError(f"Not enough images in {input_directory}. At least {num_images} required.")
    
    frame_size = cv2.imread(images[0]).shape[1::-1]  # Get frame size (width, height)
    
    for i in range(num_videos):
        selected_images = random.sample(images, num_images)
        output_path = os.path.join(output_directory, f'video_{i+1}.mp4')
        create_video(selected_images, output_path, frame_size, fps)
        print(f"Video {i+1} created: {output_path}")


generate_videos("/data/kapardi/utils/data_custom/dataset/train", "/data/kapardi/utils/Testing_model_videos/syn_videos_2")
