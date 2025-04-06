import cv2
import os
import sys

def extract_frames(video_path, output_folder):
    """Extracts frames from the given video and saves them in a unique folder."""
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    frame_folder = os.path.join(output_folder, video_name)
    os.makedirs(frame_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(frame_folder, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_path, frame)
        print(f"✅ Extracted frame: {frame_count}")
        frame_count += 1

    cap.release()
    print(f"✅ Extracted {frame_count} frames in {frame_folder}")
    return frame_folder  # Return path to extracted frames

# Run the function when script is executed
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Usage: python extract_frames.py <video_path> <output_folder>")
    else:
        video_path = sys.argv[1]
        output_folder = sys.argv[2]
        extract_frames(video_path, output_folder)
