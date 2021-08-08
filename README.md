# NTUT_for VOTT export file trans to a video #


In VOTT can generate CSV or JSON files, but these files can not be converted into a movie for easy viewing and inspection, through the following program can convert VOTT export file into a movie


## multi_tracking_excel_auto.py 


In this program, the corresponding time will be searched from the EXPORT CSV to mark on the screen, and produce a movie of the time the program is currently running

The execution instructions of the program are as follows:


python ./coding/multi_tracking_excel_auto.py --video ./video/race.mp4 --excel ./Vott_csv_5/Drone_027-export.csv

`--video` The movie user want export

`--excel` The vott export csv file 


## multi_tracking_json_auto.py

In this program, the corresponding time will be searched from the EXPORT Json to mark on the screen, and produce a movie of the time the program is currently running

The execution instructions of the program are as follows:


python ./coding/multi_tracking_json_auto.py --video ./video/race.mp4 --json ./Drone/Drone_001

`--video` The movie user want export

`--excel` The vott export json file 