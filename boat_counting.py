#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   boat_counting.py    
@Contact :   1435085388@qq.com
@License :   (C)Copyright © 2001-2019 Python Software Foundation。
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/10/27 12:16   MC      3.7.8         None
'''
import cv2 as cv
from boat_recognize import overlap
from tools import isOtherBoat


path = './video/'
video_name='car.mp4'
video_path = path+video_name
track_list=[] #跟踪对象

def count(frame,mask,x,y,w,h):
	"""
	轮船计数(test：右，左)
	:param frame: 原始帧
	:param fg_mask:
	:param x,y: 坐标轴上的x,y
	:param w,h: 所选区域宽高
	:return:
	num: 船数
	contours_out: 可信轮廓
	"""
	# frame_wait = frame[]
	frame_out = mask
	contours_out, hierachy = cv.findContours(frame_out, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	SQUARE = 12000
	#目前区域内最小的车面积为163x138
	num = 0
	boxs = []

	# 计算驶出单行区船数 Out_num
	if len(contours_out)>0:
		x0,y0,w0,h0 = 0,0,1,1
		# temp_c = contours_out[0]  # 看作临时变量，保留上一个计数的框，舍去重合干扰框
		for c in contours_out:
			if cv.contourArea(c) > SQUARE:  # 过滤噪声
				x1, y1, w1, h1 = cv.boundingRect(c)
				if w1<75 | h1>370:
					continue
				roi = overlap((x1,y1,w1,h1), (x0,y0,w0,h0))  # 计算重叠程度
				# roi = overlap((x, y, w, h), get_xywh(frame_out))  # 计算与图像外框重叠程度
				if roi > 0.2:  # 设置阈值，与前一个被计数的框相比，两框高度重叠，则舍弃
					pass
				else:
					x0, y0, w0, h0 = x1,y1,w1,h1  	#记录前一个被计数的框
					num += 1
					# x1,y1,w1,h1 = get_xywh(frame_out)
					cv.rectangle(frame[y:y+h,x:x+w],(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
					# contours.append(c)
					boxs.append([x1,y1,w1,h1])
					# cv.drawContours(frame[300:700,:960],[[[(x,y),(x+w,y+h)]]],-1,(255,0,0),2)
	return num,boxs

def countAll(nums,showNum,temp_showNum,resNum,temp_resNum,list_gap):
	"""
	计算船总数
	:param nums: 船总数
	:param showNum: 区域内该帧显示的船数（首次更新的值）
	:param temp_showNum: 区域内上一帧显示的船数（首次更新的值）
	:param resNum: 区域内该帧显示的船数
	:param temp_resNum: 区域内上一帧显示的船数
	:param list_gap:保存相邻两次更新值区间内的所有帧
	:return:
	"""
	#判断区域某几帧内是否同时有船进和出
	if temp_showNum == showNum: #相邻两次显示船数相同，可能存在同时进出的船，进一步判断
		isOther = isOtherBoat(list_gap) #进行质心纵坐标的比较
		if isOther:
			nums += 1
	if showNum != -1:  #只要更新船数，list重置
		temp_showNum = showNum
		list_gap = []
	diff = resNum - temp_resNum  #相邻两帧显示的船数差
	if diff>0:
		nums += diff  #差值即视为新增船数
	temp_resNum = resNum  #保留上一帧显示的船数
	return nums,temp_showNum,temp_resNum,list_gap


#获得窗口的坐标信息x,y,w,h
def get_xywh(frame):
	if len(frame.shape) != 2:
		return
	return 0,0,frame.shape[0],frame.shape[1]