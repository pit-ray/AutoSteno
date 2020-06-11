#encoding: utf-8
import copy
import os
import platform
import sys
from argparse import ArgumentParser
from time import sleep

import cv2
import numpy as np
import pyocr
from PIL import ImageChops, ImageFilter, ImageGrab
from pynput import mouse


def gblur(img):
    return img.filter(ImageFilter.GaussianBlur(4))

def gblur_and_2binary(img):
    return np.average(np.asarray(gblur(img)), axis=2)

def img2text(img):
    tools = pyocr.get_available_tools()

    if len(tools) == 0:
        print('[Erorr] cannot find tesseract-ocr. you have to install tesseract-ocr from (https://tesseract-ocr.github.io/tessdoc/Downloads) and export the installed path.')
        sys.exit(0)

    return tools[0].image_to_string(img, lang='jpn', builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6))


class Shotter:
    def __init__(self, threshold=10, dirname='out', upper_left=(0, 0), lower_right=(512, 512), use_ocr=True):
        self.num = 0
        self.dir = dirname
        self.use_ocr = use_ocr
        self.bbox = (upper_left[0], upper_left[1], lower_right[0], lower_right[1])

        os.makedirs(dirname, exist_ok=True)

        img = ImageGrab.grab(bbox=self.bbox)
        self.save_and_2text(img)
        self.past_img = gblur_and_2binary(img)

        self.th = threshold

    @property
    def filename(self):
        name = self.dir + '/' + str(self.num) + '.jpg'
        self.num += 1
        return name

    def save_and_2text(self, img):
        img.save(self.filename)

        #if not self.use_ocr:
        #    return

        #with open(self.dir + '/note.txt', 'a') as f:
        #    f.write('@' + self.filename)

        #    res = img2text(img)
        #    for text in res:
        #        f.write(text.content)
        #    f.write('\n')

    def __call__(self):
        img = ImageGrab.grab(bbox=self.bbox)

        blur = copy.copy(img)
        blur = gblur_and_2binary(blur)

        #print(abs(np.average(self.past_img - blur)))
        if abs(np.average(self.past_img - blur)) < self.th:
            return

        self.past_img = blur
        self.save_and_2text(img)


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
    parser.add_argument('--use_ocr', action='store_true')
    parser.add_argument('--dir', type=str, default='out')
    parser.add_argument('--threshold', type=float, default=0.1)
    opt = parser.parse_args()

    if platform.system() == 'Windows':
        from ctypes import windll
        user32 = windll.user32
        user32.SetProcessDPIAware()

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    st = Shotter(threshold=opt.threshold, dirname=opt.dir, upper_left=g_upper_left, lower_right=g_lower_right, use_ocr=opt.use_ocr)
    while True:
        st()
        sleep(0.5)
