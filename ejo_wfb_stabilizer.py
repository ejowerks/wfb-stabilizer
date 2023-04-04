#!/usr/bin/python3
# Author: ejowerks
# Version 0.00000000001 Proof of Concept Released 4/3/2023
# Open Source -- Do what you wanna do
# Thanks to https://github.com/trongphuongpro/videostabilizer 

import cv2
import numpy as np
import time

#################### USER VARS ######################################
# Decreases stabilization latency at the expense of accuracy. Set to 1 if no downsamping is desired. 
# Example: downsample = 0.5 is half resolution and runs faster but gets jittery
downsample = 1.0 

#Zoom in so you don't see the frame bouncing around. zoomFactor = 1 for no zoom
zoomFactor = 1.1

# pV and mV can be increased for more smoothing #### start with pV = 0.01 and mV = 2 
processVar=0.01 
measVar=2

# set to 1 to show the sampled area rectangle 
showSampledArea = 0

# set to 1 to display full screen
showFullScreen = 0

# set to 1 to show unstabilized B&W sampled area in a window
showUnstabilized = 0

# If test video plays too fast then increase this until it looks close enough. Varies with hardware. 
# LEAVE AT 1 if streaming live video from WFB (unless you like a delay in your stream for some weird reason)
delay_time = 1 

######################## Video Source ###############################

# For testing this script there is an unstabilized test file. Comment out if streaming from other sources below
SRC = 'UnstabilizedTest10sec.mp4'

# Your stream source. Requires gstreamer libraries 
# Can be local or another source like a GS RPi
# Check the docs for your wifibroadcast variant and/or the Googles to figure out what to do. 

# Below should work on most PC's with gstreamer installed
#SRC = 'udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false'

# Below is for author's Ubuntu PC with nvidia/cuda stuff running WFB-NG locally (no groundstation RPi). Probably won't work on your computer
#SRC = 'udpsrc port=5600 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" framerate=49/1 ! rtph264depay !  h264parse ! nvh264dec ! videoconvert ! appsink sync=false'

######################################################################



lk_params = dict( winSize  = (15,15),maxLevel = 3,criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
count = 0
a = 0
x = 0
y = 0
Q = np.array([[processVar]*3])
R = np.array([[measVar]*3])
K_collect = []
P_collect = []
prevFrame = None
video = cv2.VideoCapture(SRC)

while True:
	grab, frame = video.read()
	if grab is not True:
		exit() 
	res_w_orig = frame.shape[1]
	res_h_orig = frame.shape[0]
	res_w = int(res_w_orig * downsample)
	res_h = int(res_h_orig * downsample)
	top_left= [int(res_h/4),int(res_w/4)]
	bottom_right = [int(res_h - (res_h/4)),int(res_w - (res_w/4))]
	res_disp_w=int(res_w/2)
	res_disp_h=int(res_h/2)
	frameSize=(res_w,res_h)
	Orig = frame
	frame = cv2.resize(frame, frameSize) # Downsample if applicable
	currFrame = frame
	currGray = cv2.cvtColor(currFrame, cv2.COLOR_BGR2GRAY)
	currGray = currGray[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]  ] #selecting ROI
	if prevFrame is None:
		prevOrig = frame
		prevFrame = frame
		prevGray = currGray
	
	if (grab == True) & (prevFrame is not None):
		if showSampledArea == 1:
			cv2.rectangle(prevOrig,(top_left[1],top_left[0]),(bottom_right[1],bottom_right[0]),color = (255,255,255),thickness = 1)
		# Not in use, save for later
		#gfftmask = np.zeros_like(currGray)
		#gfftmask[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]] = 255
		
		prevPts = cv2.goodFeaturesToTrack(prevGray,maxCorners=200,qualityLevel=0.01,minDistance=30,blockSize=3)
		currPts, status, err = cv2.calcOpticalFlowPyrLK(prevGray,currGray,prevPts,None,**lk_params)
		assert prevPts.shape == currPts.shape
		idx = np.where(status == 1)[0]
		# Add orig video resolution pts to roi pts
		prevPts = prevPts[idx] + np.array([int(res_w_orig/4),int(res_h_orig/4)]) 
		currPts = currPts[idx] + np.array([int(res_w_orig/4),int(res_h_orig/4)])
		m, inliers = cv2.estimateAffinePartial2D(prevPts, currPts)
		if m is None:
			m = lastRigidTransform
		# i like smoothies
		dx = m[0, 2]
		dy = m[1, 2]
		da = np.arctan2(m[1, 0], m[0, 0])
		x += dx
		y += dy
		a += da
		Z = np.array([[x, y, a]], dtype="float")
		if count == 0:
			X_estimate = np.zeros((1,3), dtype="float")
			P_estimate = np.ones((1,3), dtype="float")
		else:
			X_predict = X_estimate
			P_predict = P_estimate + Q
			K = P_predict / (P_predict + R)
			X_estimate = X_predict + K * (Z - X_predict)
			P_estimate = (np.ones((1,3), dtype="float") - K) * P_predict
			K_collect.append(K)
			P_collect.append(P_estimate)
		diff_x = X_estimate[0,0] - x
		diff_y = X_estimate[0,1] - y
		diff_a = X_estimate[0,2] - a
		dx += diff_x
		dy += diff_y
		da += diff_a
		m = np.zeros((2,3), dtype="float")
		m[0,0] = np.cos(da)
		m[0,1] = -np.sin(da)
		m[1,0] = np.sin(da)
		m[1,1] = np.cos(da)
		m[0,2] = dx
		m[1,2] = dy
		fS = cv2.warpAffine(prevOrig, m, (res_w_orig,res_h_orig)) # apply magic stabilizer sauce to frame
		s = fS.shape
		T = cv2.getRotationMatrix2D((s[1]/2, s[0]/2), 0, zoomFactor)
		f_stabilized = cv2.warpAffine(fS, T, (s[1], s[0]))
		window_name=f'Processing:{res_w}x{res_h}'
		cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
		if showFullScreen == 1:
			cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
		cv2.imshow(window_name, f_stabilized)
		if showUnstabilized == 1:
			cv2.imshow("Unstabilized",prevGray)
		if cv2.waitKey(delay_time) & 0xFF == ord('q'):
			break
		
		
		prevOrig = Orig
		prevGray = currGray
		prevFrame = currFrame
		lastRigidTransform = m
		count += 1
	else:
		exit()
 
video.release()
 
cv2.destroyAllWindows()
