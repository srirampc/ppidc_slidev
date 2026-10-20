import typing as t

import manim as mn
from manim_themes import manim_theme as mtheme

from ppidc import PxTable, default_config


class AlgoInsight(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()

        sum_n = (
            mn.MathTex(
                r"\sum_Z \sum_y p(y) \min(I_s(y;X), I_s(y;Z))",
                fill_color=cfg.txt_color
            )
            .move_to(3.5 * mn.LEFT + 1.8 * mn.UP)
            .scale(0.8)
        )

        mx_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; X)"],
        )
        mx_table.add_grid(cfg)
        _ = mx_table.table.scale_to_fit_width(2.5)
        _ = mx_table.table.move_to(0.8 * mn.RIGHT + 1.8 * mn.UP)

        mz_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; Z)"],
        )
        mz_table.add_grid(cfg)
        _ = mz_table.table.scale_to_fit_width(2.5)
        _ = mz_table.table.next_to(mx_table.table, mn.RIGHT, buff=0.3)

        mx_dots_mid = (
            mn.MathTex(r"\cdots", fill_color=cfg.txt_color)
            .next_to(mz_table.table, mn.RIGHT, buff=0.3)
            .scale(0.8)
        )

        mx_dots_end = (
            mn.MathTex(r"\cdots", fill_color=cfg.txt_color)
            .next_to(mx_dots_mid, mn.RIGHT, buff=0.3)
            .scale(0.8)
        )
        top_brace = mn.BraceBetweenPoints(
            mz_table.table.get_top() + 1.2 * mn.LEFT,
            mz_table.table.get_top() + 2.8 * mn.RIGHT,
            direction=mn.UP,
        )
        br_size = (
            mn.MathTex(r"n-2", fill_color=cfg.txt_color)
            .next_to(top_brace, mn.UP, buff=0.1)
            .scale(0.8)
        )

        sum_flip = (
            mn.MathTex(
                r"\sum_y \sum_Z \min(p(y) I_s(y;X), p(y) I_s(y;Z))",
                fill_color=cfg.txt_color
            )
            .next_to(sum_n, mn.DOWN, buff=1.2)
            .scale(0.7)
        )

        sum_mu = (
            mn.MathTex(
                r"\sum_y \sum_Z \min(\mu(y;X), \mu(y;Z))",
                fill_color=cfg.txt_color
            )
            .next_to(sum_flip, mn.DOWN, buff=1.2)
            .scale(0.7)
        )


        vm1_table = PxTable(
            cfg,
            5,
            1,
            [r"X", r"\vdots", r"Z", r"\vdots", r"\vdots"],
            [r"\mu(1; \cdot)"],
        )
        vm1_table.add_grid(cfg)
        _ = vm1_table.table.scale_to_fit_width(2.5)
        _ = vm1_table.table.move_to(mn.RIGHT + 1.8 * mn.DOWN)

        vm2_table = PxTable(
            cfg,
            5,
            1,
            [r"X", r"\vdots", r"Z", r"\vdots", r"\vdots"],
            [r"\mu(2; \cdot)"],
        )
        vm2_table.add_grid(cfg)
        _ = vm2_table.table.scale_to_fit_width(2.5)
        _ = vm2_table.table.next_to(vm1_table.table, mn.RIGHT, buff=0.3)

        vm3_table = PxTable(
            cfg,
            5,
            1,
            [r"X", r"\vdots", r"Z", r"\vdots", r"\vdots"],
            [r"\mu(3; \cdot)"],
        )
        vm3_table.add_grid(cfg)
        _ = vm3_table.table.scale_to_fit_width(2.5)
        _ = vm3_table.table.next_to(vm2_table.table, mn.RIGHT, buff=0.3)

        self.play(
           mn.Write(sum_n),
        )
        self.wait()
        self.next_section()
        self.play(
            mn.Create(mx_table.table),
            mn.Write(mx_dots_mid),
            mn.Write(mx_dots_end),
            mn.Create(mz_table.table),
            mn.Create(top_brace),
            mn.Write(br_size),
        )
        self.wait()
        self.next_section()
        self.play(
           mn.Write(sum_flip),
           mn.Write(sum_mu),
        )
        self.wait()
        self.next_section()
        self.play(
            mn.Create(vm1_table.table),
            mn.Create(vm2_table.table),
            mn.Create(vm3_table.table),
        )
        self.wait()
