#encoding: utf-8
import copy
import os
import platform
import sys
from argparse import ArgumentParser
from time import sleep

import numpy as np
from PIL import ImageChops, ImageFilter, ImageGrab
from pynput import mouse


def gblur(img):
    return img.filter(ImageFilter.GaussianBlur(4))

def gblur_and_2binary(img):
    return np.average(np.asarray(gblur(img)), axis=2)


class Shotter:
    def __init__(self, threshold=10, dirname='out', upper_left=(0, 0), lower_right=(512, 512)):
        self.num = 0
        self.dir = dirname
        self.bbox = (upper_left[0], upper_left[1], lower_right[0], lower_right[1])

        os.makedirs(dirname, exist_ok=True)

        img = ImageGrab.grab(bbox=self.bbox)
        img.save(self.filename)
        self.past_img = gblur_and_2binary(img)

        self.th = threshold

    @property
    def filename(self):
        name = self.dir + '/' + str(self.num) + '.jpg'
        self.num += 1
        return name

    def __call__(self):
        img = ImageGrab.grab(bbox=self.bbox)

        blur = copy.copy(img)
        blur = gblur_and_2binary(blur)

        #print(abs(np.average(self.past_img - blur)))
        if abs(np.average(self.past_img - blur)) < self.th:
            return

        self.past_img = blur
        img.save(self.filename)


g_upper_left = None
g_lower_right = None
def on_click(x, y, button, pressed):
    global g_upper_left, g_lower_right
    if not pressed:
        return True

    if not g_upper_left:
        g_upper_left = (x, y)
        print('[Message] upper left position is (' + str(x) + ', ' + str(y) + ')')

    elif not g_lower_right:
        g_lower_right = (x, y)
        print('[Message] lower right position is (' + str(x) + ', ' + str(y) + ')')

    else:
        return False


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--dir', type=str, default='out')
    parser.add_argument('--threshold', type=float, default=0.1)
    opt = parser.parse_args()

    if platform.system() == 'Windows':
        from ctypes import windll
        user32 = windll.user32
        user32.SetProcessDPIAware()

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    st = Shotter(threshold=opt.threshold, dirname=opt.dir, upper_left=g_upper_left, lower_right=g_lower_right)
    while True:
        st()
        sleep(0.5)
