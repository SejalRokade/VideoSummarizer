import cv2
import os
import ffmpeg
import sys

def create_summary_video(keyframe_folder, output_folder, original_video):
    """Creates a summarized video using keyframes (without audio)."""

    if not os.path.exists(keyframe_folder) or not os.listdir(keyframe_folder):
        print(f"❌ No keyframes found in {keyframe_folder}. Check keyframe extraction.")
        return None

    os.makedirs(output_folder, exist_ok=True)

    video_name = os.path.splitext(os.path.basename(original_video))[0]
    output_video_path = os.path.join(output_folder, f"{video_name}_summary.mp4")
    temp_video_path = os.path.join(output_folder, f"{video_name}_temp.mp4")

    try:
        frames = sorted(os.listdir(keyframe_folder), key=lambda x: int(x.split('_')[1].split('.')[0]))

        # Dynamically adjust step size to get ~100 frames
        step = max(1, len(frames) // 100)  
        frames = frames[::step]  

    except Exception as e:
        print(f"❌ Error sorting keyframes: {e}")
        return None

    if not frames:
        print("❌ No frames selected for summary.")
        return None

    sample_frame = cv2.imread(os.path.join(keyframe_folder, frames[0]))
    if sample_frame is None:
        print("❌ Error reading keyframe images. Ensure they are valid.")
        return None

    height, width, _ = sample_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Adjust FPS dynamically (ensures ~5 seconds of summary)
    fps = min(10, len(frames) // 5)  

    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    for frame in frames:
        img_path = os.path.join(keyframe_folder, frame)
        img = cv2.imread(img_path)
        if img is None:
            print(f"⚠️ Skipping invalid frame: {img_path}")
            continue
        out.write(img)

    out.release()
    print(f"✅ Summary video saved (without audio): {temp_video_path}")

    try:
        video_stream = ffmpeg.input(temp_video_path, r=fps)

        # Remove the audio stream
        ffmpeg.output(video_stream, output_video_path, vcodec="libx264", acodec="aac", strict='experimental').run(overwrite_output=True)

        print(f"✅ Final summarized video (without audio) saved as: {output_video_path}")
        return output_video_path
    except ffmpeg.Error as e:
        print(f"❌ FFmpeg merging error: {str(e)}")  # Properly handle error without decode()
        return None

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("❌ Usage: python create_summary.py <keyframe_folder> <output_folder> <original_video>")
    else:
        keyframe_folder = sys.argv[1]
        output_folder = sys.argv[2]
        original_video = sys.argv[3]
        create_summary_video(keyframe_folder, output_folder, original_video)
