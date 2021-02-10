import time
import cv2
import numpy
import math
from itertools import combinations
from centroidtracker import CentroidTracker
from FPSViewer import FPSViewer
from TrackingLine import TrackingLine
from SoundPlayer import SoundPlayer


class PreventionDetectors:

    # Import models on the Net, so load our serialized model from disk.
    detector = cv2.dnn.readNetFromCaffe(prototxt="model/generic object detection model/MobileNetSSD_deploy.prototxt",
                                        caffeModel="model/generic object detection model/MobileNetSSD_deploy.caffemodel")

    # Comment the following two line of code if you are not using OpenVINO! OpenVINO is a free toolkit facilitating the optimization of a deep learning model, dedicated to Intel CPU.
    #detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
    #detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # You can change CPU with GPU if you have that.

    # initialize the list of class labels MobileNet SSD was trained to detect.
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]

    tracker = CentroidTracker(maxDisappeared=20, maxDistance=90)  # "maxDisappeared" is the number of frame that the tracker wait before delete the ID of a person if leave the camera view.

    gathering_info = dict()


    # Function that apply the "non max supression" algorithm.
    @staticmethod
    def __non_max_suppression_fast(boxes, overlapThresh):
        try:
            if len(boxes) == 0:
                return []

            if boxes.dtype.kind == "i":
                boxes = boxes.astype("float")

            pick = []

            x1 = boxes[:, 0]
            y1 = boxes[:, 1]
            x2 = boxes[:, 2]
            y2 = boxes[:, 3]

            area = (x2 - x1 + 1) * (y2 - y1 + 1)
            idxs = numpy.argsort(y2)

            while len(idxs) > 0:
                last = len(idxs) - 1
                i = idxs[last]
                pick.append(i)

                xx1 = numpy.maximum(x1[i], x1[idxs[:last]])
                yy1 = numpy.maximum(y1[i], y1[idxs[:last]])
                xx2 = numpy.minimum(x2[i], x2[idxs[:last]])
                yy2 = numpy.minimum(y2[i], y2[idxs[:last]])

                w = numpy.maximum(0, xx2 - xx1 + 1)
                h = numpy.maximum(0, yy2 - yy1 + 1)

                overlap = (w * h) / area[idxs[:last]]

                idxs = numpy.delete(idxs, numpy.concatenate(([last],
                                                             numpy.where(overlap > overlapThresh)[0])))

            return boxes[pick].astype("int")
        except Exception as e:
            print("Exception occurred in non_max_suppression : {}".format(e))

    @staticmethod
    def reset():
        PreventionDetectors.gathering_info.clear()
        PreventionDetectors.tracker.reset_tracker()
        TrackingLine.persons_id_list.clear()
        TrackingLine.centroids_dict.clear()
        TrackingLine.tracklines_colors.clear()

    @staticmethod
    def detect(frame, detect_gathering, detect_social_distancing, enable_sound, report_people_limit, show_tracking_line, show_people_ID, shows_confidence_percentage, MIN_CONFIDENCE, MAX_PERSONS, MIN_DISTANCE, TIME_LIMIT, log_name_file):
        (height, width) = frame.shape[:2]

        # Make a blob to every frame in the video. OpenCV’s new deep neural network (dnn) module contains a function that can be used for preprocessing images and preparing them for classification via pre-trained deep learning models. This function is used to make a "mean image" with a mean subtraction.
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (width, height), 127.5)  # The second argument is used like scalefactor for the image, the last one is subtracted at RGB channels.

        # Pass the blob through the network and obtain the detections and predictions.
        PreventionDetectors.detector.setInput(blob)
        all_detections = PreventionDetectors.detector.forward()

        rectangles = []

        # loop over the detections
        for i in numpy.arange(0, all_detections.shape[2]):  # numpy.arange is equivalent to the Python built-in range function, but returns an ndarray rather than a list.
            confidence = all_detections[0, 0, i, 2]  # extract the confidence associated with the prediction.

            if confidence > MIN_CONFIDENCE:  # 0.5 is the minimum confidence threshold.

                # extract the index of the class label from the `all_detections`, then compute the coordinates of the bounding box for the object.
                index = int(all_detections[0, 0, i, 1])

                if PreventionDetectors.CLASSES[index] == "person":
                    person_box = all_detections[0, 0, i, 3:7] * numpy.array([width, height, width, height])
                    (startX, startY, endX, endY) = person_box.astype("int")  # "astype()" method convert the input into the type written in parentheses.

                    # Print the percentage of confidence
                    if shows_confidence_percentage:
                        info = "{}: {:.2f}%".format(PreventionDetectors.CLASSES[index], confidence * 100)
                        cv2.putText(frame, info, (startX, startY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    # cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)  # Uncomment to see noises in blue.

                    rectangles.append(person_box)  # "rectangles" contains all the cordinates of the persons bounding box.

        boundingboxes = numpy.array(rectangles)
        boundingboxes = boundingboxes.astype("int")
        rectangles = PreventionDetectors.__non_max_suppression_fast(boundingboxes, 0.3)  # Now "rectangles" contains the correct bounding boxes without noises. For "noises" it means every rectangle finded of the same subject (just persons in this case) with different percentage of confidence. "non_max_suppression_fast" function find just the rectangle with the highest confidence and delete the others, this for all the subjects in the camera view. The name of the algorithm derives from the rectangle with the most high confidence, suppressed by many other rectangles with a low confidence ot he same subject, so "NON" max (confidence) suppression.
        # P.S. 0.3 is the threashold.

        persons_centroid = dict()

        subjects = PreventionDetectors.tracker.update(rectangles)  # "subjects" contains the persons ID and the relative bounding box.

        TrackingLine.generate_trackingline_colours(subjects)

        for (personID, boundingbox) in subjects.items():
            x1, y1, x2, y2 = boundingbox
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            # Calculate the coordinates of the center of every person and save it on a python dictionary. This coordinates will be used to detect social distancing.
            centroidX = int((x1 + x2) / 2.0)
            centroidY = int((y1 + y2) / 2.0)

            if show_tracking_line:  # print tracking line
                TrackingLine.generate_trackingline(frame, personID, centroidX, centroidY)

            persons_centroid[personID] = (centroidX, centroidY, x1, y1, x2, y2)

            # Print people's ID
            if show_people_ID:
                info = "ID: {}".format(personID)
                cv2.putText(frame, info, (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        red_zone_list = []  # The list of people too close to each other, so that violate the social distance.

        if detect_social_distancing or detect_gathering:
            for (personID1, data1), (personID2, data2) in combinations(persons_centroid.items(), 2):  # The "combinations()" method match every person in the dictionary 2 per time, so if I have 3 person the matchs are: 0 1, 0 2, 1 2.
                dx, dy = data1[0] - data2[0], data1[1] - data2[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < MIN_DISTANCE:  # 70.0 is the minimum social distance threshold.
                    if personID1 not in red_zone_list:
                        red_zone_list.append(personID1)

                    if personID2 not in red_zone_list:
                        red_zone_list.append(personID2)

                    if personID1 not in PreventionDetectors.gathering_info:
                        PreventionDetectors.gathering_info[personID1] = [time.time(), time.time(), 1]
                    elif personID1 in PreventionDetectors.gathering_info:
                        PreventionDetectors.gathering_info[personID1][1] = time.time()

                    if personID2 not in PreventionDetectors.gathering_info:
                        PreventionDetectors.gathering_info[personID2] = [time.time(), time.time(), 1]
                    elif personID2 in PreventionDetectors.gathering_info:
                        PreventionDetectors.gathering_info[personID2][1] = time.time()

                    cv2.line(frame, (data1[0], data1[1]), (data2[0], data2[1]), (0, 150, 255), 2)  # Draw the line between to person too close to each other.


            # handle delay before pop a person from gathering_info dictionary
            for (personID1, data1), (personID2, data2) in combinations(persons_centroid.items(), 2):

                if personID1 not in red_zone_list and personID1 in PreventionDetectors.gathering_info and PreventionDetectors.gathering_info[personID1][2] >= FPSViewer.fps*3:
                    PreventionDetectors.gathering_info.pop(personID1)
                elif personID1 not in red_zone_list and personID1 in PreventionDetectors.gathering_info:
                    PreventionDetectors.gathering_info[personID1][2] += 1
                elif personID1 in red_zone_list and personID1 in PreventionDetectors.gathering_info and PreventionDetectors.gathering_info[personID1][2] != 1:
                    PreventionDetectors.gathering_info[personID1][2] = 1

                if personID2 not in red_zone_list and personID2 in PreventionDetectors.gathering_info and PreventionDetectors.gathering_info[personID2][2] >= FPSViewer.fps*3:
                    PreventionDetectors.gathering_info.pop(personID2)
                elif personID2 not in red_zone_list and personID2 in PreventionDetectors.gathering_info:
                    PreventionDetectors.gathering_info[personID2][2] += 1
                elif personID2 in red_zone_list and personID2 in PreventionDetectors.gathering_info and PreventionDetectors.gathering_info[personID2][2] != 1:
                    PreventionDetectors.gathering_info[personID2][2] = 1


        # The remaining lines code draws the rectangles for each person, the warning texts, generate the log file and play sound.

        gathering_detected = False

        for (personID, data) in persons_centroid.items():
            if personID in red_zone_list and not detect_gathering:
                cv2.rectangle(frame, (data[2], data[3]), (data[4], data[5]), (0, 0, 255), 2)

                with open("output/" + log_name_file + ".txt", "a") as file:
                    file.write("PERSON ID " + str(personID) + "   -   " + "(X: " + str(data[0]) + ", Y: " + str(data[1]) + ")   -   " + str(time.ctime()) + "          WARNING!" + "\n")

            elif personID in red_zone_list and detect_gathering and PreventionDetectors.gathering_info[personID][1] - PreventionDetectors.gathering_info[personID][0] > TIME_LIMIT:
                cv2.rectangle(frame, (data[2], data[3]), (data[4], data[5]), (0, 0, 255), 2)
                gathering_detected = True

                with open("output/" + log_name_file + ".txt", "a") as file:
                    file.write("PERSON ID " + str(personID) + "   -   " + "(X: " + str(data[0]) + ", Y: " + str(data[1]) + ")   -   " + str(time.ctime()) + "          WARNING!" + "\n")

            else:
                cv2.rectangle(frame, (data[2], data[3]), (data[4], data[5]), (0, 255, 0), 2)

                with open("output/" + log_name_file + ".txt", "a") as file:
                    file.write("PERSON ID " + str(personID) + "   -   " + "(X: " + str(data[0]) + ", Y: " + str(data[1]) + ")   -   " + str(time.ctime()) + "\n")

        people_limit_exceeded = False
        social_distance_violated = False
        persons_count = len(subjects)
        printable_persons_count = "People count: {}".format(persons_count)
        if report_people_limit and persons_count < MAX_PERSONS:
            cv2.putText(frame, printable_persons_count, (20, 40), cv2.FONT_ITALIC, 0.5, (0, 255, 0), 1)
        elif report_people_limit and persons_count >= MAX_PERSONS:
            people_limit_exceeded = True
            cv2.putText(frame, printable_persons_count, (20, 40), cv2.FONT_ITALIC, 0.5, (0, 0, 255), 1)
            cv2.putText(frame, "MAXIMUM NUMBER OF PEOPLE EXCEEDED!", (20, 60), cv2.FONT_ITALIC, 0.5, (0, 0, 255), 1)
        else:
            cv2.putText(frame, printable_persons_count, (20, 40), cv2.FONT_ITALIC, 0.5, (0, 255, 0), 1)

        if gathering_detected:
            cv2.putText(frame, "GATHERING DETECTED!", (20, 80), cv2.FONT_ITALIC, 0.5, (0, 0, 255), 1)

        if red_zone_list and detect_social_distancing:  # If "red_zone_list" is not empty, someone violated the social distance.
            social_distance_violated = True
            cv2.putText(frame, "SOCIAL DISTANCE VIOLATED!", (20, 100), cv2.FONT_ITALIC, 0.5, (0, 0, 255), 1)


        if enable_sound and (people_limit_exceeded or social_distance_violated or gathering_detected):
            SoundPlayer.playWarning()
        else:
            SoundPlayer.stopWarning()
