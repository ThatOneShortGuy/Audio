# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:28:48 2021

@author: braxt
"""
import speech_recognition as sr
import sys
import os
from volume_equalizer import to_ex
from threading import Thread


def recognize(i, save=False):
    name, ext = os.path.splitext(i)
    converted = False
    if ext != '.wav':
        converted = True
        i = to_ex(i, '.wav')
    r = sr.Recognizer()
    with sr.AudioFile(i) as source:
        r.adjust_for_ambient_noise(source, 69)
        audio = r.record(source)
    if converted and not save:
        to_ex(i, ext)
    text = ''
    try:
        text = r.recognize_google(audio)
    except sr.UnknownValueError:
        print('Google could not understand audio')
    except Exception as e:
        print(f'Failed due to {e}')
    if not text:
        try:
            text = r.recognize_google(audio)
        except sr.UnknownValueError:
            print('Google could not understand audio')
        except Exception as e:
            print(f'Failed due to {e}')
    if text:
        print(text)
        with open(name+'.txt', 'w') as f:
            f.writelines(text)


if __name__ == '__main__':
    args = sys.argv
    args.extend(['-f', 'D:/Sounds'])
    if len(args) > 1:
        if args[1] == '-f':
            i = os.listdir(args[2])
            i = [os.path.join(args[2], inp) for inp in i]
        else:
            i = args[1:-1]
        if args[-1] == '-s':
            save = True
        else:
            save = False
    else:
        i = ['C:/Users/braxt/Downloads/SLSS 2100 Elevator Speech.mp3']
    for inputs in i:
        recognize(inputs)
        # th = Thread(target=recognize, args=(inputs, save))
        # th.start()
