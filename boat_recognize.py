#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   boat_recognize.py    
@Contact :   1435085388@qq.com
@License :   (C)Copyright © 2001-2019 Python Software Foundation。
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/10/27 12:17   MC      3.7.8         None
'''

def overlap(box1, box2):
    """
    检查两个矩形框的重叠程度.
    """
    endx = max(box1[0] + box1[2], box2[0] + box2[2])
    startx = min(box1[0], box2[0])
    width = box1[2] + box2[2] - (endx - startx)

    endy = max(box1[1] + box1[3], box2[1] + box2[3])
    starty = min(box1[1], box2[1])
    height = box1[3] + box2[3] - (endy - starty)

    if (width <= 0 or height <= 0):
        return 0
    else:
        Area = width * height
        Area1 = box1[2] * box1[3]
        Area2 = box2[2] * box2[3]
        ratio = Area / (Area1 + Area2 - Area)

        return ratio

#检查是否接近帧边界，
# if track_list:
#     tlist = copy.copy(track_list)
#         for e in tlist:
#             x, y = e.center
#             if 10 < x < x_size - 10 and 10 < y < y_size - 10:
#                 e.update(frame)
#             else:
#                 track_list.remove(e)