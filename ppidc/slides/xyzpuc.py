import typing as t

import manim as mn
from manim_themes import manim_theme as mtheme

from ppidc import default_config


class PUC(mn.Scene):
    @t.override
    def setup(self) -> None:
        self.cfg = default_config()
        mtheme.apply_theme(self, theme_name=self.cfg.manim_theme)

    @t.override
    def construct(self) -> None:
        x_pt = 3 * mn.LEFT
        y_pt = 3 * mn.RIGHT
        line_xy = mn.Line(x_pt, y_pt).set_color(self.cfg.txt_color)
        x_label = mn.MathTex("X", fill_color=self.cfg.txt_color).next_to(
            line_xy.get_start(), mn.LEFT
        )
        y_label = mn.MathTex("Y", fill_color=self.cfg.txt_color).next_to(
            line_xy.get_end(), mn.RIGHT
        )

        z_pt = line_xy.get_midpoint() + 2 * mn.UP
        z_dot = mn.Dot(z_pt, color=self.cfg.txt_color)
        z_label = mn.MathTex("Z", fill_color=self.cfg.txt_color).next_to(
            z_dot, mn.UP
        )
        z_circle = mn.Circle(
            radius=0.5, color=self.cfg.txt_color
        ).move_to(z_pt)

        self.play(mn.Create(line_xy), mn.Write(x_label), mn.Write(y_label))
        self.next_section()
        self.play(mn.Create(z_dot), mn.Write(z_label))
        self.next_section()
        self.play(mn.Create(z_circle))
        self.wait()
