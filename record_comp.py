# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 11:25:53 2021

@author: braxt
"""

import pyaudio
import wave
from volume_equalizer import equalize, to_ex
from mss import mss
import numpy as np
import time
import cv2
from threading import Thread
import os
from progressbar import ProgressBar

sct = mss()


def record_audio(filename, record_seconds, rate=48000, channels=2, chunk=2048):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=1)
    print('* recording')
    if record_seconds == 0:
        from keyboard import is_pressed
        frames = []
        while not is_pressed('q'):
            frames.append(stream.read(chunk))
    else:
        frames = [stream.read(chunk) for _ in range(int(rate/chunk * record_seconds))]

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    try:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    finally:
        wf.close()


def record_screen(filename, record_seconds, fps=30):
    fourcc = cv2.VideoWriter_fourcc(*'mpgi')
    vid = cv2.VideoWriter(filename, fourcc, fps, (799, 333))
    times = []
    t = time.perf_counter()
    bar = ProgressBar(fps*record_seconds, learning_rate=.008)
    for i in range(fps*record_seconds):
        while time.perf_counter()-t < i/fps:
            pass
        vid.write(np.array(sct.grab((2292, 252, 3091, 585)))[:, :, :3])
        bar.update()

    vid and vid.release()
    return times


def record(filename, secs, fps=30, tempname='part1/temp1'):
    (th := Thread(target=record_screen, args=(f'{tempname}.mp4', secs))).start()
    record_audio(f'{tempname}.wav', secs, 44100)
    equalize(f'{tempname}.wav')
    to_ex(f'{tempname}.wav', '.mp3')
    th.join()
    # os.system(
    #     f'ffmpeg -loglevel error -i {tempname}.mp4 -i {tempname}.mp3 -c:v copy -c:a aac {filename} -y')

    # os.remove('temp69420.wav')
    # os.remove('temp69420.mp4')


record('part1.mp4', 35)
# times = record_screen('temp1.mp4', 5)
# print(np.mean(times))
