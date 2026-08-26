import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import Config, default_config


class PxTable:
    table: mn.Table
    def __init__(self,
            cfg: Config,
            n_rows: int,
            n_cols: int,
            row_names: list[str],
            col_names: list[str]
    ) -> None:
        assert(len(col_names) == n_cols)
        assert(len(row_names) == n_rows)
        t_entries = [["·" for y in range(n_cols+1)] for x in range(n_rows+1)]
        #t_entries[0][0] = "X" # "?·3"
        t_entries[0][1:] = col_names
        for rx, r_name in zip(range(n_rows), row_names):
            t_entries[rx+1][0] = r_name

        table = mn.Table(
            t_entries,
            include_inner_lines=False,
            include_outer_lines=True,
            element_to_mobject_config={"color": cfg.txt_color},
        )
        self.table  = table

    def h_line(self, y: float, width: int, cfg: Config) -> mn.Line:
        r_left: tuple[float, float, float] =  (
            float(self.table.get_left()[0]), y, 0.0
        )
        r_right: tuple[float, float, float] = (
            float(self.table.get_right()[0]), y, 0
        )
        return mn.Line(
            r_left,  r_right, color=cfg.txt_color, stroke_width=width,
        )

    def v_line(self, x: float, width: int, cfg: Config) -> mn.Line:
        return mn.Line(
            [x, self.table.get_top()[1], 0],
            [x, self.table.get_bottom()[1], 0],
            color=cfg.txt_color, stroke_width=width,
        )

    def add_grid(self, cfg: Config) -> None:
        """Draw every grid line of the table: strong (width 6) for the
        outer border, the header-row separator, and the first-column
        separator; thin (width 2) for all remaining inner lines."""
        entries = self.table.get_entries()
        # group cells by row via their y-coordinate (robust, no label API needed)
        rows: dict[float, list[mn.Mobject]] = {}
        for e in entries:
            y = round(float(e.get_center()[1]), 6)
            rows.setdefault(y, []).append(e)
        ys = sorted(rows.keys(), reverse=True)
        for row in rows.values():
            row.sort(key=lambda e: float(e.get_center()[0]))

        thin, strong = 2, 6

        # all horizontal boundaries: outer top/bottom + one between each row pair
        row_borders: list[float] = [rows[ys[0]][0].get_top()[1]] + [
            (rows[ys[i]][0].get_bottom()[1] + rows[ys[i+1]][0].get_top()[1]) / 2
            for i in range(len(ys) - 1)
        ] + [rows[ys[-1]][0].get_bottom()[1]]
        # all vertical boundaries: outer left/right + one between each column pair
        header_row = rows[ys[0]]
        col_borders: list[float] = [header_row[0].get_left()[0]] + [
            (header_row[i].get_right()[0] + header_row[i+1].get_left()[0]) / 2
            for i in range(len(header_row) - 1)
        ] + [header_row[-1].get_right()[0]]

        # indices 0 and len-1 are the outer border; index 1 is the header
        # row / first column separator — those are strong, the rest thin
        grid = mn.VGroup(
            *(self.h_line(y, thin, cfg)
              for _i, y in enumerate(row_borders[1:2])),
            *(self.v_line(x, thin, cfg)
              for _i, x in enumerate(col_borders[1:2])),
        )
        _ = self.table.add(grid)


class SpecificInfo(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        x_pt = 3 * mn.LEFT
        y_pt = 3 * mn.RIGHT
        line_xy = mn.Line(x_pt, y_pt).set_color(cfg.txt_color)
        mid_xy = line_xy.get_midpoint()
        x_dot = mn.Dot(x_pt, color=cfg.txt_color)
        y_dot = mn.Dot(y_pt, color=cfg.txt_color)
        z_pt = mid_xy + 3 * mn.UP
        z_dot = mn.Dot(z_pt, color=cfg.txt_color)
        x_label = mn.MathTex("X", fill_color=cfg.txt_color).next_to(
            line_xy.get_start(), mn.LEFT
        )
        y_label = mn.MathTex("Y", fill_color=cfg.txt_color).next_to(
            line_xy.get_end(), mn.RIGHT
        )
        z_label = mn.MathTex("Z", fill_color=cfg.txt_color).next_to(
            z_pt, mn.UP
        )

        px_table = PxTable(
            cfg, 4, 3, ["x=1", "x=2", "x=3", "x=4"], ["y=1", "y=2", "y=3"] ,
        )
        px_table.add_grid(cfg)
        table = px_table.table
        _ = table.scale_to_fit_width(5)
        _ = table.move_to(mid_xy + 0.0 * mn.DOWN)
        self.play(
            mn.Create(x_dot),
            mn.Create(y_dot),
            mn.Write(x_label),
            mn.Write(y_label),
        )
        self.next_section()
        self.play(mn.Create(table))
        self.next_section()
        self.wait()
