import tensorflow as tf
from typing import List
import cv2
import os

vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")

# Mapping integers back to original characters
num_to_char = tf.keras.layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True)


# Load the video
def load_video(path: str) -> List[float]:
    cap = cv2.VideoCapture(path)
    frames = []
    for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, frame = cap.read()
        frame = tf.image.rgb_to_grayscale(frame)
        frames.append(frame[190:236, 80:220, :])  # type: ignore
    cap.release()

    mean = tf.math.reduce_mean(frames)
    std = tf.math.reduce_std(tf.cast(frames, tf.float32))
    return tf.cast((frames - mean), tf.float32) / std


# Load the subtitles for video
def load_subtitles(path: str) -> List[str]:
    with (open(path, 'r') as f):
        lines = f.readlines()
    tokens = []
    for line in lines:
        line = line.split()
        if line[2] != 'sil':
            tokens = [*tokens, ' ', line[2]]
    return char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))[1:]


# Loading the video and subtitles simultaneously
def load_data(path: str):
    path = bytes.decode(path.numpy())

    # Path Splitter for MacOS/Linux
    file_name = path.split('/')[-1].split('.')[0]

    # for Windows
    # file_name = path.split('\\')[-1].split('.')[0]

    video_path = os.path.join('..', 'dataset', 'videos', f'{file_name}.mpg')  # replace with your location
    subtitles_path = os.path.join('..', 'dataset', 'subtitles', f'{file_name}.align')  # replace with your location
    frames = load_video(video_path)
    subtitles = load_subtitles(subtitles_path)

    return frames, subtitles
