import os
import subprocess


def get_rec_file(file_path, out_dir, fps=20):

    # dir_name = os.path.split(file_path)[0]
    file_name = os.path.split(file_path)[-1]

    out_file = f'{os.path.join(out_dir, os.path.splitext(file_name)[0])}.mp4'

    result = subprocess.run(['MP4Box','-add', f'{file_path}:fps={fps}', out_file])

    return result, out_file