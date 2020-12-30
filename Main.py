import cv2
import imutils
import configparser
import PySimpleGUI as sg
from FPSViewer import FPSViewer
from MovementDetector import MovementDetector
from PreventionDetectors import PreventionDetectors


def main():

    config = configparser.ConfigParser()
    config.read('config.ini')

    sg.theme('DarkTeal10')

    input_choice_frame = [
        [sg.Button('Sample video', key='sv'), sg.Button('Webcam', key='wc'), sg.Button('IP Camera', key='ip')],
        [sg.Text('Insert a valid RTSP url (rtsp://user:pass@ip:port):', key='text_url_stream', visible=False)],
        [sg.InputText(key='url_stream', visible=False), sg.Button('ok', key='ok', visible=False)],
        [sg.Text('Invalid URL. Please try again!', key='invalid_url_text', text_color='red', visible=False)]
    ]

    movement_detector_frame = [
        [sg.Checkbox('show contours', default=config['DEFAULT']['show_contours'], key='show_contours'), sg.Checkbox('show rectangles', default=config['DEFAULT']['show_rectangles'], key='show_rectangles')],
    ]

    prevention_detectors_frame = [
        [sg.Checkbox('detect people', default=config['DEFAULT']['detect_people'], key='detect_people'), sg.Checkbox('detect gathering', default=config['DEFAULT']['detect_gathering'], key='detect_gathering'), sg.Checkbox('detect social distancing', default=config['DEFAULT']['detect_social_distancing'], key='detect_social_distancing'), sg.Checkbox('report people limit', default=config['DEFAULT']['report_people_limit'], key='report_people_limit')],
        [sg.Text('minimum confidence (in percentage)'), sg.Slider(range=(0, config['DEFAULT']['minimum_confidence_max_slider_range']), default_value=config['DEFAULT']['minimum_default_confidence'], size=(40, 15), orientation='horizontal', key='MIN_CONFIDENCE')],
        [sg.Text('minimum distance'), sg.Slider(range=(0, config['DEFAULT']['minimum_distance_max_slider_range']), default_value=config['DEFAULT']['minimum_default_distance'], size=(51.5, 15), orientation='horizontal', key='MIN_DISTANCE')],
        [sg.Text('gathering time limit', pad=(5, 10)), sg.Spin([i for i in range(0, int(config['DEFAULT']['time_limit_max_spin_range']))], initial_value=config['DEFAULT']['default_time_limit'], pad=(0, 10), key='TIME_LIMIT', font=('Helvetica 13')), sg.Text('seconds', pad=(5, 10))],
        [sg.Text('maximum number of people'), sg.Spin([i for i in range(0, int(config['DEFAULT']['max_people_max_spin_range']))], initial_value=config['DEFAULT']['default_max_people'], key='MAX_PERSONS', font=('Helvetica 13'))]
    ]

    circle_buttons = [
        [
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/sound_off.png', image_size=(50, 50), image_subsample=5, border_width=0, key='sound_button'),
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/exit.png', image_size=(50, 50), image_subsample=5, border_width=0, key='exit_button')
        ],
    ]

    logo = [
        [sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/logo1.png', image_size=(670, 120), image_subsample=3, border_width=0)],
    ]

    credits = [
        [sg.Text('Final Release(v1.0): X/X/XXXX         Developed by DavidG33k', font='Helvetica 9')]
    ]

    video_layout = [
        [sg.Image(key='image', background_color='black')]
    ]

    layout = [
        [sg.Column(logo, justification='center')],
        [sg.Column(video_layout, justification='center')],
        [sg.Frame('Input type choice', input_choice_frame, pad=(0, 20), font=('Helvetica 12'), key='input_frame')],
        [sg.Frame('Movement detector', movement_detector_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Prevention detectors', prevention_detectors_frame, pad=(0, 20), font=('Helvetica 12'))],
        [sg.Column(circle_buttons, justification='right')],
        [sg.HorizontalSeparator(color='grey')],
        [sg.Column(credits, justification='center')]
    ]

    window_title = 'COVID Prev. Sys.'
    window = sg.Window(window_title, layout, location=(0, 0))

    file = open("output/log.txt", "r+")
    file.truncate(0)
    file.close()

    sound_enabled = False

    video = None
    frame1 = None
    frame2 = None

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

        if frame1 is not None and frame2 is not None:
            if values['show_contours'] or values['show_rectangles']:
                MovementDetector.detect(cv2, frame1, frame2, enable_contours=values['show_contours'], enable_rectangles=values['show_rectangles'])

            frame = imutils.resize(frame1, width=600)  # imutils library used to resize every frame of video.

            if values['detect_people']:
                PreventionDetectors.detect(frame, detect_gathering=values['detect_gathering'], detect_social_distancing=values['detect_social_distancing'], enable_sound=sound_enabled, report_people_limit=values['report_people_limit'],
                                   MIN_CONFIDENCE=(values['MIN_CONFIDENCE']/100),
                                   MAX_PERSONS=values['MAX_PERSONS'],
                                   MIN_DISTANCE=values['MIN_DISTANCE'],
                                   TIME_LIMIT=values['TIME_LIMIT'])

            FPSViewer.calculate_fps()
            FPSViewer.show_fps(frame)

            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window['image'].update(data=imgbytes)

        if video is not None:
            frame1 = frame2
            ret, frame2 = video.read()

    video.release()
    window.Close()

main()