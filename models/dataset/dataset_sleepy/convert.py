import os
import subprocess

def convert_mp4_to_avi(mp4_path, avi_path):
    """
    Convert an MP4 file to AVI using FFmpeg.
    """
    command = [
        'ffmpeg', 
        '-i', mp4_path,      # Input file (MP4)
        '-vcodec', 'libx264', # Codec for video
        '-acodec', 'libmp3lame', # Codec for audio
        avi_path              # Output file (AVI)
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def convert_all_mp4_to_avi(dataset_dir):
    """
    Convert all MP4 files in the dataset directory to AVI.
    """
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:
            if file.endswith('.mp4'):
                mp4_file_path = os.path.join(root, file)
                avi_file_path = os.path.join(root, file.replace('.mp4', '.avi'))
                convert_mp4_to_avi(mp4_file_path, avi_file_path)
                print(f"Đã chuyển đổi {file} thành {file.replace('.mp4', '.avi')}")

# Cập nhật đường dẫn thư mục chứa video MP4
dataset_dir = 'D:/KLTN/AI/dataset_sleepy'

# Chuyển đổi tất cả các video MP4 thành AVI
convert_all_mp4_to_avi(dataset_dir)
