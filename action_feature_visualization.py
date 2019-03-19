#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
     # @Time    : 2019-03-16 22:47
     # @Author  : Awiny
     # @Site    :
     # @Project : Action_Video_Visualization
     # @File    : action_feature_visualization.py
     # @Software: PyCharm
     # @Github  : https://github.com/FingerRec
     # @Blog    : http://fingerrec.github.io
"""
import scipy.io
import os
import cv2
from utils import *

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  #close the warning
#i want to do a show video such as openpose, show detection video and label real time, plot the weights of the prediction layer
#plot heat map as well
#this work may be finished in 2-3 days.
class Visualization(object):
    def __init__(self):
        return

    def gen_heatmap(self, cam, frame):
        """
        geneate headmap and focus map from images
        :return:
        """
        # produce heatmap and focusmap for every frame and activation map
        #cam:16x224x224x3 frame:1x3x16x224x224
        for i in range(cam.shape[0]):
            #   Create colourmap
            heatmap = cv2.applyColorMap(np.uint8(255 * cam[i]), cv2.COLORMAP_JET)
            #   Create focus map
            focusmap = np.uint8(255 * cam[i])
            focusmap = cv2.normalize(cam[i], dst=focusmap, alpha=20, beta=255, norm_type=cv2.NORM_MINMAX,
                                     dtype=cv2.CV_8UC1)
            # Create frame with heatmap
            heatframe = heatmap // 2 + frame[0][i] // 2
            #   Create frame with focus map in the alpha channel
            focusframe = frame[0][i]
            focusframe = cv2.cvtColor(np.uint8(focusframe), cv2.COLOR_BGR2BGRA)
            focusframe[:, :, 3] = focusmap

        return heatframe, focusframe

    @staticmethod
    def gen_mask_img(origin_img,  heat_map, pred_top3, prob_top3, label):
        """
        a img will be divide into four parts, origin images, activation_map, heatmap, focusmap
        and add text into them
        may be want to visulization these filters, do it later
        :return:
        """
        h, w, c = origin_img.shape
        x1 = int(round((w - 224) / 2.))
        y1 = int(round((h - 224) / 2.))
        cropped_img = origin_img[y1:(y1 + 224), x1:(x1 + 224), :]
        #focus_crop_img = np.zeros([224, 224, 3])
        #for i in range(3):
        #    focus_crop_img = focus_map[:,:,i] * focus_map[:, :, 3]
        #focus_crop_img = cv2.cvtColor(focus_map, cv2.COLOR_RGBA2RGB)
        #focus_map = np.resize(focus_crop_img, [224,224,3])
        classes = [x.strip() for x in open('resources/classInd.txt')]
        label_name = 'real label: ' + classes[label - 1]
        put_text(cropped_img, label_name, (0.1, 0.5))
        for i in range(3):
            label_text = "  Top {}: label: {}".format(i+1, classes[pred_top3[i]])
            put_text(heat_map[i], label_text, (0.1, 0.5))
            prob_text = "prob: {}".format(str(prob_top3[i])[:7])
            put_text(heat_map[i], prob_text, (0.2, 0.5))
        img0 = np.concatenate((cropped_img, heat_map[0]), axis=1)
        img1 = np.concatenate((heat_map[1], heat_map[2]), axis=1)
        maskimg = np.concatenate((img0, img1), axis=0)
        return maskimg
