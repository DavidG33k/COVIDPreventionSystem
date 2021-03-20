class MovementDetector:

    @staticmethod
    def detect(cv2, frame1, frame2, enable_contours, enable_rectangles):
        frame_difference = cv2.absdiff(frame1, frame2)  # absolute difference between frame1 and frame2.
        gray = cv2.cvtColor(frame_difference, cv2.COLOR_BGR2GRAY)  # used to convert the difference of the frame in a gray scale, so RGB to GRAY.
        blur = cv2.GaussianBlur(gray, (5, 5), 0)  # Gussian blur applied on the difference of the frame in gray scale.
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)  # Based on a threshold, if the pixel color exceeds it, I set the color to a max value (generally white), else to zero (generally black).
        dilated = cv2.dilate(thresh, None, iterations=3)  # Essentially a dilatation applied to a frame, so a thickness. The opposite is the cv2.erode() method.
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # used to find the contours

        if enable_contours:
            MovementDetector.__show_contours(cv2, frame1, contours)
        if enable_rectangles:
            MovementDetector.__show_rectangle(cv2, frame1, contours)

    @staticmethod
    def __show_contours(cv2, frame1, contours):
        cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2)

    @staticmethod
    def __show_rectangle(cv2, frame1, contours):
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)

            if cv2.contourArea(contour) > 4000:
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 0, 255), 2)

