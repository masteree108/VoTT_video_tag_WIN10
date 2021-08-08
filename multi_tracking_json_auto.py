# python ./coding/multi_tracking_excel.py --video ./video/race.mp4 --excel ./Vott_csv_5/Drone_027-export.csv

# import the necessary packages
from imutils.video import VideoStream, FileVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import math
import cv2
import modin.pandas as pd
import os
import psutil
import time
import datetime
import traceback
from numba import jit
import os, json

# this finds our json files


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
ap.add_argument("-j", "--json", type=str,
                help="josn file ")
ap.add_argument("-r", "--rate", type=int,
                help="excel file frame rate")
args = vars(ap.parse_args())

if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
# initialize the FPS throughput estimator

fps = None
fps = FPS().start()
time = None
datetime_dt = datetime.datetime.today()
datetime_format = datetime_dt.strftime('%Y%m%d_%H%M')
path_to_json = os.path.join(args["json"])
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

# loop over frames from the video stream
# create a video exporter
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv2.VideoWriter(str(datetime_format) + '.mp4', fourcc, args["rate"], (3840, 2160))
Rs_time = -1
None_wirte = 0
write_gap = (30 / args['rate']) + 1
df_row = 0
df = pd.DataFrame()

#trans json to a csv file
#
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        try:
            json_text = json.load(json_file)
            # here you need to know the layout of your json and each json has to have
            # the same structure (obviously not the structure I have here)
            for i in range(len(json_text['regions'])):
                for j in range(len(json_text['regions'][i]['tags'])):
                    df.loc[df_row, 0] = json_text['asset']['timestamp']
                    df.loc[df_row, 1] = round(json_text['regions'][i]['boundingBox']['left'])
                    df.loc[df_row, 2] = round(json_text['regions'][i]['boundingBox']['top'])
                    df.loc[df_row, 3] = round(json_text['regions'][i]['boundingBox']['left'])+round(json_text['regions'][i]['boundingBox']['width'])
                    df.loc[df_row, 4] = round(json_text['regions'][i]['boundingBox']['top'])+round(json_text['regions'][i]['boundingBox']['height'])
                    df.loc[df_row, 5] =json_text['regions'][i]['tags'][j]
                    df_row=df_row+1
        except KeyError:
            pass
df.rename(columns={0: 'Time'}, inplace=True)
df.rename(columns={1: 'xmin'}, inplace=True)
df.rename(columns={2: 'ymin'}, inplace=True)
df.rename(columns={3: 'xmax'}, inplace=True)
df.rename(columns={4: 'ymax'}, inplace=True)
df.rename(columns={5: 'label'}, inplace=True)
df.columns = df.columns.str.strip()
print(df)

def compare(time_flag):
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
        xmin = round(time_flag.iloc[i, 1])
        ymin = round(time_flag.iloc[i, 2])
        xmax = round(time_flag.iloc[i, 3])
        ymax = round(time_flag.iloc[i, 4])
        text = format(time_flag.iloc[i, 5])
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

while vs.isOpened():
    video_time = (np.array([vs.get(cv2.CAP_PROP_POS_MSEC)]) / 10) / 100
    print(video_time)
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
    # we need both the json and an index number so use enumerate()
    time_flag = df[round(df['Time'], 1) == (int(video_time * 10)) / 10]
    # only choice compare frame write into mp4
    compare(time_flag)
    if time_flag.shape[0] > 1 and Rs_time != (time_flag.iloc[1, 0]):
        print("有框框")
        out.write(frame)
        Rs_time=time_flag.iloc[1, 0]
        write_gap=0
        None_wirte=0
    elif write_gap>=(30/args['rate'])+1 and  None_wirte % (30 / args['rate']) == 0 :
        print("只有畫面")
        out.write(frame)
        None_wirte=0
    None_wirte += 1
    write_gap += 1
    # only choice compare frame write into mp4
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

# 輸出結果
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
cv2.destroyAllWindows()

# here I define my pandas Dataframe with the columns I want to get from the json
