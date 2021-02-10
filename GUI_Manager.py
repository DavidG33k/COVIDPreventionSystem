import cv2
import time
import os
import subprocess
import glob
import webbrowser
from PreventionDetectors import PreventionDetectors

class GUI_Manager:

    @staticmethod
    def buttons_listener(video, window, values, event, log_name_file, sound_enabled, input_choice_backup, initialization_time):

        # INPUT BUTTONS
        if event == 'sv':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            window['sv'].Update(disabled=True)
            window['wc'].Update(disabled=True)
            window['ip'].Update(disabled=True)
            video = cv2.VideoCapture('resources/Initialization.mp4')
            input_choice_backup = 'sv'
            initialization_time = time.time()
        elif event == 'wc':
            window['invalid_url_text'].hide_row()
            window['invalid_url_text'].Update(visible=False)
            window['sv'].Update(disabled=True)
            window['wc'].Update(disabled=True)
            window['ip'].Update(disabled=True)
            video = cv2.VideoCapture('resources/Initialization.mp4')
            input_choice_backup = 'wc'
            initialization_time = time.time()
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
            window['sv'].Update(disabled=True)
            window['wc'].Update(disabled=True)
            window['ip'].Update(disabled=True)
            window['text_url_stream'].Update(visible=False)
            window['url_stream'].Update(visible=False)
            window['ok'].Update(visible=False)
            window['text_url_stream'].hide_row()
            window['url_stream'].hide_row()
            window['ok'].hide_row()
            video = cv2.VideoCapture('resources/Initialization.mp4')
            input_choice_backup = 'ok'
            initialization_time = time.time()


        if initialization_time != None and time.time() - initialization_time >= 5:
            window['sv'].Update(disabled=False)
            window['wc'].Update(disabled=False)
            window['ip'].Update(disabled=False)
            PreventionDetectors.reset()
            if input_choice_backup == 'sv':
                video = cv2.VideoCapture('video/test_video2.mp4')

                log_name_file = time.ctime()
                file = open("output/" + log_name_file + ".txt", "w+")
                file.write("INPUT TYPE: Sample video\n\n")
                file.close()
            elif input_choice_backup == 'wc':
                video = cv2.VideoCapture(0)

                log_name_file = time.ctime()
                file = open("output/" + log_name_file + ".txt", "w+")
                file.write("INPUT TYPE: WebCam\n\n")
                file.close()
            elif input_choice_backup == 'ok':
                video = cv2.VideoCapture(values['url_stream'])

                if not video.isOpened():
                    window['invalid_url_text'].unhide_row()
                    window['invalid_url_text'].Update(visible=True)
                    video = cv2.VideoCapture('resources/TryAgain.mp4')
                else:
                    log_name_file = time.ctime()
                    file = open("output/" + log_name_file + ".txt", "w+")
                    file.write("INPUT TYPE: IPCam (URL: " + values['url_stream'] + ")\n\n")
                    file.close()

            initialization_time = None


        # LOG BUTTONS
        if event == 'open_logs_folder':
            try:
                os.startfile('output/')  # To open a directory in Windows systems
            except:
                subprocess.Popen(['xdg-open', 'output/'])  # To open a directory in Unix systems
        elif event == 'clear_logs_folder':
            files = glob.glob('output/*')
            for f in files:
                os.remove(f)

        # SOUND BUTTON
        if event == 'sound_button' and sound_enabled:
            window['sound_button'].Update(image_filename='resources/sound_off_60x60.png', image_size=(60, 60), image_subsample=1)
            sound_enabled = False
        elif event == 'sound_button' and not sound_enabled:
            window['sound_button'].Update(image_filename='resources/sound_on_60x60.png', image_size=(60, 60), image_subsample=1)
            sound_enabled = True

        # GITHUB BUTTON
        if event == 'github_button':
            webbrowser.open('https://github.com/DavidG33k/')

        return video, log_name_file, sound_enabled, input_choice_backup, initialization_time

    @staticmethod
    def responsive_gui(window, values, event):

        if event == 'detect_people':
            if values['detect_people']:
                window['show_people_ID'].Update(disabled=False)
                window['shows_confidence_percentage'].Update(disabled=False)
                window['show_tracking_line'].Update(disabled=False)
                window['MIN_CONFIDENCE'].Update(disabled=False)
                window['detect_gathering'].Update(disabled=False)
                window['detect_social_distancing'].Update(disabled=False)
                window['report_people_limit'].Update(disabled=False)
                if values['detect_gathering'] or values['detect_social_distancing']:
                    window['MIN_DISTANCE'].Update(disabled=False)
                if values['report_people_limit']:
                    window['MAX_PERSONS'].Widget['state'] = 'normal'
                if values['detect_gathering']:
                    window['TIME_LIMIT'].Widget['state'] = 'normal'
            else:
                window['show_people_ID'].Update(disabled=True)
                window['shows_confidence_percentage'].Update(disabled=True)
                window['show_tracking_line'].Update(disabled=True)
                window['MIN_CONFIDENCE'].Update(disabled=True)
                window['detect_gathering'].Update(disabled=True)
                window['detect_social_distancing'].Update(disabled=True)
                window['report_people_limit'].Update(disabled=True)
                window['MIN_DISTANCE'].Update(disabled=True)
                window['MAX_PERSONS'].Widget['state'] = 'disabled'
                window['TIME_LIMIT'].Widget['state'] = 'disabled'
        elif event == 'report_people_limit':
            if values['report_people_limit']:
                window['MAX_PERSONS'].Widget['state'] = 'normal'
            elif not values['report_people_limit']:
                window['MAX_PERSONS'].Widget['state'] = 'disabled'
        elif event == 'detect_gathering' or event == 'detect_social_distancing':
            if values['detect_gathering']:
                window['TIME_LIMIT'].Widget['state'] = 'normal'
            else:
                window['TIME_LIMIT'].Widget['state'] = 'disabled'
            if values['detect_gathering'] or values['detect_social_distancing']:
                window['MIN_DISTANCE'].Update(disabled=False)
            else:
                window['MIN_DISTANCE'].Update(disabled=True)

