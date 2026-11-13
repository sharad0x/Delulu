
import pygame


def initialize_audio():

    if not pygame.mixer.get_init():
        pygame.mixer.init()


def play_song(song):

    pygame.mixer.music.load(song)

    pygame.mixer.music.play()


def stop_song():

    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def shutdown_audio():

    if pygame.mixer.get_init():
        pygame.mixer.quit()
