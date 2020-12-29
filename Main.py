import cv2
import imutils
import PySimpleGUI as sg
from FPSViewer import FPSViewer
from MovementDetector import MovementDetector
from PreventionDetectors import PreventionDetectors


def main():

    sg.theme('DarkTeal10')

    input_choice_frame = [
        [sg.Button('Sample video', key='sv'), sg.Button('Webcam', key='wc'), sg.Button('IP Camera', key='ip')],
        [sg.Text('Insert a valid RTSP url (rtsp://user:pass@ip:port):', key='text_url_stream', visible=False)],
        [sg.InputText(key='url_stream', visible=False), sg.Button('ok', key='ok', visible=False)],
        [sg.Text('Invalid URL. Please try again!', key='invalid_url_text', text_color='red', visible=False)]
    ]

    movement_detector_frame = [
        [sg.Checkbox('show contours', key='show_contours'), sg.Checkbox('show rectangles', key='show_rectangles')],
    ]

    prevention_detectors_frame = [
        [sg.Checkbox('detect people', default=True, key='detect_people'), sg.Checkbox('detect gathering', default=True, key='detect_gathering'), sg.Checkbox('detect social distancing', default=False, key='detect_social_distancing'), sg.Checkbox('enable people limit', default=False, key='enable_people_limit')],
        [sg.Text('minimum confidence (in percentage)'), sg.Slider(range=(0, 100), default_value=50, size=(40, 15), orientation='horizontal', key='MIN_CONFIDENCE')],
        [sg.Text('minimum distance'), sg.Slider(range=(0, 300), default_value=70, size=(51.5, 15), orientation='horizontal', key='MIN_DISTANCE')],
        [sg.Text('gathering time limit (in frame)'), sg.Slider(range=(0, 500), default_value=50, size=(44.5, 15), orientation='horizontal', key='TIME_LIMIT')],
        [sg.Text('maximum number of people', pad=(0, 10)), sg.Spin([i for i in range(0, 31)], initial_value=5, key='MAX_PERSONS', pad=(0, 10), font=('Helvetica 13'))]
    ]

    circle_buttons = [
        [
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/sound_off.png', image_size=(50, 50), image_subsample=5, border_width=0, key='sound_button'),
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/exit.png', image_size=(50, 50), image_subsample=5, border_width=0, key='exit_button')
        ],
    ]

    logo = [
        [sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/logo2.png', image_size=(500, 90), image_subsample=4, border_width=0)],
    ]

    credits = [
        [sg.Text('Final Release(v1.0): X/X/XXXX         Developed by DavidG33k', font='Helvetica 9')]
    ]


    layout = [
        [sg.Column(logo, justification='center')],
        [sg.Image(key='image')],
        [sg.Frame('Input type choice', input_choice_frame, pad=(0, 20), font=('Helvetica 12'), key='input_frame')],
        [sg.Frame('Movement detector', movement_detector_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Prevention detectors', prevention_detectors_frame, pad=(0, 20), font=('Helvetica 12'))],
        [sg.Column(circle_buttons, justification='right')],
        [sg.HorizontalSeparator(color='grey')],
        [sg.Column(credits, justification='center')]
    ]
    window_title = 'COVID Prev. Sys.'
    window = sg.Window(window_title, layout, location=(0, 0))

    sound_enabled = False

    input_choice = ''

    while True:
        event, values = window.read(timeout=0)

        if event == sg.WIN_CLOSED or event == 'exit_button':
            return

        if event == 'sv':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            input_choice = 'video/test_video2.mp4'
        elif event == 'wc':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            input_choice = '0'
        elif event == 'ip':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            window['sv'].Update(disabled=True)
            window['wc'].Update(disabled=True)
            window['ip'].Update(disabled=True)
            window['text_url_stream'].unhide_row()
            window['url_stream'].unhide_row()
            window['ok'].unhide_row()
            window['text_url_stream'].Update(visible=True)
            window['url_stream'].Update(visible=True)
            window['ok'].Update(visible=True)
        elif event == 'ok':
            window['sv'].Update(disabled=False)
            window['wc'].Update(disabled=False)
            window['ip'].Update(disabled=False)
            window['text_url_stream'].Update(visible=False)
            window['url_stream'].Update(visible=False)
            window['ok'].Update(visible=False)
            window['text_url_stream'].hide_row()
            window['url_stream'].hide_row()
            window['ok'].hide_row()
            input_choice = values['url_stream']  # rtsp://192.168.1.4:8080/h264_pcm.sdp

        if input_choice == '0':
            video = cv2.VideoCapture(0)  # 0 for Webcam, path to open a video.
            break
        elif not input_choice == '':
            video = cv2.VideoCapture(input_choice)

            if video.isOpened():
                input_choice = ''
                break

            window['invalid_url_text'].unhide_row()
            window['invalid_url_text'].Update(visible=True)
            input_choice = ''


    ret, frame1 = video.read()
    ret, frame2 = video.read()

    while True:
        event, values = window.read(timeout=0)

        if event == sg.WIN_CLOSED or event == 'exit_button':
            return

        if event == 'sv':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            video = cv2.VideoCapture('video/test_video2.mp4')
        elif event == 'wc':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            video = cv2.VideoCapture(0)
        elif event == 'ip':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            window['sv'].Update(disabled=True)
            window['wc'].Update(disabled=True)
            window['ip'].Update(disabled=True)
            window['text_url_stream'].unhide_row()
            window['url_stream'].unhide_row()
            window['ok'].unhide_row()
            window['text_url_stream'].Update(visible=True)
            window['url_stream'].Update(visible=True)
            window['ok'].Update(visible=True)
        elif event == 'ok':
            window['sv'].Update(disabled=False)
            window['wc'].Update(disabled=False)
            window['ip'].Update(disabled=False)
            window['text_url_stream'].Update(visible=False)
            window['url_stream'].Update(visible=False)
            window['ok'].Update(visible=False)
            window['text_url_stream'].hide_row()
            window['url_stream'].hide_row()
            window['ok'].hide_row()
            video_backup = video
            video = cv2.VideoCapture(values['url_stream'])

            if not video.isOpened():
                window['invalid_url_text'].unhide_row()
                window['invalid_url_text'].Update(visible=True)
                video = video_backup


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
            PreventionDetectors.detect(frame, detect_gathering=values['detect_gathering'], detect_social_distancing=values['detect_social_distancing'], enable_sound=sound_enabled, enable_people_limit=values['enable_people_limit'],
                                   MIN_CONFIDENCE=(values['MIN_CONFIDENCE']/100),
                                   MAX_PERSONS=values['MAX_PERSONS'],
                                   MIN_DISTANCE=values['MIN_DISTANCE'],
                                   TIME_LIMIT=values['TIME_LIMIT'])

        FPSViewer.calculate_fps()
        FPSViewer.show_fps(frame)  # TODO Sono obsoleto :( migliorami!

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