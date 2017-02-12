import cv2
import numpy as np

video_stream = 'http://10.10.0.83:8080/stream/video.mjpeg'


if __name__ == '__main__':

    cap = cv2.VideoCapture(video_stream)
    bg_subtract = cv2.BackgroundSubtractorMOG()

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    framerate = cap.get(5)

    kernel = np.ones((5,5), np.uint8)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (5,5), 0)
        frame = bg_subtract.apply(frame, learningRate=0.0001)

        cv2.imshow('frame', frame)
        if cv2.waitKey(22) & 0xff == ord('q'):
            break


    cap.release()