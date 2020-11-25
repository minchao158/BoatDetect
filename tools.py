#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tools.py
@Contact :   1435085388@qq.com
@License :   (C)Copyright © 2001-2019 Python Software Foundation。
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/10/30 10:18   MC      3.7.8         None
'''
import cv2 as cv
import math

def videoProcess(path,history=500,epsilon=-1):
	"""
	视频处理，得到背景差分模型
	:param path: 视频路径
	:param history: 训练bg减法器所用帧数，默认500
	:param epsillon: 背景更新的学习率，默认-1，即自动更新
	:return:
	camera:视频读取对象
	fg_mask:背景差分模型
	"""
	camera = cv.VideoCapture(path)
	# res,frame = camera.read()
	frames = 0
	#varThreshold:方差阈值，判断当前像素是前景还是背景默认16
	bs = cv.createBackgroundSubtractorMOG2(detectShadows=True) #阴影剔除
	fg_mask = None
	while True:
		res,frame = camera.read()
		if not res:
			break
		frame_gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
		fg_mask = bs.apply(frame_gray,None,epsilon) #epsilon：学习率0-1，0背景不更新，1逐帧更新，默认-1自动更新
		if frames < history:
			frames += 1
			continue
		else:
			break

	return camera,bs

def pictureProcess(fg_mask):
	"""
	图像处理
	:param fg_mask:背景差分图像
	:return: dilated:形态学处理后的图像
	"""
	th = cv.threshold(fg_mask.copy(), 127, 255, cv.THRESH_BINARY)[1]
	# avg = cv.blur(th,ksize=(5,5))
	# avg = cv.threshold(th.copy(), 127, 255, cv.THRESH_BINARY)[1]
	# open = cv.morphologyEx(avg,cv.MORPH_OPEN,(7,7))

	# cv.imshow('th', th)
	dilated = cv.dilate(th, cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 5)), iterations=2)
	(9,9)
	dilated = cv.erode(dilated, cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3)), iterations=2)
	(3,3)

	return th,dilated
	# return th,open

# def isUpdate(frame,wait_num,temp_wait,flag_wait,out_num,temp_out,flag_out):
def isUpdate(frame,stream,res_num1,res_num2,contours1,contours2,list_gap1,list_gap2):
	#res_num当前视频帧显示的数
	last_show1 = -1
	last_show2 = -1
	list_gap1.append(contours1)
	list_gap2.append(contours2)
	# isTheSameBox = False
	if stream[0][0] == stream[0][1]:
	# if wait_num == temp_wait:
		stream[0][2]+=1
		# flag_wait += 1
	else:
		stream[0][2] = 0
	# flag_wait -= 1
	if stream[1][0] == stream[1][1]:
		# if out_num == temp_out:
		# if stream[1][2]>=1 and isSame(contours1,boxs2):
		# 	isTheSameBox = True
		stream[1][2] += 1
		# flag_out += 1
	else:
		stream[1][2] = 0
		# flag_out -= 1
	#计数标记最小为0
	stream[0][2] = max(0,stream[0][2])
	# flag_wait = max(0,flag_wait)
	stream[1][2] = max(0,stream[1][2])
	# flag_out = max(0,flag_out)

	stream[0][1],stream[1][1] = stream[0][0],stream[1][0]#保留上一帧的船数值
	# temp_wait,temp_out = wait_num,out_num

	#如果连续n帧数字不变，则更新船数
	if stream[0][2] ==15:#由于等待区有辆车太大，超出检测框范围，出现检测不到整个框的情况
	# if flag_wait == 59:
		last_show1 = stream[0][0]
		print("上行等待船数为：", stream[0][0])
		# print("上行等待船数为：", wait_num)
		cv.putText(frame, "UpWait:" + str(stream[0][0]), (1100, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 255, 0), 3)
		# cv.putText(frame, "UpWait:" + str(wait_num), (1100, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
		res_num1 = stream[0][0]
		stream[0][2] = 0 # 重置计数标记
		flag_Upwait = 0
	else:
		print("上行等待船数为：", res_num1)
		cv.putText(frame, "UpWait:" + str(res_num1), (1100, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 255, 0), 3)
	if stream[1][2] == 5:
	# if flag_out == 59:
		last_show2 = stream[1][0]
		print('驶出单行区船数为：', stream[1][0])
		# print('驶出单行区船数为：', out_num)
		cv.putText(frame, "DownOut:" + str(stream[1][0]), (550, 100), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)
		# cv.putText(frame, "DownOut:" + str(out_num), (700, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
		res_num2 = stream[1][0]
		stream[1][2] = 0 # 重置计数标记
		# flag_DownOut = 0
	else:
		print('驶出单行区船数为：', res_num2)
		cv.putText(frame, "DownOut:" + str(res_num2), (550, 100), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)
		# res = stream[1][1]
	return frame,stream,res_num1,res_num2,list_gap1,list_gap2,last_show1,last_show2

#计算所有框的质心
def center(contours):
	"""
	计算质心
	:param contours: 轮廓
	:return:
	center_list: 轮廓中每个矩形框的质心构成的列表
	"""
	center_list = []

	if len(contours)<=0:
		return []
	for c in contours:
		x,y,w,h = c
		center = (x+w//2,y+h//2)
		center_list.append(center)
	return center_list #[[],[],[]]

#计算所有框的纵坐标
def center_y(contours):
	y_list = []
	if not contours:
		return y_list
	center_list = center(contours)
	for i in range(len(center_list)):
		y = center_list[i][1]
		y_list.append(y)
	return y_list

#判断是否在车出去的同时会有车进来
def isOtherBoat(contours_gap):
	"""
	判断是否在车出去的同时会有车进来
	:param box1: 前一帧轮廓
	:param box2: 该帧轮廓
	:return: same:判断结果
	"""
	isOther = False
	yy_list = [] #保存所有框质心的y坐标
	if not contours_gap:
		return False
	for boxs in contours_gap: #boxs为每帧的轮廓
		if  boxs:
			y_list = center_y(boxs) #每帧的矩形框质心y坐标构成的列表
			yy_list += y_list
	if len(yy_list) <= 0:
		return isOther
	#获取最大值和最小值
	max_y = max(yy_list)
	min_y = min(yy_list)
	if max_y - min_y > 290:  #设置阈值：两框垂直距离的差超过阈值，说明船进同时有船出
		isOther = True
	return isOther

from datetime import datetime
#将时间戳的差转换为秒
def diffStampToTime(time1,time2):
	seconds = (datetime.fromtimestamp(time2)-datetime.fromtimestamp(time1)).seconds
	return seconds