import cv2
import imutils
import configparser
import PySimpleGUI as sg
from FPSViewer import FPSViewer
from MovementDetector import MovementDetector
from PreventionDetectors import PreventionDetectors
from GUI_Manager import GUI_Manager


def main():

    config = configparser.ConfigParser()
    config.read('config.ini')

    sg.theme('DarkTeal10') #DARK MODE ENABLED BY DEFAULT

    input_choice_frame = [
        [sg.Button('Sample video', key='sv'), sg.Button('Webcam', key='wc'), sg.Button('IP Camera', key='ip')],
        [sg.Text('Insert a valid RTSP url (rtsp://user:pass@ip:port):', key='text_url_stream', visible=False)],
        [sg.InputText(key='url_stream', visible=False), sg.Button('ok', key='ok', visible=False)],
        [sg.Text('Invalid URL. Please try again!', key='invalid_url_text', text_color='red', visible=False)]
    ]

    movement_detector_frame = [
        [sg.Checkbox('show contours', default=config['DEFAULT']['show_contours'], key='show_contours'), sg.Checkbox('show rectangles', default=config['DEFAULT']['show_rectangles'], key='show_rectangles')],
    ]

    main_options_frame = [
        [sg.Checkbox('detect people', default=config['DEFAULT']['detect_people'], enable_events=True, key='detect_people'), sg.Checkbox('show people ID', default=config['DEFAULT']['show_people_ID'], disabled=not bool(int(config['DEFAULT']['detect_people'])),key='show_people_ID'), sg.Checkbox('shows confidence percentage', default=config['DEFAULT']['shows_confidence_percentage'], disabled=not bool(int(config['DEFAULT']['detect_people'])), key='shows_confidence_percentage'), sg.Checkbox('show tracking line', default=config['DEFAULT']['show_tracking_line'], disabled=not bool(int(config['DEFAULT']['detect_people'])), key='show_tracking_line')],
        [sg.Text('minimum confidence (in percentage)'), sg.Slider(range=(0, config['DEFAULT']['minimum_confidence_max_slider_range']), default_value=config['DEFAULT']['minimum_default_confidence'], size=(43, 15), orientation='horizontal', disabled=not bool(int(config['DEFAULT']['detect_people'])), key='MIN_CONFIDENCE')],
    ]

    gathering_detection_frame = [
        [sg.Checkbox('detect gathering', default=config['DEFAULT']['detect_gathering'], enable_events=True, disabled=not bool(int(config['DEFAULT']['detect_people'])), key='detect_gathering'), sg.Checkbox('report social distancing violation', default=config['DEFAULT']['report_social_distancing_violation'], enable_events=True, disabled=not bool(int(config['DEFAULT']['detect_people'])), key='detect_social_distancing'), sg.Checkbox('report maximum number of people:', default=config['DEFAULT']['report_people_limit'], enable_events=True, disabled=not bool(int(config['DEFAULT']['detect_people'])), key='report_people_limit'), sg.Spin([i for i in range(0, int(config['DEFAULT']['max_people_max_spin_range']))], initial_value=config['DEFAULT']['default_max_people'], disabled=not bool(int(config['DEFAULT']['report_people_limit'])) or not bool(int(config['DEFAULT']['detect_people'])), key='MAX_PERSONS', font=('Helvetica 13'))],
        [sg.Text('minimum social distance'), sg.Slider(range=(0, config['DEFAULT']['minimum_distance_max_slider_range']), default_value=config['DEFAULT']['minimum_default_distance'], size=(50, 15), orientation='horizontal', disabled=(not bool(int(config['DEFAULT']['detect_gathering'])) and not bool(int(config['DEFAULT']['report_social_distancing_violation']))) or not bool(int(config['DEFAULT']['detect_people'])), key='MIN_DISTANCE')],
        [sg.Text('gathering time limit: ', pad=(5, 10)), sg.Spin([i for i in range(0, int(config['DEFAULT']['time_limit_max_spin_range']))], initial_value=config['DEFAULT']['default_time_limit'], pad=(0, 10), disabled=not bool(int(config['DEFAULT']['detect_gathering'])) or not bool(int(config['DEFAULT']['detect_people'])), key='TIME_LIMIT', font=('Helvetica 13')), sg.Text('seconds', pad=(5, 10))],
    ]

    circle_buttons = [
        [
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/sound_off_60x60.png', image_size=(60, 60), image_subsample=1, border_width=0, key='sound_button'),
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']),image_filename='resources/github_60x60.png', image_size=(60, 60), image_subsample=1, border_width=0, key='github_button'),
            sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/exit_60x60.png', image_size=(60, 60), image_subsample=1, border_width=0, key='exit_button')
        ],
    ]

    logo = [
        [sg.ReadFormButton('', button_color=('black', sg.LOOK_AND_FEEL_TABLE['DarkTeal10']['BACKGROUND']), image_filename='resources/logo2.png', image_size=(670, 120), image_subsample=3, border_width=0)],
    ]

    video_layout = [
        [sg.Image(key='image', background_color='black')]
    ]

    log_frame = [
        [sg.Button('Open logs folder', key='open_logs_folder'), sg.Button('Clear logs folder', key='clear_logs_folder')]
    ]

    # MAIN LAYOUT
    layout = [
        [sg.Column(logo, justification='center')],
        [sg.Column(video_layout, justification='center')],
        [sg.Frame('Input type choice', input_choice_frame, pad=(0, 0), font=('Helvetica 12'))],
        [sg.Frame('Logs', log_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Main options', main_options_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Gathering detection', gathering_detection_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Frame('Movement detection', movement_detector_frame, pad=(0, 10), font=('Helvetica 12'))],
        [sg.Column(circle_buttons, justification='right')],
    ]

    window_title = 'COVID Prev. Sys.'
    window = sg.Window(window_title, layout, location=(0, 0))

    sound_enabled = False

    log_name_file = ''

    __enable_contours = None
    __enable_rectangles = None
    __detect_gathering = None
    __detect_social_distancing = None
    __report_people_limit = None
    __show_tracking_line = None
    __show_people_ID = None
    __shows_confidence_percentage = None
    __MIN_CONFIDENCE = None
    __MAX_PERSONS = None
    __MIN_DISTANCE = None
    __TIME_LIMIT = None

    video = None
    frame1 = None
    frame2 = None

    input_choice_backup = None
    initialization_time = None

    while True:
        event, values = window.read(timeout=0)

        # EXIT CONDITION
        if event == sg.WIN_CLOSED or event == 'exit_button':
            return

        # BUTTONS LISTENER
        video, log_name_file, sound_enabled, input_choice_backup, initialization_time = GUI_Manager.buttons_listener(video, window, values, event, log_name_file, sound_enabled, input_choice_backup, initialization_time)

        # RESPONSIVE GUI
        GUI_Manager.responsive_gui(window, values, event)

        # UPDATE CONSTANTS
        if __enable_contours != values['show_contours']:
            __enable_contours = values['show_contours']
        if __enable_rectangles != values['show_rectangles']:
            __enable_rectangles = values['show_rectangles']
        if __detect_gathering != values['detect_gathering']:
            __detect_gathering = values['detect_gathering']
        if __detect_social_distancing != values['detect_social_distancing']:
            __detect_social_distancing = values['detect_social_distancing']
        if __report_people_limit != values['report_people_limit']:
            __report_people_limit = values['report_people_limit']
        if __show_tracking_line != values['show_tracking_line']:
            __show_tracking_line = values['show_tracking_line']
        if __show_people_ID != values['show_people_ID']:
            __show_people_ID = values['show_people_ID']
        if __shows_confidence_percentage != values['shows_confidence_percentage']:
            __shows_confidence_percentage = values['shows_confidence_percentage']
        if __MIN_CONFIDENCE != (values['MIN_CONFIDENCE']/100):
            __MIN_CONFIDENCE = (values['MIN_CONFIDENCE']/100)
        if __MAX_PERSONS != values['MAX_PERSONS']:
            __MAX_PERSONS = values['MAX_PERSONS']
        if __MIN_DISTANCE != values['MIN_DISTANCE']:
            __MIN_DISTANCE = values['MIN_DISTANCE']
        if __TIME_LIMIT != values['TIME_LIMIT']:
            __TIME_LIMIT = values['TIME_LIMIT']

        if frame1 is not None and frame2 is not None:
            if values['show_contours'] or values['show_rectangles']:
                MovementDetector.detect(cv2, frame1, frame2, enable_contours=__enable_contours, enable_rectangles=__enable_rectangles)

            frame = imutils.resize(frame1, width=600)  # imutils library used to resize every frame of video.

            if values['detect_people']:
                PreventionDetectors.detect(frame, detect_gathering=__detect_gathering, detect_social_distancing=__detect_social_distancing, enable_sound=sound_enabled, report_people_limit=__report_people_limit, show_tracking_line=__show_tracking_line, show_people_ID=__show_people_ID, shows_confidence_percentage=__shows_confidence_percentage,
                                   MIN_CONFIDENCE=__MIN_CONFIDENCE,
                                   MAX_PERSONS=__MAX_PERSONS,
                                   MIN_DISTANCE=__MIN_DISTANCE,
                                   TIME_LIMIT=__TIME_LIMIT,
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