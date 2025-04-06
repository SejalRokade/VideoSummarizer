import streamlit as st
import os
import subprocess
import time

st.title("🎥 AI-Powered Video Summarizer")

uploaded_file = st.file_uploader("📂 Upload a video", type=["mp4", "avi", "mov"])

if uploaded_file:
    os.makedirs("inputs", exist_ok=True)
    os.makedirs("frames", exist_ok=True)
    os.makedirs("keyframes", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    video_path = os.path.join("inputs", uploaded_file.name)

    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.video(video_path)
    st.write("⏳ Processing the video... Please wait.")

    subprocess.run(["python", "extract_frames.py", video_path, "frames"])
    st.write("✅ Frames extracted successfully!")
    subprocess.run(["python", "keyframe_selection.py", f"frames/{uploaded_file.name.split('.')[0]}", "keyframes"])
    st.write("✅ Keyframes extracted successfully!")
    subprocess.run(["python", "create_summary.py", f"keyframes/{uploaded_file.name.split('.')[0]}", "outputs", video_path])
    st.write("✅ Summary created successfully!")


    summary_path = f"outputs/{uploaded_file.name.split('.')[0]}_summary.mp4"

    if os.path.exists(summary_path):
        time.sleep(2)
        st.video(summary_path)
    else:
        st.error(f"❌ File not found: {summary_path}")
