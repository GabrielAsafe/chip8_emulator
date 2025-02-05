import pygame
import os

class Timers:
    def __init__(self):
        self.delay_timer_value = 0
        self.sound_timer_value = 0

        # Inicializa o pygame mixer para som
        pygame.mixer.init()
        self.sound_path = os.path.abspath('res/beep.mp3')

    def set_delay_timer(self, val):
        self.delay_timer_value = val

    def set_sound_timer(self, val):
        self.sound_timer_value = val

    def decrement_timers(self):
        """Decrementa os timers em 1 unidade, chamado a 60Hz no loop principal"""
        if self.delay_timer_value > 0:
            self.delay_timer_value -= 1

        if self.sound_timer_value > 0:
            self.sound_timer_value -= 1
            self.beep()

    def beep(self):
        """Toca um beep enquanto o sound timer estiver ativo"""
        pygame.mixer.music.load(self.sound_path)
        pygame.mixer.music.play()
