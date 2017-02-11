import cv2
import sys
import time
import os


if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) != 3:
        sys.stderr.write('usage python basicrecord.py <time-to-record-in-seconds> <path-to-output.avi>')
        sys.exit()

    duration = sys.argv[1]
    output_file = sys.argv[2]
    if os.path.isfile(output_file):
        os.remove(output_file)


    cap = cv2.VideoCapture(0)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    cap.set(5,20)

    out = cv2.VideoWriter(output_file, cv2.cv.CV_FOURCC(*'MJPG'), 20.0, (frame_width, frame_height), True)

    start_time = time.time()
    end_time = start_time + float(duration)

    while time.time() < end_time:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    out.release()
    cap.release()