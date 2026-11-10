import typing as t

import manim as mn
from manim.mobject.types.vectorized_mobject import VMobject
from manim_themes import manim_theme as mtheme

from ppidc import PxTable, default_config, scene_header, theme_background

_TEX_RED = r"\sum_y p(y) \min(I_s(y;X), I_s(y;Z))"
_TEX_RHO = r"\rho((X, Z); Y) = "
_TEX_PID = r"\nu((X, Z); Y) = I(X, Z) - \rho((X, Z); Y)"
_TABLE_WIDTH: float = 4.0
_TABLE_HEIGHT: float = 3.0
_TEXT_WIDTH: float = 4.5
_RHO_WIDTH: float = 2.0


class Redundancy(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        header_txt = scene_header("Redundancy and Unique Contribution", cfg)
        py_values = [0.3, 0.4, 0.3]
        x_values = [1.12, 2.22, 0.85]
        z_values = [3.38, 1.29, 1.35]
        min_values = [min(x, z) for x, z in zip(x_values, z_values, strict=True)]

        mx_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; X)"],
            body=[[f"{value:.2f}"] for value in x_values],
        )
        mx_table.add_grid(cfg)
        _ = mx_table.table.scale_to_fit_height(_TABLE_HEIGHT)
        _ = mx_table.table.move_to(5 * mn.LEFT + 1.2 * mn.UP)

        mz_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; Z)"],
            body=[[f"{value:.2f}"] for value in z_values],
        )
        mz_table.add_grid(cfg)
        _ = mz_table.table.scale_to_fit_height(_TABLE_HEIGHT)
        _ = mz_table.table.next_to(mx_table.table, mn.RIGHT, buff=0.3)

        py_table = PxTable(
            cfg,
            1,
            3,
            [r"p(y)"],
            [r"y=1", r"y=2", r"y=3"],
            body=[[f"{value:.2f}" for value in py_values]],
        )
        py_table.add_grid(cfg)
        _ = py_table.table.scale_to_fit_width(1.25 * _TABLE_WIDTH)
        _ = py_table.table.next_to(mx_table.table, mn.DOWN, buff=0.3).shift(
            0.6 * mn.RIGHT
        )
        py_cells = t.cast(
            list[VMobject], [py_table.cell(0, column) for column in range(3)]
        )

        minxz_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"\min(I_s(y; X), I_s(y; Z))"],
            body=[[f"{value:.2f}"] for value in min_values],
        )
        minxz_table.add_grid(cfg)
        _ = minxz_table.table.scale_to_fit_height(_TABLE_HEIGHT)
        _ = minxz_table.table.next_to(mz_table.table, mn.RIGHT, buff=1.2)
        # Keep references to all values before hiding them from the initial
        # table; cell() needs the complete table for its row lookup.
        min_cells = t.cast(
            list[VMobject], [minxz_table.cell(row, 0) for row in range(3)]
        )
        min_entries = minxz_table.table.get_entries()
        for cell in min_cells:
            min_entries.remove(cell)  # pyright: ignore[reportUnusedCallResult]

        x_boxes = [
            mn.SurroundingRectangle(
                mx_table.cell(row, 0), color=mn.RED, stroke_width=4, buff=0.06
            )
            for row in range(3)
        ]
        z_boxes = [
            mn.SurroundingRectangle(
                mz_table.cell(row, 0), color=mn.BLUE, stroke_width=4, buff=0.06
            )
            for row in range(3)
        ]

        red_txt = mn.MathTex(_TEX_RED, fill_color=cfg.txt_color).scale_to_fit_width(
            minxz_table.table.width
        )
        _ = red_txt.next_to(minxz_table.table, mn.DOWN, buff=0.3)
        rho_txt = mn.MathTex(_TEX_RHO, fill_color=cfg.txt_color).scale_to_fit_width(
            _RHO_WIDTH
        )
        _ = rho_txt.next_to(red_txt, mn.LEFT, buff=0.5)

        pid_txt = mn.MathTex(_TEX_PID, fill_color=cfg.txt_color)
        _ = pid_txt.move_to(3 * mn.DOWN)
        self.play(mn.Create(header_txt))
        self.play(
            mn.Create(py_table.table),
            mn.Create(mx_table.table),
            mn.Create(mz_table.table),
        )
        self.next_section()
        self.play(mn.Create(minxz_table.table))
        self.next_section()
        self.play(*(mn.Create(box) for box in [*x_boxes, *z_boxes]))
        result_boxes: list[mn.SurroundingRectangle] = []
        for row in range(3):
            result_box = mn.SurroundingRectangle(
                min_cells[row], color=mn.ORANGE, stroke_width=4, buff=0.06
            )
            # Work on copies so all three source pairs remain highlighted.
            # Opposite arcs keep the incoming boxes apart as they converge.
            x_fly = x_boxes[row].copy()
            z_fly = z_boxes[row].copy()
            self.play(
                mn.Transform(x_fly, result_box, path_arc=mn.PI / 6),
                mn.Transform(z_fly, result_box.copy(), path_arc=-mn.PI / 6),
                run_time=1.5,
            )
            # x_fly has become the result box; retire the duplicate Z copy.
            self.remove(z_fly)  # pyright: ignore[reportUnusedCallResult]
            result_boxes.append(x_fly)
            self.play(mn.Write(min_cells[row]))
            self.next_section()

        # Replace the per-row highlights with one box around the values, but
        # leave the values themselves visible for the summation.
        self.play(mn.FadeOut(mn.VGroup(*result_boxes)))
        min_group_box = mn.SurroundingRectangle(
            mn.VGroup(*min_cells), color=mn.GREEN, stroke_width=4, buff=0.12
        )
        py_group_box = mn.SurroundingRectangle(
            mn.VGroup(*py_cells), color=mn.GREEN, stroke_width=4, buff=0.12
        )
        min_total = mn.MathTex(
            f"{sum(py * mx for py, mx in zip(py_values, min_values)):.2f}",
            fill_color=cfg.txt_color,
        )
        _ = min_total.scale(0.8).next_to(min_group_box, mn.RIGHT, buff=0.2)
        self.play(
            mn.Create(min_group_box), mn.Create(py_group_box), mn.Write(min_total)
        )
        self.next_section()
        red_box = mn.SurroundingRectangle(
            red_txt, color=mn.GREEN, stroke_width=4, buff=0.12
        )
        self.play(mn.Write(red_txt), mn.Create(red_box))
        self.next_section()
        pid_box = mn.SurroundingRectangle(
            pid_txt, color=cfg.txt_color, stroke_width=4, buff=0.12
        )
        self.play(mn.Write(rho_txt))
        self.next_section()
        self.play(mn.Write(pid_txt), mn.Create(pid_box))
        self.wait()
