#!/usr/bin/env python3


import numpy as np
import pygame as pg

from color_system import cs_hdtv, cs_srgb, cs_smpte
from black_bodies import planck


DEFAULT_SCREEN_SIZE = (1000, 600)
SPEC_WIDTH = DEFAULT_SCREEN_SIZE[0] - 300
SPEC_HEIGHT = DEFAULT_SCREEN_SIZE[1] - 100
PADDING_LEFT = 50
PADDING_TOP = (DEFAULT_SCREEN_SIZE[1] - SPEC_HEIGHT) // 2


class Main:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
        self.running = True
        # self.cs = cs_hdtv
        self.cs = cs_srgb
        # self.cs = cs_smpte
        self.lam = np.arange(380., 781., 5)
        self.spec = planck(self.lam, 6000)
        self.spec_max = np.max(self.spec) * 4
        self.update_needed = False

        self.pressed = False

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
            new_spec = np.zeros(len(self.spec))
            new_spec[i] = self.spec[i]
            color = (self.cs.spec_to_rgb(new_spec) * 255).astype(int)
            color = pg.Color(color)  # TODO: precompute colors
            bin_height = spec_bin / self.spec_max * SPEC_HEIGHT
            bottom = DEFAULT_SCREEN_SIZE[1] - PADDING_TOP
            top = bottom - bin_height
            rect = pg.Rect(left_bin_xpos, top, right_bin_xpos - left_bin_xpos + 1, bin_height)
            pg.draw.rect(self.screen, color, rect)

            left_bin_xpos = right_bin_xpos

        # render color
        color = (self.cs.spec_to_rgb(self.spec) * 255).astype(int)
        pg.draw.rect(self.screen, color, pg.Rect(SPEC_WIDTH + PADDING_LEFT + 50, 200, 120, 120))

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
        elif event.type == pg.KEYDOWN:
            unicode = event.unicode.strip()
            if unicode and unicode in '4567':
                freq = int(unicode) * 1000
                self.spec = planck(self.lam, freq)
            self.update_needed = True

    def set_bin(self):
        mouse_pos = np.array(pg.mouse.get_pos())
        if PADDING_LEFT <= mouse_pos[0] < PADDING_LEFT + SPEC_WIDTH:
            if PADDING_TOP <= mouse_pos[1] < PADDING_TOP + SPEC_HEIGHT:
                spec_index = int((mouse_pos[0] - PADDING_LEFT) / SPEC_WIDTH * len(self.spec))
                spec_index = min(spec_index, len(self.spec)-1)
                height = (1 - (mouse_pos[1] - PADDING_TOP) / SPEC_HEIGHT) * self.spec_max
                self.spec[spec_index] = height

        self.update_needed = True


def main():
    main_instance = Main()
    main_instance.run()
    pg.quit()


if __name__ == '__main__':
    main()
