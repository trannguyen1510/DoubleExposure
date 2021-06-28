import os
import sys
import argparse
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms

from MODNet.src.models.modnet import MODNet


def get_mask(input_path, output_path):

    ckpt_path = 'MODNet/pretrained/modnet_photographic_portrait_matting.ckpt'
    # check input arguments
    if not os.path.exists(input_path):
        print('Cannot find input path: {0}'.format(input_path))
        exit()
    if not os.path.exists(output_path):
        print('Cannot find output path: {0}'.format(output_path))
        exit()
    if not os.path.exists(ckpt_path):
        print('Cannot find ckpt path: {0}'.format(ckpt_path))
        exit()

    # define hyper-parameters
    ref_size = 512

    # define image to tensor transform
    im_transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ]
    )

    # create MODNet and load the pre-trained ckpt
    modnet = MODNet(backbone_pretrained=False)
    # modnet = nn.DataParallel(modnet).cuda()
    modnet = nn.DataParallel(modnet)
    device = torch.device('cpu')
    modnet.load_state_dict(torch.load(ckpt_path, device))
    modnet.eval()

    # inference images
    # im_names = os.listdir(input_path)
    im_name = os.path.split(input_path)[-1]
    print('Process image: {0}'.format(im_name))

    # read image
    # im = Image.open(os.path.join(input_path, im_name))
    im = Image.open(input_path)
    # unify image channels to 3
    im = np.asarray(im)
    if len(im.shape) == 2:
        im = im[:, :, None]
    if im.shape[2] == 1:
        im = np.repeat(im, 3, axis=2)
    elif im.shape[2] == 4:
        im = im[:, :, 0:3]

    # convert image to PyTorch tensor
    im = Image.fromarray(im)
    im = im_transform(im)

    # add mini-batch dim
    im = im[None, :, :, :]

    # resize image for input
    im_b, im_c, im_h, im_w = im.shape
    if max(im_h, im_w) < ref_size or min(im_h, im_w) > ref_size:
        if im_w >= im_h:
            im_rh = ref_size
            im_rw = int(im_w / im_h * ref_size)
        elif im_w < im_h:
            im_rw = ref_size
            im_rh = int(im_h / im_w * ref_size)
    else:
        im_rh = im_h
        im_rw = im_w

    im_rw = im_rw - im_rw % 32
    im_rh = im_rh - im_rh % 32
    im = F.interpolate(im, size=(im_rh, im_rw), mode='area')

    # inference
    # _, _, matte = modnet(im.cuda(), True)
    _, _, matte = modnet(im, True)

    # resize and save matte
    matte = F.interpolate(matte, size=(im_h, im_w), mode='area')
    matte = matte[0][0].data.cpu().numpy()
    matte_name = im_name.split('.')[0] + '_mask.png'
    Image.fromarray(((matte * 255).astype('uint8')), mode='L').save(os.path.join(output_path, matte_name))

    return matte_name


if __name__ == '__main__':
    get_mask(os.path.join('static/input', 'input2.jpg'), 'static/output')
    print('Done')
