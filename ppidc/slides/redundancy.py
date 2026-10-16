import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import PxTable, default_config


class Redundancy(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()

        pxz_table = PxTable(
            cfg,
            4,
            3,
            [r"x=1", r"x=2", r"x=3", r"x=4"],
            [r"z=1", r"z=2", r"z=3"],
            corner_name=r"\mu(x,y)",
        )
        pxz_table.add_grid(cfg)
        table_xz = pxz_table.table
        _ = table_xz.scale_to_fit_width(5)
        _ = table_xz.move_to(mn.ORIGIN + mn.LEFT)
        pxz_title = (
            mn.MathTex(r"P(X,Z)", fill_color=cfg.txt_color)
            .next_to(table_xz, mn.UP, buff=0.3)
            .scale(0.8)
        )

        pyz_table = PxTable(
            cfg,
            3,
            3,
            [r"y=1", r"y=2", r"y=3"],
            [r"z=1", r"z=2", r"z=3"],
            corner_name=r"\mu(x,y)",
        )
        pyz_table.add_grid(cfg)
        table_yz = pyz_table.table
        _ = table_yz.scale_to_fit_width(5)
        _ = table_yz.move_to(mn.ORIGIN + mn.RIGHT)
        pyz_title = (
            mn.MathTex(r"P(X,Y)", fill_color=cfg.txt_color)
            .next_to(table_xz, mn.UP, buff=0.3)
            .scale(0.8)
        )

        pz_table = PxTable(
            cfg,
            1,
            3,
            [r"p(z)"],
            [r"z=1", r"z=2", r"z=3"],
        )
        pz_table.add_grid(cfg)
        pz_marginal = pz_table.table
        _ = pz_marginal.scale_to_fit_width(table_yz.width)
        _ = pz_marginal.next_to(table_yz, mn.DOWN + mn.LEFT, buff=0.35)
        pz_title = (
            mn.MathTex(r"P(Z)", fill_color=cfg.txt_color)
            .next_to(pz_marginal, mn.LEFT, buff=0.3)
            .scale(0.8)
        )

        self.play(
            mn.Create(table_xz),
            mn.Write(pxz_title),
            mn.Create(table_yz),
            mn.Write(pyz_title),
            mn.Create(pz_marginal),
            mn.Write(pz_title),
        )
        self.wait()
