import datetime
import cv2


class FPSViewer:

    fps_start_time = datetime.datetime.now()
    fps = 0
    frames_count = 0

    @staticmethod
    def calculate_fps():
        FPSViewer.frames_count += 1
        fps_end_time = datetime.datetime.now()
        time_difference = fps_end_time - FPSViewer.fps_start_time

        if time_difference.seconds != 0:  # To avoid division by zero!
            FPSViewer.fps = (FPSViewer.frames_count / time_difference.seconds)

    @staticmethod
    def show_fps(frame):
        printable_fps = "FPS: {:.2f}".format(FPSViewer.fps)
        cv2.putText(frame, printable_fps, (20, 20), cv2.FONT_ITALIC, 0.5, (0, 0, 0), 2)

    @staticmethod
    def reset():
        FPSViewer.fps_start_time = datetime.datetime.now()
        FPSViewer.fps = 0
        FPSViewer.frames_count = 0
