# import cv2
# import numpy as np
#
# # 第一步：使用cv2.VideoCapture读取视频
# cap = cv2.VideoCapture('car.mp4')
# # 第二步：cv2.getStructuringElement构造形态学使用的kernel
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# # 第三步：构造高斯混合模型
# model = cv2.createBackgroundSubtractorMOG2()
#
# while (True):
# 	# 第四步：读取视频中的图片，并使用高斯模型进行拟合
# 	ret, frame = cap.read()
# 	# 运用高斯模型进行拟合，在两个标准差内设置为0，在两个标准差外设置为255
# 	fgmk = model.apply(frame)
# 	# 第五步：使用形态学的开运算做背景的去除
# 	fgmk = cv2.morphologyEx(fgmk, cv2.MORPH_OPEN, kernel)
# 	# 第六步：cv2.findContours计算fgmk的轮廓
# 	contours,hira = cv2.findContours(fgmk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# 	for c in contours:
# 		if cv2.contourArea(c)<10000:
# 			continue
# 		# 第七步：进行人的轮廓判断，使用周长，符合条件的画出外接矩阵的方格
# 		length = cv2.arcLength(c, True)
#
# 		if length > 188:
# 			(x, y, w, h) = cv2.boundingRect(c)
# 			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
# 	# 第八步：进行图片的展示
# 	cv2.imshow('fgmk', fgmk)
# 	cv2.imshow('frame', frame)
#
# 	if cv2.waitKey(150) & 0xff == 27:
# 		break
#
# cap.release()
# cv2.destroyAllWindows()

# a = [0,2,0,1]
# #将列表中的元素元组化
# print(list(enumerate(a)))

# 几种背景差分方法
import cv2 as cv
def bgDiff(path, method='MOG2'):
	def default():
		return None
	camera = cv.VideoCapture(path)
	switch = {
		# 'MOG':cv.createBackgroundSubtractorMOG(),
		'MOG2':cv.createBackgroundSubtractorMOG2(),
		'KNN':cv.createBackgroundSubtractorKNN(),
		# 'GMG':cv.createBackgroundSubtractorGMG() 已过时
	}
	model = switch.get(method,default)
	if not model:
		return
	model = cv.createBackgroundSubtractorMOG2(detectShadows=True)
	frames = 0
	history = 50
	while True:
		res, frame = camera.read()
		if not res:
			break
		frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
		bg_mask = model.apply(frame_gray)
		if frames < history:
			frames += 1
			continue
		th = cv.threshold(bg_mask.copy(),127,255,cv.THRESH_BINARY)[1]
		# median = cv.medianBlur(th,5)
		# cv.imshow('median',median)

		avg = cv.blur(th,ksize=(5,5))
		avg = cv.threshold(th.copy(),127,255,cv.THRESH_BINARY)[1]

		cv.imshow('avg',avg)
		open = cv.morphologyEx(avg,cv.MORPH_OPEN,(7,7))
		cv.imshow('open',open)

		cv.imshow('mog2', bg_mask)

		if cv.waitKey(1) & 0xff == 27:
			break
	camera.release()

# bgDiff('car.mp4',method='KNN')
bgDiff('car.mp4')