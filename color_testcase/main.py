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
WHITE_BORDER_SIZE = 10
COLOR_CHANGE_AMOUNT = 0.01


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
        self.filter = normed(gaussian(self.spec_width, 0.2, 0.0))
        self.update_needed = False
        self.gauss_pos = 0
        self.gauss_filter_pos = 0
        self.use_filter = False
        self.normalize_brightness = False
        self.normalize_spec_brightness = False

        self.pressed = False

        self.normalized_colors = []
        self.colors = []
        for i in range(self.spec_width):
            spec = np.zeros(self.spec_width)
            spec[i] = 1
            normalized_color = (self.cs.spec_to_rgb(spec, normalize=True) * 255).astype(int)
            self.normalized_colors.append(pg.Color(normalized_color))
            color = (self.cs.spec_to_rgb(spec, normalize=False) * 255).astype(int)
            color = np.minimum(color * 0.2, 255).astype(int)
            self.colors.append(color)

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

    def render_spec(self, spec, color_factor=1.0):
        left_bin_xpos = PADDING_LEFT
        for i, spec_bin in enumerate(spec):
            right_bin_xpos = PADDING_LEFT + (i+1) / len(spec) * SPEC_WIDTH
            color = self.normalized_colors[i] if self.normalize_spec_brightness else self.colors[i]
            color = pg.Color([int(c*color_factor) for c in color])
            bin_height = spec_bin * SPEC_HEIGHT
            bottom = DEFAULT_SCREEN_SIZE[1] - PADDING_TOP
            top = bottom - bin_height
            rect = pg.Rect(left_bin_xpos, top, right_bin_xpos - left_bin_xpos + 1, bin_height)
            pg.draw.rect(self.screen, color, rect)

            left_bin_xpos = right_bin_xpos

    def render(self):
        self.screen.fill(pg.Color(0, 0, 0))

        # render spec
        color_factor = 0.5 if self.use_filter else 1.0
        self.render_spec(self.spec, color_factor)

        if self.use_filter:
            # render filtered spec
            self.render_spec(self.spec * self.filter)
            # render filter
            left_bin_xpos = PADDING_LEFT
            for i, filter_bin in enumerate(self.filter):
                right_bin_xpos = PADDING_LEFT + (i+1) / len(self.spec) * SPEC_WIDTH
                color = pg.Color(255, 255, 255)  # - self.colors[i]
                bin_height = filter_bin * SPEC_HEIGHT
                bottom = DEFAULT_SCREEN_SIZE[1] - PADDING_TOP
                top = bottom - bin_height
                pg.draw.line(self.screen, color, (left_bin_xpos, top), (right_bin_xpos, top))
                pg.draw.line(self.screen, pg.Color(0, 0, 0), (left_bin_xpos, top-1), (right_bin_xpos, top-1))

                left_bin_xpos = right_bin_xpos

        # render color
        spec = self.spec * self.filter if self.use_filter else self.spec
        color = self.cs.spec_to_rgb(spec, normalize=self.normalize_brightness) * 255
        color = np.minimum(color / (1 if self.normalize_brightness else 32), 255).astype(int)
        pg.draw.rect(
            self.screen, pg.Color(255, 255, 255),
            pg.Rect(SPEC_WIDTH + PADDING_LEFT + 50 + 60, 200 - WHITE_BORDER_SIZE, 60 + WHITE_BORDER_SIZE, 120 + 2 * WHITE_BORDER_SIZE)
        )
        pg.draw.rect(self.screen, color, pg.Rect(SPEC_WIDTH + PADDING_LEFT + 50, 200, 120, 120))

        font = self.render_font.render(
            'RGB: ({}, {}, {})'.format(color[0], color[1], color[2]),
            True, pg.Color(220, 220, 220), pg.Color(0, 0, 0, 0)
        )
        self.screen.blit(font, (SPEC_WIDTH + PADDING_LEFT + 50, 200+120+40))
        normalize_font = self.render_font.render(
            'normalized' if self.normalize_brightness else 'not normalized',
            True, pg.Color(220, 220, 220), pg.Color(0, 0, 0, 0)
        )
        self.screen.blit(normalize_font, (SPEC_WIDTH + PADDING_LEFT + 50, 200+120+70))

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
            if text == 'f':
                self.use_filter = not self.use_filter
            elif text == 'n':
                self.normalize_brightness = not self.normalize_brightness
            elif text == 'N':
                self.normalize_spec_brightness = not self.normalize_spec_brightness
            # modify spec
            elif text and text in '1234567890':
                if text == '0':
                    freq = 10000
                else:
                    freq = int(text) * 1000
                self.spec = normed(planck(self.lam, freq))
            elif text == 's':
                self.spec = normed(planck(self.lam, 6600))
            elif text == 'c':
                self.spec = normed(gaussian(self.spec_width, 0.2, -0.43))
                self.gauss_pos = -0.43
            elif text == 'y':
                self.spec = normed(gaussian(self.spec_width, 0.2, -0.05))
                self.gauss_pos = -0.05
            elif text == 'm':
                self.spec = normed(gaussian(self.spec_width, 0.2, -0.7))
                self.spec += normed(gaussian(self.spec_width, 0.2, 0.4))
                self.gauss_pos = 0.4
            elif text == 'k':
                self.spec = np.zeros(self.spec_width)
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
                self.gauss_pos = min(self.gauss_pos + COLOR_CHANGE_AMOUNT, 1.5)
                self.spec = normed(gaussian(self.spec_width, 0.2, self.gauss_pos))
            elif text == '-':
                self.gauss_pos = max(self.gauss_pos - COLOR_CHANGE_AMOUNT, -1.5)
                self.spec = normed(gaussian(self.spec_width, 0.2, self.gauss_pos))
            # modify filter
            elif text and text in '!"§$%&/()=':
                freq = np.arange(1, 11)['!"§$%&/()='.index(text)] * 1000
                self.filter = normed(planck(self.lam, freq))
            elif text == 'S':
                self.filter = normed(planck(self.lam, 6600))
            elif text == 'C':
                self.filter = normed(gaussian(self.spec_width, 0.2, -0.43))
                self.gauss_filter_pos = -0.43
            elif text == 'Y':
                self.filter = normed(gaussian(self.spec_width, 0.2, -0.05))
                self.gauss_filter_pos = -0.05
            elif text == 'M':
                self.filter = normed(gaussian(self.spec_width, 0.2, -0.7))
                self.filter += normed(gaussian(self.spec_width, 0.2, 0.4))
                self.gauss_filter_pos = 0.4
            elif text == 'K':
                self.filter = np.zeros(self.spec_width)
            elif text == 'R':
                self.filter = normed(gaussian(self.spec_width, 0.2, 0.44))
                self.gauss_filter_pos = 0.44
            elif text == 'G':
                self.filter = normed(gaussian(self.spec_width, 0.2, -0.17))
                self.gauss_filter_pos = -0.17
            elif text == 'B':
                self.filter = normed(gaussian(self.spec_width, 0.2, -0.74))
                self.gauss_filter_pos = -0.74
            elif text == '*':
                self.gauss_filter_pos = min(self.gauss_filter_pos + COLOR_CHANGE_AMOUNT, 1.5)
                self.filter = normed(gaussian(self.spec_width, 0.2, self.gauss_filter_pos))
            elif text == '_':
                self.gauss_filter_pos = max(self.gauss_filter_pos - COLOR_CHANGE_AMOUNT, -1.5)
                self.filter = normed(gaussian(self.spec_width, 0.2, self.gauss_filter_pos))
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
            if pg.key.get_mods() & (pg.KMOD_SHIFT | pg.KMOD_LSHIFT):
                self.filter[spec_index] = height
            else:
                self.spec[spec_index] = height

        self.update_needed = True


def main():
    main_instance = Main()
    main_instance.run()
    pg.quit()


if __name__ == '__main__':
    main()
