import cv2
import numpy as np
import time
import requests
import sys
import state

video_stream = 'http://169.254.225.251:8080/stream/video.mjpeg'
minimum_area = 8000


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


if __name__ == '__main__':

    cap = cv2.VideoCapture(video_stream)
    # cap = cv2.VideoCapture('/home/brianzhao/Code/hackpoly-parking/moving-car.mp4')
    bg_subtract = cv2.BackgroundSubtractorMOG()

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    framerate = cap.get(5)

    small_kernel = np.ones((5, 5), np.uint8)
    kernel = np.ones((10, 10), np.uint8)

    base_frame = None

    for i in range(50):
        ret, frame = cap.read()
        if not ret:
            continue

        if base_frame is None:
            base_frame = frame
        else:
            base_frame = cv2.addWeighted(base_frame, 0.50, frame, 0.50, 0)

    base_frame = cv2.cvtColor(base_frame, cv2.COLOR_BGR2GRAY)
    base_frame = cv2.GaussianBlur(base_frame, (5, 5), 0)
    print 'done creating baseline'

    middle_line_left = (0, base_frame.shape[0] / 2)
    middle_line_right = (base_frame.shape[1], base_frame.shape[0] / 2)
    center_y_of_camera = base_frame.shape[0] / 2

    # # Setup SimpleBlobDetector parameters.
    # params = cv2.SimpleBlobDetector_Params()
    #
    # # Change thresholds
    # params.minThreshold = 0
    # params.maxThreshold = 9999
    #
    # # Filter by Area.
    # params.filterByArea = True
    # params.minArea = 1500
    #
    # # Filter by Circularity
    # params.filterByCircularity = True
    # params.minCircularity = 0.1
    #
    # # Filter by Convexity
    # params.filterByConvexity = True
    # params.minConvexity = 0.87
    #
    # # Filter by Inertia
    # params.filterByInertia = True
    # params.minInertiaRatio = 0.01
    #
    # # Create a detector with the parameters
    # detector = cv2.SimpleBlobDetector(params)


    start_time = time.time()
    previous_blobs = []
    # count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # count+=1
        # print 'fps: ', count/float(time.time()-start_time)
        # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        original_frame = frame.copy()
        cv2.rectangle(original_frame, middle_line_left, middle_line_right, (0, 0, 255), thickness=5)

        frame = cv2.GaussianBlur(frame, (5, 5), 2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = bg_subtract.apply(frame, learningRate=0.0001)
        # frame = cv2.subtract(changed_frame,base_frame)
        # ret,frame = cv2.threshold(frame,10,255,cv2.THRESH_BINARY)

        # frame = cv2.erode(frame,small_kernel, iterations=1)
        frame = cv2.dilate(frame, kernel, iterations=3)
        frame = cv2.dilate(frame, small_kernel, iterations=1)
        # frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
        # keypoints = detector.detect(frame)


        contours, hierarchy = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # original_frame = cv2.drawKeypoints(frame, keypoints, np.array([]), 255,
        #                           cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        potential_cars = filter(lambda contour: cv2.contourArea(contour) > minimum_area, contours)

        new_blobs = []
        for new_blob in potential_cars:
            x, y, w, h = cv2.boundingRect(new_blob)
            center_y = y + (h / 2)
            center_x = x + (w / 2)
            # cv2.rectangle(original_frame, (x, y), (x + w, y+h), 255, 2)
            new_blobs.append(state.Blob(center_x, center_y, w, h, cv2.contourArea(new_blob)))

        # merge blobs
        to_delete = set()
        new_blobs.sort(key=lambda blob: blob.area, reverse=True)
        for new_blob in new_blobs:
            if new_blob not in to_delete:
                for new_blob_1 in new_blobs:
                    if new_blob_1 not in to_delete and new_blob_1 is not new_blob and \
                            new_blob.close_to(new_blob_1):
                        new_blob.merge(new_blob_1)
                        # print 'merge occurred'
                        to_delete.add(new_blob_1)

        for new_blob in to_delete:
            # print 'deleted stuff'
            new_blobs.remove(new_blob)

        for new_blob in new_blobs:
            cv2.rectangle(original_frame, (int(new_blob.x - new_blob.w/2), int(new_blob.y - new_blob.h/2)),
                          (int(new_blob.x + new_blob.w/2), int(new_blob.y + new_blob.h/2)), 255, 2)

        # numBeforeTop = len(filter(lambda blob: blob.centroid[1] < center_y_of_camera,previous_blobs))
        # numBeforeBottom = len(previous_blobs) - numBeforeTop
        #
        # numAfterTop = len(filter(lambda blob: blob.centroid[1] < center_y_of_camera,new_blobs))
        # numAfterBottom = len(new_blobs) - numAfterTop
        #
        # numLeft = numAfterTop - numBeforeTop
        # numEntered = numAfterBottom - numBeforeBottom
        # total = numEntered - numLeft
        # if total != 0:
        #     print total, 'cars entered'
        #     print requests.post('http://10.110.165.48:9000/lots', json={'lot': 'J', 'diff': total})
        # previous_blobs = new_blobs

        # todo fix this, wrong assumption

        for new_blob in new_blobs:
            if len(previous_blobs) != 0:
                closest_previous_blob = previous_blobs[0]
                dist = new_blob.dist(closest_previous_blob)
                for previous_blob in previous_blobs[1:]:
                    new_dist = previous_blob.dist(new_blob)
                    if new_dist < dist:
                        dist = new_dist
                        closest_previous_blob = previous_blob
                previous_blobs.remove(closest_previous_blob)
                if closest_previous_blob.y < center_y_of_camera and new_blob.y > center_y_of_camera:
                    print 'car entered parking lot!'
                    print requests.post('http://10.110.165.48:9000/lots', json={'lot': 'J', 'diff': 1})
                elif closest_previous_blob.y > center_y_of_camera and new_blob.y < center_y_of_camera:
                    print 'car left parking lot!'
                    print requests.post('http://10.110.165.48:9000/lots', json={'lot': 'J', 'diff': -1})

        previous_blobs = new_blobs

        cv2.imshow('original', original_frame)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    cap.release()
