import os
import subprocess


def get_rec_file(file_name):

    out_file = f'{os.path.splitext(os.path.split(file_name)[-1])[0]}.mp4'

    result = subprocess.run(['MP4Box',
                    '-add', file_name,
                    ':fps=20', out_file])