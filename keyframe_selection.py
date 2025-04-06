import cv2
import os
import sys
import numpy as np

def extract_keyframes(frame_folder, output_folder, threshold_ratio=0.02, hist_threshold=0.85, min_interval=3):
    """
    Extracts keyframes based on frame differences and histogram comparison.

    Parameters:
    - frame_folder (str): Path to folder containing extracted frames.
    - output_folder (str): Directory to store selected keyframes.
    - threshold_ratio (float): Ratio of max frame difference to decide keyframes.
    - hist_threshold (float): Threshold for histogram correlation (lower = more keyframes).
    - min_interval (int): Minimum interval between keyframes to ensure spread.

    Returns:
    - keyframe_dir (str): Path to keyframe storage.
    """
    video_name = os.path.basename(frame_folder)
    keyframe_dir = os.path.join(output_folder, video_name)
    os.makedirs(keyframe_dir, exist_ok=True)

    frame_files = sorted(os.listdir(frame_folder), key=lambda x: int(x.split('_')[1].split('.')[0]))

    prev_frame = None
    prev_hist = None
    keyframe_count = 0
    last_selected_frame = -min_interval  # Ensures the first frame is selected

    frame_diffs = []

    for i, frame_file in enumerate(frame_files):
        frame_path = os.path.join(frame_folder, frame_file)
        frame = cv2.imread(frame_path)

        if frame is None:
            continue

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.equalizeHist(gray_frame)  # Apply Histogram Equalization

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray_frame).mean()
            frame_diffs.append(diff)

        prev_frame = gray_frame

    # Set threshold dynamically as a percentage of the max difference
    if frame_diffs:
        dynamic_threshold = threshold_ratio * np.max(frame_diffs)
    else:
        dynamic_threshold = 10  # Default fallback

    prev_frame = None

    for i, frame_file in enumerate(frame_files):
        frame_path = os.path.join(frame_folder, frame_file)
        frame = cv2.imread(frame_path)

        if frame is None:
            continue

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.equalizeHist(gray_frame)

        hist = cv2.calcHist([gray_frame], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        is_keyframe = False

        # First frame is always a keyframe
        if prev_frame is None:
            is_keyframe = True
        else:
            frame_diff = cv2.absdiff(prev_frame, gray_frame).mean()
            hist_similarity = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)

            if (frame_diff > dynamic_threshold or hist_similarity < hist_threshold) and (i - last_selected_frame) >= min_interval:
                is_keyframe = True

        if is_keyframe:
            keyframe_path = os.path.join(keyframe_dir, f"keyframe_{keyframe_count}.jpg")
            cv2.imwrite(keyframe_path, frame)
            keyframe_count += 1
            prev_frame = gray_frame
            prev_hist = hist
            last_selected_frame = i  # Update last selected frame index

    print(f"✅ Extracted {keyframe_count} keyframes in {keyframe_dir}")

    return keyframe_dir

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Usage: python keyframe_selection.py <frame_folder> <output_folder>")
    else:
        frame_folder = sys.argv[1]
        output_folder = sys.argv[2]
        extract_keyframes(frame_folder, output_folder)
