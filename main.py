#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
     # @Time    : 2019-03-17 12:55
     # @Author  : Awiny
     # @Site    :
     # @Project : Action_Video_Visualization
     # @File    : main.py
     # @Software: PyCharm
     # @Github  : https://github.com/FingerRec
     # @Blog    : http://fingerrec.github.io
"""
import argparse
from net.mfnet_3d import MFNET_3D
from action_recognition import ActionRecognition
from utils import *
from action_feature_visualization import Visualization

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  #close the warning
os.environ["CUDA_VISIBLE_DEVICES"]='0'

def parse_args():
    parser = argparse.ArgumentParser(description='mfnet-base-parser')
    parser.add_argument("--num_classes", type=int, default=101)
    parser.add_argument("--model_weights", type=str, default='pretrained_model/MFNet3D_UCF-101_Split-1_96.3.pth')
    parser.add_argument("--video", type=str, default='test_videos/v_HeadMassage_g02_c05.avi')
    parser.add_argument("--frames_num", type=int, default=16, help = "the frames num for the network input")
    parser.add_argument("--label", type=int, default=38)
    parser.add_argument("--clip_steps", type=int, default=8)
    parser.add_argument("--output_dir", type=str, default="output")
    return parser.parse_args()
args = parse_args()

def load_model():
    model_ft = MFNET_3D(args.num_classes)
    model_ft = torch.nn.DataParallel(model_ft).cuda()
    checkpoint = torch.load(args.model_weights)
    model_ft.load_state_dict(checkpoint['state_dict'])
    model_ft.cuda()
    model_ft.eval()
    return model_ft

def decode_on_the_fly(self):
    """
    there incule two way to implement decode on the fly
    we need to consider the video at begin and at end
    :return:
    """

def main():
    global args
    reg_net = ActionRecognition(load_model())
    visulaize = Visualization()

    length, width, height = video_frame_count(args.video)
    if length < args.frames_num:
        print("the video's frame num is {}, shorter than {}, will repeat the last frame".format(length, args.frames_num))
    cap = cv2.VideoCapture(args.video)
    #q = queue.Queue(self.frames_num)
    frames = list()
    count = 0
    while count < length:
        ret, frame = cap.read()
        if type(frame) == type(None):
            break
        else:
            frames.append(frame)
    #if video shorter than frames_num, repeat last frame
    while len(frames) < args.frames_num:
        frames.append(frames[length - 1])
    mask_imgs = list()
    for i in range(int(length/args.clip_steps) -1):
        if i < length - args.frames_num:
            reg_imgs = frames[i*args.clip_steps:i*args.clip_steps + args.frames_num]
        else:
            reg_imgs = frames[length - 1 - args.frames_num:length - 1]
        RGB_vid, vid = reg_net.img_process(reg_imgs, args.frames_num)
        cam, pred = reg_net.generate_cam(vid, args.label)
        heat_map, focus_map = visulaize.gen_heatmap(cam, RGB_vid)
        mask_img = visulaize.gen_mask_img(RGB_vid[0][0], heat_map, heat_map, focus_map)
        mask_imgs.append(mask_img)
        print("precoss video clips: {}/{}, wait a moment".format(i+1, int(length/args.clip_steps)-1))
    saved_video_path = save_as_video(args.output_dir, mask_imgs, args.label)
    saved_image_path = save_as_imgs(args.output_dir, mask_imgs, int(length/args.clip_steps)-1, args.label)
    #visualization(saved_video_path)


if __name__ == '__main__':
    main()