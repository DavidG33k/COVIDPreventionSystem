import time
import cv2


class FPSViewer:

    prev_frame_time = 0
    new_frame_time = 0
    fps = 0

    @staticmethod
    def calculate_fps():
        FPSViewer.new_frame_time = time.time()

        FPSViewer.fps = 1 / (FPSViewer.new_frame_time - FPSViewer.prev_frame_time)
        FPSViewer.prev_frame_time = FPSViewer.new_frame_time

    @staticmethod
    def show_fps(frame):
        printable_fps = "FPS: {:.2f}".format(FPSViewer.fps)
        cv2.putText(frame, printable_fps, (20, 20), cv2.FONT_ITALIC, 0.5, (0, 0, 0), 2)

