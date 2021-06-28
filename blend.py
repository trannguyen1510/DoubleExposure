import random

import cv2
import numpy as np
import tkinter as tk
import imageio


def image_resize_and_pad_crop(image, width=None, height=None, color=(255, 255, 255), inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # Padding to make same size
    delta_w = width - resized.shape[1]
    delta_h = height - resized.shape[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)
    # print(top, bottom, left, right)
    border = [top, bottom, left, right]
    border = [f if f >= 0 else 0 for f in border]
    padded = cv2.copyMakeBorder(resized, border[0], border[1], border[2], border[3], cv2.BORDER_CONSTANT, value=color)

    # Crop to make same size
    (hp, wp) = padded.shape[:2]
    cropped = padded
    if width < wp:
      cropped = padded[:, :width]
    if height < hp:
      cropped = padded[:height, :]
    # return the resized image
    return cropped


def fit_screen(img, width, height):
    h, w = img.shape[:2]
    while True:
        if w > width or h > height * 2:
            h = h//2
            w = w//2
        else:
            break
    return cv2.resize(img, (w, h), cv2.INTER_AREA)


def blending(path_in, path_effect, path_mask, color_bg=(178, 192, 192), alpha=0.5):

    img_color_in = cv2.imread(path_in, cv2.IMREAD_UNCHANGED)
    img_color_effect = cv2.imread(path_effect, cv2.IMREAD_UNCHANGED)
    img_color_mask = cv2.imread(path_mask, cv2.IMREAD_UNCHANGED)

    if img_color_in.shape != img_color_effect.shape:
        img_color_effect = image_resize_and_pad_crop(img_color_effect, img_color_in.shape[1], img_color_in.shape[0])

    # mask_rgb = cv2.cv2.cvtColor(img_color_mask, cv2.COLOR_GRAY2BGR)
    # vertical = np.hstack((img_color_in, img_color_effect, mask_rgb))
    # cv2.imshow('Input-Effect-Mask', vertical)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    mat = np.repeat(np.asarray(img_color_mask)[:, :, None], 3, axis=2) / 255
    after = img_color_in * mat * (1 - alpha) + img_color_effect * alpha + np.full(img_color_in.shape, color_bg) * (1 - mat)
    return after/255


def blend_gif(url, img):
    url = "https://media0.giphy.com/media/2vmiW6mcYgKst3QVDK/giphy.gif"

    frames = imageio.mimread(imageio.core.urlopen(url).read(), '.gif')

def save(folder, img):
    random_idx = random.randint(1, 1000)
    name = 'blend_{0}.png'.format(random_idx)
    path = folder + '/' + name
    cv2.imwrite(path, img*255)
    return name


if __name__ == '__main__':
    # result = blending('static\input2.jpg', 'static\effect2.jpg', 'static\input2_mask.png')
    # print(result.shape)
    # cv2.imshow('Result', result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imwrite('static/blend.png', result*255)

    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    print(screen_width, screen_height)
