import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import PxTable, default_config, scene_header, theme_background


_TEX_RED = r" \sum_y p(y) \min(I_s(y;X), I_s(y;Z))"
_TABLE_WIDTH : float = 4.0
_TABLE_HEIGHT : float = 3.0

class Redundancy(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        header_txt = scene_header("Redundancy and Unique Contribution", cfg)

        mx_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; X)"],
        )
        mx_table.add_grid(cfg)
        _ = mx_table.table.scale_to_fit_height(_TABLE_HEIGHT)
        _ = mx_table.table.move_to(5 * mn.LEFT + mn.UP)

        mz_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; Z)"],
        )
        mz_table.add_grid(cfg)
        _ = mz_table.table.scale_to_fit_height(_TABLE_HEIGHT)
        _ = mz_table.table.next_to(mx_table.table, mn.RIGHT, buff=0.3)


        minxz_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"\min(I_s(y; Z), I_s(y; Z))"],
        )
        minxz_table.add_grid(cfg)
        _ = minxz_table.table.scale_to_fit_height(_TABLE_HEIGHT)
        _ = minxz_table.table.next_to(mz_table.table, mn.RIGHT, buff=1.2)


        red_txt = mn.MathTex(_TEX_RED, fill_color=cfg.txt_color)
        _ = red_txt.next_to(minxz_table.table, mn.DOWN, buff = 0.3)
        self.play(mn.Create(header_txt))
        self.play(
            mn.Create(mx_table.table),
            mn.Create(mz_table.table),
        )
        self.next_section()
        self.play(
            mn.Create(minxz_table.table),
        )
        self.wait()
        self.play(
            mn.Write(red_txt),
        )
