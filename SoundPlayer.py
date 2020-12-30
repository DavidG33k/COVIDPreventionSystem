import pygame


class SoundPlayer:

    #pygame.init()
    #pygame.mixer.music.set_volume(0.2)
    #pygame.mixer.music.load('sounds/warning.wav')

    @staticmethod
    def playWarning():
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

    @staticmethod
    def stopWarning():
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
