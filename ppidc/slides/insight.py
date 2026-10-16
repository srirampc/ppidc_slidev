import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import PxTable, default_config


class AlgoInsight(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()

        mx_table = PxTable(
            cfg,
            4,
            1,
            [r"x=1", r"x=2", r"x=3", r"x=4"],
            [r"\mu(x)"],
        )
        mx_table.add_grid(cfg)
        table_mx = mx_table.table
        _ = table_mx.scale_to_fit_width(5)
        _ = table_mx.move_to(mn.RIGHT)

        mx_title = (
            mn.MathTex(r"\mu(X,Z)", fill_color=cfg.txt_color)
            .next_to(table_mx, mn.UP, buff=0.3)
            .scale(0.8)
        )


        self.play(
            mn.Create(table_mx),
            mn.Write(mx_title),
        )
        self.wait()
