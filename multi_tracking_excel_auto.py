# python ./coding/multi_tracking_excel.py --video ./video/race.mp4 --excel ./Vott_csv_5/Drone_027-export.csv

# import the necessary packages
from imutils.video import VideoStream, FileVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import math
import cv2
import pandas as pd
import os
import psutil
import time
import datetime
import traceback
from numba import jit

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
ap.add_argument("-e", "--excel", type=str,
                help="Vott export excel file")
ap.add_argument("-r", "--rate", type=int,
                help="excel file frame rate")
args = vars(ap.parse_args())

if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
# initialize the FPS throughput estimator

fps = None
fps = FPS().start()
time = None
datetime_dt = datetime.datetime.today()
datetime_format = datetime_dt.strftime('%Y%m%d_%H%M')

try:
    df = pd.read_csv(args["excel"])
except ValueError:
    print("\033[1;41m  請輸入Vott excel 檔案   \033[0m")
    exit(-1)
# pd.set_option('display.max_rows', 500)
df2 = pd.concat([df['image'].str.split('=', expand=True), df], axis=1).drop('image', axis=1)

# trans lable name
df2.rename(columns={1: 'Time'}, inplace=True)
df2.rename(columns={0: 'File'}, inplace=True)
# str to int (sort is by acsll)
df2['Time'] = pd.to_numeric(df2['Time'])
# df3=df2.sort_values(by=['Time','label'],ascending=True)
df3 = df2
print(df3)

# loop over frames from the video stream
# create a video exporter
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv2.VideoWriter(str(datetime_format) + '.mp4', fourcc, args["rate"], (3840, 2160))
Rs_time = -1
None_wirte = 0
write_gap=7

@jit
def compare(time, time_flag):
    Rs_xmin = 0
    Rs_ymin = 0
    Rs_xmax = 0
    Rs_ymax = 0
    reapeat_counter = 0
    # print video time & wheater write frame to video(True or False)
    # compare time with vott csv file time and show on Terminal
    # print(time_flag)
    # draw vott export file on video
    for i in range(time_flag.shape[0]):
        xmin = round(time_flag.iloc[i, 2])
        ymin = round(time_flag.iloc[i, 3])
        xmax = round(time_flag.iloc[i, 4])
        ymax = round(time_flag.iloc[i, 5])
        text = format(time_flag.iloc[i, 6])
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax),
                      (0, 0, 255), 2)
        # draw label on video
        if Rs_xmin == xmin and Rs_ymin == ymin and Rs_xmax == xmax and Rs_ymax == ymax:
            reapeat_counter += 1
            cv2.putText(frame, text, (xmin, ymin - 25 * reapeat_counter),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else:
            Rs_xmin = xmin
            Rs_ymin = ymin
            Rs_xmax = xmax
            Rs_ymax = ymax
            reapeat_counter = 0
            cv2.putText(frame, text, (xmin, ymin - 25 * reapeat_counter),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        """if time_flag.shape[0]>2:
            if xmin==int(time_flag.iloc[i-2,2]) :
                cv2.putText(frame, text, (xmin, ymin -50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0 , 0 , 255), 3)
            elif xmin==int(time_flag.iloc[i-1,2]) :
                cv2.putText(frame, text, (xmin, ymin -25),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else :
                cv2.putText(frame, text, (xmin , ymin ),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        elif time_flag.shape[0]>1:
            if xmin==int(time_flag.iloc[i-1,2]) :
                cv2.putText(frame, text, (xmin, ymin -25),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else :
                cv2.putText(frame, text, (xmin , ymin ),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else :
            cv2.putText(frame, text, (xmin, ymin),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)"""


while (vs.isOpened()):
    time = ((np.array([vs.get(cv2.CAP_PROP_POS_MSEC)]) / 10)) / 100
    print(time)
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    # check to see if we have reached the end of the stream
    if frame is None:
        break
    # resize the frame (so we can process it faster) and grab the
    # frame dimensions
    frame = imutils.resize(frame, width=3840, height=2160)
    (H, W) = frame.shape[:2]
    fps.update()
    fps.stop()
    # compare function
    time_flag = df3[round(df3['Time'], 1) == (int(time * 10)) / 10]
    # only choice compare frame write into mp4
    compare(time, time_flag)
    if time_flag.shape[0] > 1 and Rs_time != (time_flag.iloc[1, 1]):
        print("有框框")
        out.write(frame)
        Rs_time=time_flag.iloc[1, 1]
        write_gap=0
        None_wirte=0
    elif write_gap>=(30/args['rate'])+1 and  None_wirte % (30 / args['rate']) == 0 :
        print("只有畫面")
        out.write(frame)
        None_wirte=0
    None_wirte+=1
    write_gap+=1
    key = cv2.waitKey(1) & 0xFF
    # key == ord("d"):
# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()
# otherwise, release the file pointer
else:
    vs.release()
    out.release()
# close all windows
cv2.destroyAllWindows()


