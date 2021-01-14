import time
import os
import subprocess
import glob
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
        [sg.Checkbox('detect people', default=config['DEFAULT']['detect_people'], key='detect_people'), sg.Checkbox('detect gathering', default=config['DEFAULT']['detect_gathering'], key='detect_gathering'), sg.Checkbox('detect social distancing', default=config['DEFAULT']['detect_social_distancing'], key='detect_social_distancing'), sg.Checkbox('show tracking line', default=config['DEFAULT']['show_tracking_line'], key='show_tracking_line')],
        [sg.Text('minimum confidence (in percentage)'), sg.Slider(range=(0, config['DEFAULT']['minimum_confidence_max_slider_range']), default_value=config['DEFAULT']['minimum_default_confidence'], size=(40, 15), orientation='horizontal', key='MIN_CONFIDENCE')],
        [sg.Text('minimum distance'), sg.Slider(range=(0, config['DEFAULT']['minimum_distance_max_slider_range']), default_value=config['DEFAULT']['minimum_default_distance'], size=(51.5, 15), orientation='horizontal', key='MIN_DISTANCE')],
        [sg.Text('gathering time limit', pad=(5, 10)), sg.Spin([i for i in range(0, int(config['DEFAULT']['time_limit_max_spin_range']))], initial_value=config['DEFAULT']['default_time_limit'], pad=(0, 10), key='TIME_LIMIT', font=('Helvetica 13')), sg.Text('seconds', pad=(5, 10))],
        [sg.Checkbox('report maximum number of people', default=config['DEFAULT']['report_people_limit'], key='report_people_limit'), sg.Spin([i for i in range(0, int(config['DEFAULT']['max_people_max_spin_range']))], initial_value=config['DEFAULT']['default_max_people'], key='MAX_PERSONS', font=('Helvetica 13'))]
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

    log_frame = [
        [sg.Button('Open logs folder', key='open_logs_folder'), sg.Button('Clear logs folder', key='clear_logs_folder')]
    ]

    layout = [
        [sg.Column(logo, justification='center')],
        [sg.Column(video_layout, justification='center')],
        [sg.Frame('Input type choice', input_choice_frame, pad=(0, 20), font=('Helvetica 12'))],
        [sg.Frame('Movement detector', movement_detector_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Prevention detectors', prevention_detectors_frame, pad=(0, 20), font=('Helvetica 12'))],
        [sg.Frame('Logs', log_frame, font=('Helvetica 12'))],
        [sg.Column(circle_buttons, justification='right')],
        [sg.HorizontalSeparator(color='grey')],
        [sg.Column(credits, justification='center')]
    ]

    window_title = 'COVID Prev. Sys.'
    window = sg.Window(window_title, layout, location=(0, 0))

    sound_enabled = False

    log_name_file = ''

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
            PreventionDetectors.reset()

            log_name_file = time.ctime()
            file = open("output/" + log_name_file + ".txt", "w+")
            file.write("INPUT TYPE: Sample video\n\n")
            file.close()
        elif event == 'wc':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            video = cv2.VideoCapture(0)
            PreventionDetectors.reset()

            log_name_file = time.ctime()
            file = open("output/" + log_name_file + ".txt", "w+")
            file.write("INPUT TYPE: WebCam\n\n")
            file.close()
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
            else:
                PreventionDetectors.reset()
                log_name_file = time.ctime()
                file = open("output/" + log_name_file + ".txt", "w+")
                file.write("INPUT TYPE: IPCam (URL: " + values['url_stream'] + ")\n\n")
                file.close()

        if event == 'open_logs_folder':
            try:
                os.startfile('output/')  # To open a directory in Windows systems
            except:
                subprocess.Popen(['xdg-open', 'output/'])  # To open a directory in Unix systems
        elif event == 'clear_logs_folder':
            files = glob.glob('output/*')
            for f in files:
                os.remove(f)

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
                PreventionDetectors.detect(frame, detect_gathering=values['detect_gathering'], detect_social_distancing=values['detect_social_distancing'], enable_sound=sound_enabled, report_people_limit=values['report_people_limit'], show_tracking_line=values['show_tracking_line'],
                                   MIN_CONFIDENCE=(values['MIN_CONFIDENCE']/100),
                                   MAX_PERSONS=values['MAX_PERSONS'],
                                   MIN_DISTANCE=values['MIN_DISTANCE'],
                                   TIME_LIMIT=values['TIME_LIMIT'],
                                   log_name_file=log_name_file)

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