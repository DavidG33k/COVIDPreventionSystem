import cv2
import imutils
import PySimpleGUI as sg
from FPSViewer import FPSViewer
from MovementDetector import MovementDetector
from PreventionDetectors import PreventionDetectors



def main():

    sg.theme('DarkTeal10')

    input_choice_frame = [
        [sg.Button('Sample video', key=''), sg.Button('Webcam', key=''), sg.Button('IP Camera', key='')],
    ]

    movement_detector_frame = [
        [sg.Checkbox('show contours', key='show_contours'), sg.Checkbox('show rectangles', key='show_rectangles')],
    ]

    prevention_detectors_frame = [
        [sg.Checkbox('detect people', default=True, key='detect_people'), sg.Checkbox('detect gathering', default=True, key='detect_gathering'), sg.Checkbox('detect social distancing', default=True, key='detect_social_distancing')],
        [sg.Text('minimum distance'), sg.Slider(range=(0, 300), default_value=70, size=(51.5, 15), orientation='horizontal', key='MIN_DISTANCE')],
        [sg.Text('minimum confidence (in percentage)'), sg.Slider(range=(0, 100), default_value=50, size=(40, 15), orientation='horizontal', key='MIN_CONFIDENCE')],
        [sg.Text('maximum number of people'), sg.Spin([i for i in range(0, 31)], initial_value=5, key='MAX_PERSONS', font=('Helvetica 13'))]
    ]

    sound_button = [
        [sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/sound_off.png', image_size=(50, 50), image_subsample=5, border_width=0, key='sound_button')],
    ]

    sound_button = [
        [
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/sound_off.png', image_size=(50, 50), image_subsample=5, border_width=0, key='sound_button'),
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/exit.png', image_size=(50, 50), image_subsample=5, border_width=0, key='exit_button')
        ],
    ]

    unical_icon = [
        [sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/icon.png', image_size=(600, 60), image_subsample=4, border_width=0)],
    ]

    layout = [
        #[sg.Column(unical_icon, justification='center')],
        [sg.Image(key='image')],
        [sg.Frame('Input type choice', input_choice_frame, pad=(0, 20), font=('Helvetica 12'))],
        [sg.Frame('Movement detector', movement_detector_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Prevention detectors', prevention_detectors_frame, pad=(0, 20), font=('Helvetica 12'))],
        [sg.Column(sound_button, justification='right')]
    ]

    window_title = 'COVID Prevention System'
    window = sg.Window(window_title, layout, location=(0, 0))

    video = cv2.VideoCapture('video/test_video2.mp4')  # 0 for Webcam, path to open a video.

    ret, frame1 = video.read()
    ret, frame2 = video.read()

    sound_enabled = False

    while True:
        event, values = window.read(timeout=0)

        if event == sg.WIN_CLOSED or event == 'exit_button':
            return

        if event == 'sound_button' and sound_enabled:
            window['sound_button'].Update(image_filename='resources/sound_off.png', image_size=(50, 50), image_subsample=5)
            sound_enabled = False
        elif event == 'sound_button' and not sound_enabled:
            window['sound_button'].Update(image_filename='resources/sound_on.png', image_size=(50, 50), image_subsample=5)
            sound_enabled = True



        if values['show_contours'] or values['show_rectangles']:
            MovementDetector.detect(cv2, frame1, frame2, enable_contours=values['show_contours'], enable_rectangles=values['show_rectangles'])

        frame = imutils.resize(frame1, width=600)  # imutils library used to resize every frame of video.

        if values['detect_people']:
            PreventionDetectors.detect(frame, detect_gathering=values['detect_gathering'], detect_social_distancing=values['detect_social_distancing'], enable_sound=sound_enabled,
                                   MIN_CONFIDENCE=(values['MIN_CONFIDENCE']/100),
                                   MAX_PERSONS=values['MAX_PERSONS'],
                                   MIN_DISTANCE=values['MIN_DISTANCE'])

        FPSViewer.calculate_fps()
        FPSViewer.show_fps(frame)

        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        window['image'].update(data=imgbytes)

        frame1 = frame2
        ret, frame2 = video.read()

    video.release()
    window.Close()

main()




'''

def do_nothing_trackbar(x):
    pass

def main():

    FPSViewer.reset()

    window_title = 'COVID Prevention System'
    cv2.namedWindow(window_title)


    # The following two line of code are used to remove toolbar and statusbar.
    cv2.namedWindow(window_title, cv2.WINDOW_GUI_NORMAL)
    cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    video = cv2.VideoCapture('video/test_video2.mp4')  # 0 for Webcam, path to open a video.

    cv2.createTrackbar('minimum distance', window_title, 70, 300, do_nothing_trackbar)
    cv2.createTrackbar('minimum confidence (in percentage)', window_title, 50, 100, do_nothing_trackbar)
    cv2.createTrackbar('maximum number of people', window_title, 5, 30, do_nothing_trackbar)

    ret, frame1 = video.read()
    ret, frame2 = video.read()

    detect_movement = False

    while True:


        if detect_movement:
            MovementDetector.detect(cv2, frame1, frame2, enable_contours=False, enable_rectangle=False)

        frame = imutils.resize(frame1, width=600)  # imutils library used to resize every frame of video.

        PreventionDetectors.detect(frame, detect_gathering=True, detect_social_distancing=True,
                                   MIN_CONFIDENCE=(cv2.getTrackbarPos('minimum confidence (in percentage)',window_title)/100),
                                   MAX_PERSONS=cv2.getTrackbarPos('maximum number of people', window_title),
                                   MIN_DISTANCE=cv2.getTrackbarPos('minimum distance', window_title))

        FPSViewer.calculate_fps()
        FPSViewer.show_fps(frame)


        cv2.imshow(window_title, frame)


        frame1 = frame2
        ret, frame2 = video.read()


        key = cv2.waitKey(1)
        if key == 27:  # 27 is the key code to close the software with the "ESC" button.
            break

        if cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE) == 0:  # The method returns a 1 if it is visible and 0 if it is not. So, if I press 'X' button the window will be closed and the software too.
            break



    video.release()
    cv2.destroyAllWindows()


main()

'''