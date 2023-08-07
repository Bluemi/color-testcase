#!/usr/bin/env python3


import numpy as np
import pygame as pg

from color_system import cs_srgb
from black_bodies import planck


DEFAULT_SCREEN_SIZE = (1000, 600)
SPEC_WIDTH = DEFAULT_SCREEN_SIZE[0] - 300
SPEC_HEIGHT = DEFAULT_SCREEN_SIZE[1] - 100
PADDING_LEFT = 50
PADDING_TOP = (DEFAULT_SCREEN_SIZE[1] - SPEC_HEIGHT) // 2


def gaussian(n, sigma, m):
    x = np.linspace(-1, 1, n)
    return 1 / np.sqrt(2 * np.pi * sigma ** 2) * np.exp(-((x - m)**2 / (2 * sigma**2)))


def normed(spec):
    return spec / np.max(spec)


class Main:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
        self.render_font = pg.font.Font(pg.font.get_default_font(), 18)

        self.running = True
        self.cs = cs_srgb
        self.lam = np.arange(380., 781., 5)
        self.spec_width = len(self.lam)
        self.spec = normed(planck(self.lam, 6000))
        self.update_needed = False
        self.gauss_pos = 0

        self.pressed = False

        self.colors = []
        for i in range(self.spec_width):
            spec = np.zeros(self.spec_width)
            spec[i] = 1
            color = (self.cs.spec_to_rgb(spec) * 255).astype(int)
            self.colors.append(pg.Color(color))

    def run(self):
        self.render()
        while self.running:
            # event handling
            events = [pg.event.wait()]
            events = events + pg.event.get()
            self.handle_events(events)

            # render
            if self.update_needed:
                self.render()
                self.update_needed = False

        pg.quit()

    def render(self):
        self.screen.fill(pg.Color(0, 0, 0))
        # render spec
        left_bin_xpos = PADDING_LEFT
        for i, spec_bin in enumerate(self.spec):
            right_bin_xpos = PADDING_LEFT + (i+1) / len(self.spec) * SPEC_WIDTH
            color = self.colors[i]
            bin_height = spec_bin * SPEC_HEIGHT
            bottom = DEFAULT_SCREEN_SIZE[1] - PADDING_TOP
            top = bottom - bin_height
            rect = pg.Rect(left_bin_xpos, top, right_bin_xpos - left_bin_xpos + 1, bin_height)
            pg.draw.rect(self.screen, color, rect)

            left_bin_xpos = right_bin_xpos

        # render color
        color = (self.cs.spec_to_rgb(self.spec) * 255).astype(int)
        pg.draw.rect(self.screen, color, pg.Rect(SPEC_WIDTH + PADDING_LEFT + 50, 200, 120, 120))

        font = self.render_font.render(
            'RGB: ({}, {}, {})'.format(color[0], color[1], color[2]),
            True, pg.Color(220, 220, 220), pg.Color(0, 0, 0, 0)
        )
        self.screen.blit(font, (SPEC_WIDTH + PADDING_LEFT + 50, 200+120+20))

        pg.display.flip()

    def handle_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.pressed = True
            self.set_bin()
        elif event.type == pg.MOUSEBUTTONUP:
            self.pressed = False
        elif event.type == pg.MOUSEMOTION:
            if self.pressed:
                self.set_bin()
        elif event.type in (pg.WINDOWENTER, pg.WINDOWSHOWN, pg.WINDOWFOCUSGAINED):
            self.update_needed = True
        elif event.type == pg.TEXTINPUT:
            text = event.text.strip()
            if text and text in '1234567890':
                if text == '0':
                    freq = 10000
                else:
                    freq = int(text) * 1000
                self.spec = normed(planck(self.lam, freq))
            elif text == 'c':
                self.spec = normed(gaussian(self.spec_width, 0.2, -0.43))
                self.gauss_pos = -0.43
            elif text == 'y':
                self.spec = normed(gaussian(self.spec_width, 0.2, -0.05))
                self.gauss_pos = -0.05
            elif text == 'm':
                self.spec = normed(gaussian(self.spec_width, 0.2, -1))
                self.spec += normed(gaussian(self.spec_width, 0.2, 0.6))
                self.gauss_pos = 0.6
            elif text == 'r':
                self.spec = normed(gaussian(self.spec_width, 0.2, 0.44))
                self.gauss_pos = 0.44
            elif text == 'g':
                self.spec = normed(gaussian(self.spec_width, 0.1, -0.17))
                self.gauss_pos = -0.17
            elif text == 'b':
                self.spec = normed(gaussian(self.spec_width, 0.2, -0.74))
                self.gauss_pos = -0.74
            elif text == '+':
                self.gauss_pos = min(self.gauss_pos + 0.02, 1)
                self.spec = normed(gaussian(self.spec_width, 0.2, self.gauss_pos))
            elif text == '-':
                self.gauss_pos = max(self.gauss_pos - 0.02, -1)
                self.spec = normed(gaussian(self.spec_width, 0.2, self.gauss_pos))
            self.update_needed = True
        elif event.type == pg.KEYDOWN:
            if event.key == 27:
                self.running = False

    def set_bin(self):
        mouse_pos = np.array(pg.mouse.get_pos())
        if PADDING_LEFT <= mouse_pos[0] < PADDING_LEFT + SPEC_WIDTH:
            # if PADDING_TOP <= mouse_pos[1] < PADDING_TOP + SPEC_HEIGHT:
            spec_index = int((mouse_pos[0] - PADDING_LEFT) / SPEC_WIDTH * len(self.spec))
            spec_index = min(spec_index, len(self.spec)-1)
            height = 1 - (mouse_pos[1] - PADDING_TOP) / SPEC_HEIGHT
            height = min(max(height, 0), 1)
            self.spec[spec_index] = height

        self.update_needed = True


def main():
    main_instance = Main()
    main_instance.run()
    pg.quit()


if __name__ == '__main__':
    main()
