#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   boat_detect.py    
@Contact :   1435085388@qq.com
@License :   (C)Copyright © 2001-2019 Python Software Foundation。
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/10/29 10:20   MC      3.7.8         None
'''
import cv2 as cv
import time
from datetime import datetime
from boat_counting import count, countAll
from tools import videoProcess, pictureProcess, isUpdate, diffStampToTime

a = time.time()
path = './video/'
video_name1 = 'car.mp4'
video_name2 = 'car2.mp4'
video_path1 = path + video_name1
video_path2 = path + video_name1

def detect():
	camera, bs = videoProcess(video_path1, history=50, epsilon=0.01)
	# camera2, bs2 = videoProcess(video_path2, history=50, epsilon=0.01)


	# 下游(上行)
	temp_DownWait = 0  # 上行等待
	temp_DownOut = 0  # 下行驶出出单行区
	flag_DownWait = 0
	flag_DownOut = 0

	num_DownWait = 0  # 上行等待区该帧船数
	num_DownOut = 0  # 下行驶出单行区当前框内船数
	nums_DownIn_gap = 0
	nums_DownOut_gap = 0
	nums_DownIn = 0  # 上行等待区驶入总数
	nums_DownOut = 0  # 下行驶出单行区总数

	temp_nums_DownIn = 0 #存储上一帧显示的船总数
	temp_nums_DownOut = 0 #

	downStream = [[num_DownWait, temp_DownWait, flag_DownWait], [num_DownOut, temp_DownOut, flag_DownOut]]
	list_gap_out = []
	list_gap_wait = []
	# lastShow_out = -1
	# lastShow_wait = -1
	temp_lastShow_out = 0
	temp_lastShow_wait = 0

	res_num_out = 0  # 记录下游驶出单行区中上一次显示的船数
	temp_res_out = 0  # 即记录上一帧下行驶出区域中的船数
	res_num_wait = 0  # 记录下游等待区上一次显示的船数
	temp_res_wait = 0  # 即记录上一帧上行等待区域中的船数

	# 上游(下行)

	temp_UpWait = 0  # 下行等待
	temp_UpOut = 0  # 上行驶出出单行区
	flag_UpWait = 0
	flag_UpOut = 0

	num_UpWait = 0
	num_UpOut = 0
	nums_UpIn_gap = 0 #一个红绿灯时间内驶入的船数
	nums_UpOut_gap = 0
	nums_UpIn = 0
	nums_UpOut = 0

	temp_nums_UpIn = 0 #保存上一帧显示的船总数
	temp_nums_UpOut = 0

	upStream = [[num_UpWait, temp_UpWait, flag_UpWait], [num_UpOut, temp_UpOut, flag_UpOut]]

	list_gap_out2 = []
	list_gap_wait2 = []
	# lastShow_out2 = -1
	# lastShow_wait2 = -1
	temp_lastShow_out2 = 0
	temp_lastShow_wait2 = 0

	res_num_out2 = 0  # 记录驶出单行区中上一次显示的船数
	temp_res_out2 = 0  # 即记录上一帧上行驶出区域中的船数
	res_num_wait2 = 0  # 记录上游等待区上一次显示的船数
	temp_res_wait2 = 0  # 即记录上一帧下行等待区域中的船数

	#红绿灯
	list_light = ['red', 'green']
	light_Up = list_light[1]  # 初始上游优先
	light_Down = list_light[0]  #初始上游优先

	temp_light_Up = 'red'
	temp_light_Down = 'red'

	flag_light_Up = 0
	flag_light_Down = 0
	i = 0

	import time
	time_start = time.time()
	now = time.time() #保存上一次的开始时间

	flag_time = 1 #1:计时开始，0：停止计时

	while True:
		res, frame = camera.read()
		# res2, frame2 = camera2.read()
		i += 1

		print(i)
		if i == 1174:
			print(i)
			pass
		if not res:
			break
		fg_mask = bs.apply(frame)
		# fg_mask2 = bs2.apply(frame2)
		cv.imshow('fg', fg_mask)
		# cv.imshow('fg2', fg_mask2)
		th, dilated = pictureProcess(fg_mask)
		# th2, dilated2 = pictureProcess(fg_mask2)

		cv.imshow('th', th)
		# cv.imshow('th2', th2)

		# 下游
		# 下游船的使出单行区和等待数量
		x_wait, y_wait, w_wait, h_wait = 1000, 350, 560, 400
		x_out, y_out, w_out, h_out = 440, 350, 560, 400
		# 画出区域框
		cv.rectangle(frame, (x_out, y_out), (x_out + w_out, y_out + h_out), (200, 0, 200), 2)
		cv.rectangle(frame, (x_wait, y_wait), (x_wait + w_wait, y_wait + h_wait), (200, 0, 200), 2)
		frame_wait = dilated[y_wait:y_wait + h_wait, x_wait:x_wait + w_wait]
		frame_out = dilated[y_out:y_out + h_out, x_out:x_out + w_out]
		cv.imshow('frame_wait', frame_wait)
		cv.imshow('frame_out', frame_out)

		# 计算此刻上行等待船数，此刻驶出单行道船数,可信轮廓
		downStream[0][0], contours_wait = count(frame, frame_wait, x_wait, y_wait, w_wait, h_wait)
		downStream[1][0], contours_out = count(frame, frame_out, x_out, y_out, w_out, h_out)  # 下游出来的船【【【】】】

		frame, downStream, \
		res_num_wait, res_num_out, \
		list_gap_wait, list_gap_out, \
		lastShow_wait, lastShow_out = isUpdate(frame, downStream,
											   res_num_wait, res_num_out,
											   contours_wait, contours_out,
											   list_gap_wait, list_gap_out)

		# 计算等待区驶入单行区总数
		nums_DownIn, temp_lastShow_wait, temp_res_wait, list_gap_wait = countAll(nums_DownIn, lastShow_wait,
																			   temp_lastShow_wait,
																			   res_num_wait, temp_res_wait,
																			   list_gap_wait)
		cv.putText(frame, "DownInNums:" + str(nums_DownIn), (1050, 300), cv.FONT_HERSHEY_COMPLEX, 2, (255, 255, 0), 3)
		# 计算放行区驶出船总数
		nums_DownOut, temp_lastShow_out, temp_res_out, list_gap_out = countAll(nums_DownOut, lastShow_out,
																			   temp_lastShow_out,
																			   res_num_out, temp_res_out, list_gap_out)
		cv.putText(frame, "DownOutNums:" + str(nums_DownOut), (400, 300), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)

		# cv.imshow("video", frame)



		# 上游
		# 上游船的使出单行区和等待数量
		# x_wait2, y_wait2, w_wait2, h_wait2 = 1000, 350, 560, 400
		# x_out2, y_out2, w_out2, h_out2 = 440, 350, 560, 400
		# # 画出区域框
		# cv.rectangle(frame2, (x_out2, y_out2), (x_out2 + w_out2, y_out2 + h_out2), (200, 0, 200), 2)
		# cv.rectangle(frame2, (x_wait2, y_wait2), (x_wait2 + w_wait2, y_wait2 + h_wait2), (200, 0, 200), 2)
		# frame_wait2 = dilated2[y_wait2:y_wait2 + h_wait2, x_wait2:x_wait2 + w_wait2]
		# frame_out2 = dilated2[y_out2:y_out2 + h_out2, x_out2:x_out2 + w_out2]
		# cv.imshow('frame_wait2', frame_wait2)
		# cv.imshow('frame_out2', frame_out2)
		#
		# # 计算此刻上行等待船数，此刻驶出单行道船数,可信轮廓
		# upStream[0][0], contours_wait2 = count(frame2, frame_wait2, x_wait2, y_wait2, w_wait2, h_wait2)
		# upStream[1][0], contours_out2 = count(frame2, frame_out2, x_out2, y_out2, w_out2, h_out2)  # 下游出来的船【【【】】】
		#
		# frame2, upStream, \
		# res_num_wait2, res_num_out2, \
		# list_gap_wait2, list_gap_out2, \
		# lastShow_wait2, lastShow_out2 = isUpdate(frame2, upStream,
		# 										 res_num_wait2, res_num_out2,
		# 										 contours_wait2, contours_out2,
		# 										 list_gap_wait2, list_gap_out2)
		#
		# nums_UpIn, temp_lastShow_wait2, temp_res_wait2, list_gap_wait2 = countAll(nums_UpIn, lastShow_wait2,
		# 																			temp_lastShow_wait2, res_num_wait2,
		# 																			temp_res_wait2, list_gap_wait2)
		# cv.putText(frame2, "UpInNums:" + str(nums_UpIn), (1050, 300), cv.FONT_HERSHEY_COMPLEX, 2, (255, 255, 0), 3)
		# nums_UpOut, temp_lastShow_out2, temp_res_out2, list_gap_out2 = countAll(nums_UpOut, lastShow_out2,
		# 																		temp_lastShow_out2, res_num_out2,
		# 																		temp_res_out2, list_gap_out2)
		# cv.putText(frame2, "UpOutNums:" + str(nums_UpOut), (400, 300), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)
		#
		#
		#
		# #判断红绿灯
		# #假设初始单行区没有船，开始为上行优先
		# # a对于下游：
		# #1.开始计时，并计数
		# #2.通行时间为30s，后置下游绿灯-->红灯
		# #3.比较进入单行区的船以及驶出单行区的船，得到在单行区未驶出的船数
		# #4.船全部驶出，后置上游红灯-->绿灯
		# # b对于上游：
		# #计算等待区中的船，若超过某阈值如30艘，告知下游绿灯-->红灯，执行a3~a4
		# # 上下游交替执行以上ab循环
		# #时间开始
		# #如果上游等待数量过多达到30，下游转红灯
		# #
		# if flag_time==1:
		# 	now = time.time()
		# nums_UpIn_gap += nums_UpIn - temp_nums_UpIn
		# nums_UpOut_gap += nums_UpOut - temp_nums_UpOut
		# nums_DownIn_gap += nums_DownIn - temp_nums_DownIn
		# nums_DownOut_gap += nums_DownOut - temp_nums_DownOut
		#
		# temp_nums_UpIn = nums_UpIn
		# temp_nums_UpOut = nums_UpOut
		# temp_nums_DownIn = nums_DownIn
		# temp_nums_DownOut = nums_DownOut
		#
		# 	#都为红灯时，计算驶出船数
		# if light_Up == 'green':
		# 	#最大等待时间更为优先，此处未考虑
		# 	if num_DownWait >= 30 | diffStampToTime(now,time_start) >= 30: #如果下游等待过多,或者时间到了30s
		# 		light_Up = list_light[0] #上游转红灯
		# 		flag_time = 0 #计时停止
		# 		flag_light_Down = 1
		# if light_Down == 'green':
		# 	if num_UpWait >= 30 | diffStampToTime(now,time_start) >= 30: #如果上游等待过多,或者时间到了30s
		# 		light_Down = list_light[0] #下游转红灯
		# 		flag_time = 0  # 计时停止
		# 		flag_light_Up = 1
		#
		# # if light_Up == 'red':
		# #
		# if (nums_UpIn - nums_DownOut <= 0) & (flag_light_Down == 1):
		# 	light_Down = list_light[1] #下游转绿灯
		# 	#重置计数
		# 	nums_DownIn_gap = 0 #下游驶入
		# 	nums_UpOut_gap = 0 #上游驶出
		# 	flag_light_Down = 0
		# 	#下游开始计时
		# 	flag_time = 1
		# 	time_start = time.time() #开始计时
		#
		# if (nums_DownIn-nums_UpOut<=0) & (flag_light_Up == 1):
		# 	light_Up = list_light[1] #上游转绿灯
		# 	#重置计数
		# 	nums_UpIn_gap = 0 #上游驶入
		# 	nums_DownOut_gap = 0 #下游驶出
		# 	flag_light_Up = 0
		# 	#上游开始计时
		# 	flag_time = 1
		# 	time_start = time.time()  # 开始计时
		#
		# cv.putText(frame,'In_gap:'+str(nums_DownIn_gap),(1050,200),cv.FONT_HERSHEY_COMPLEX,2,(255,0,255),3)
		# cv.putText(frame,'Out_gap'+str(nums_DownOut_gap),(400,200),cv.FONT_HERSHEY_COMPLEX,2,(255,0,255),3)
		# cv.putText(frame2, 'In_gap:' + str(nums_UpIn_gap), (1050, 200), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
		# cv.putText(frame2, 'Out_gap' + str(nums_UpOut_gap), (400, 200), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
		#
		# if light_Up == 'red':
		# 	color_up = (0,0,255)
		# else:
		# 	color_up = (0,255,0)
		# if light_Down == 'red':
		# 	color_down = (0,0,255)
		# else:
		# 	color_down = (0,255,0)
		#
		# cv.circle(frame,(200,200),20,color_down,-1)
		# cv.circle(frame2,(200,200),20,color_up,-1)

		cv.imshow("video", frame)
		# cv.imshow("video2", frame2)
		if cv.waitKey(1) & 0xff == 27:
			break
	camera.release()
	# camera2.release()

detect()
