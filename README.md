# ejo_wfb_stabilizer.py

Simple proof-of-concept starter script to stabilize video stream with low latency from wifibroadcast FPV (or any streaming source). 

I put this together because I could not find any ultra low latency software stabilization for FPV. Most stabilization solutions are meant for highly refined post-processing video. The fastest real-time stabilizers that I could find added hundreds of milliseconds latency which is not suitable for FPV. The standard solution to reduce processing time is to reduce the resolution of the frames, run the point-feature matching (or other processing) on the low-res frames, then scale up the translation to the full frame size. Doing this affects accuracy, resulting in a video stream with a minor but frustrating jitter when operating a remote vehicle at high speeds off-road. This stabilizer script differs in that it cuts out a smaller region of interest, finds the points, then adds the appropriate full resolution dimensions to them. It does not downsample the frame and therefore retains the accuracy (mostly).

Requires Python, OpenCV-python, gstreamer

Linux (roughly) - apt install python3 python3-opencv gstreamer1.0-plugins-good

Windows - Install python from the windows app store then open a command prompt and run 'pip install opencv-python'


Included in this repo is a test shaky video UnstabilizedTest10sec.mp4 -- to test just run:

python ejo_wfb_stabilizer.py


More info https://www.rcgroups.com/forums/showthread.php?4320259-Realtime-wifibroadcast-FPV-stabilization-for-off-road-FPV-racing-rovers-robotics
