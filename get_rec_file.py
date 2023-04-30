import os
import subprocess


def get_rec_file(file_path, fps=20):

    dir_name = os.path.split(file_path)[0]
    file_name = os.path.split(file_path)[-1]

    out_file = f'{os.path.join(dir_name, os.path.splitext(file_name)[0])}.mp4'

    result = subprocess.run(['MP4Box',
                    '-add', f'{file_name}:fps={fps}', out_file])