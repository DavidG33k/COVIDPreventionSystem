import cv2
from collections import defaultdict
from random import randint

class TrackingLine:

    centroids_dict = defaultdict(list)
    persons_id_list = []
    tracklines_delay_before_append = 0
    tracklines_colors = dict()

    @staticmethod
    def generate_trackingline_colours(subjects):

        # generate a random colour for each person's tracking line.
        for (personID, _) in subjects.items():
            if personID not in TrackingLine.tracklines_colors:
                TrackingLine.tracklines_colors[personID] = ((randint(0, 255), randint(0, 255), randint(0, 255)))

    @staticmethod
    def generate_trackingline(frame, personID, centroidX, centroidY):

        cv2.circle(frame, (centroidX, centroidY), 4, TrackingLine.tracklines_colors[personID], -1)

        TrackingLine.tracklines_delay_before_append += 1
        if TrackingLine.tracklines_delay_before_append > 10:  # Just a delay before append the centroids of the people
            TrackingLine.centroids_dict[personID].append((centroidX, centroidY))
            TrackingLine.tracklines_delay_before_append = 0

        if personID not in TrackingLine.persons_id_list:
            TrackingLine.persons_id_list.append(personID)
            cv2.line(frame, (centroidX, centroidY), (centroidX, centroidY),
                     TrackingLine.tracklines_colors[personID], 2)
        else:
            for i in range(len(TrackingLine.centroids_dict[personID])):
                if not i + 1 == len(TrackingLine.centroids_dict[personID]):
                    start_line = (TrackingLine.centroids_dict[personID][i][0],
                                  TrackingLine.centroids_dict[personID][i][1])
                    end_line = (TrackingLine.centroids_dict[personID][i + 1][0],
                                TrackingLine.centroids_dict[personID][i + 1][1])
                    cv2.line(frame, start_line, end_line, TrackingLine.tracklines_colors[personID], 2)

        if len(TrackingLine.centroids_dict[personID]) > 5:  # max lenght of tracklines
            TrackingLine.centroids_dict[personID].pop(0)
