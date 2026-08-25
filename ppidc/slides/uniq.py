import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import default_config


class UniqInfo(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        x_pt = 3 * mn.LEFT + 1 * mn.DOWN
        y_pt = 3 * mn.RIGHT + 1 * mn.DOWN
        line_xy = mn.Line(x_pt, y_pt).set_color(cfg.txt_color)
        mid_xy = line_xy.get_midpoint()
        x_dot = mn.Dot(x_pt, color=cfg.txt_color)
        y_dot = mn.Dot(y_pt, color=cfg.txt_color)
        x_label = mn.MathTex("X", fill_color=cfg.txt_color).next_to(
            line_xy.get_start(), mn.LEFT
        )
        y_label = mn.MathTex("Y", fill_color=cfg.txt_color).next_to(
            line_xy.get_end(), mn.RIGHT
        )
        z_pt = mid_xy + 3 * mn.UP
        z_dot = mn.Dot(z_pt, color=cfg.txt_color)
        self.play(
            mn.Create(line_xy),
            mn.Create(x_dot),
            mn.Create(y_dot),
            mn.Write(x_label),
            mn.Write(y_label),
            mn.Write(z_dot),
        )
        self.next_section()
