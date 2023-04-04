# ejo_wfb_stabilizer.py

Demo: https://youtu.be/lo-eb6zSxgQ

Simple proof-of-concept starter script to stabilize video stream with low latency from wifibroadcast FPV (or any streaming source). Works sufficiently well with 720p and lower digital FPV video streams. This is not meant to be a high-quality stabilizer as it is designed to make a jittery/bumpy FPV feed tolerable and useable while adding the least possible amount of latency to the stream.

About: I put this together because I could not find any ultra low latency software stabilization for FPV. Most video stabilization solutions are designed for post-processing video files, and the fastest live-streaming stabilizers that I could find added hundreds of milliseconds latency at best which is not suitable for FPV. The usual common solution to reduce frame processing time is to downsample the resolution of the frames, run the point-feature matching (or other processing) on the low-res frames, then scale up the translation to the full frame size. Using this downsample method works but it affects the stabilizer's accuracy, resulting in a video stream with a noticable jitter when operating a remote vehicle at high speeds off-road. The simple method employed in this script differs in that it cuts out a region of interest (ROI), and remaps each point feature coordinate found in the ROI to the appropriate full sized location before further processing and smoothing. It does not downsample and therefore retains the same  stabilization accuracy as a full sized frameset, resulting in a smooth low-latency stabilzed video stream.


Requires Python, OpenCV-python, gstreamer and probably other libraries I forgot about

Linux (roughly) - apt install python3 python3-opencv gstreamer1.0-plugins-* 

Windows - Install python from the windows app store then open a command prompt and run 'pip install opencv-python'


Included in this repo is a test shaky video. To test run:

python ejo_wfb_stabilizer.py UnstabilizedTest10sec.mp4 

...or edit the file and set the SRC variable to your own streaming source. 
