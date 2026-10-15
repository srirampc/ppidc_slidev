import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import Config, default_config

_EXPR_TEX = r"\frac{p(x,y)}{p(y)} \log \left( \frac{p(x,y)}{p(x)\cdot p(y)} \right)"


def _parts_by_tex(expr: mn.MathTex, tex: str) -> list[mn.VGroup]:
    """All occurrences of `tex` isolated within `expr`. manim tags each
    isolated occurrence as its own SVG group, but `get_part_by_tex()` only
    returns the first one."""
    return [
        expr.id_to_vgroup_dict[match_id]
        for tex_str, match_id in expr.matched_strings_and_ids
        if tex_str == tex
    ]


class PxTable:
    table: mn.Table

    def __init__(
        self,
        cfg: Config,
        n_rows: int,
        n_cols: int,
        row_names: list[str],
        col_names: list[str],
        corner_name: str | None = None,
    ) -> None:
        assert len(col_names) == n_cols
        assert len(row_names) == n_rows
        t_entries = [
            [mn.MathTex(r"\cdot", fill_color=cfg.txt_color) for _y in range(n_cols + 1)]
            for _x in range(n_rows + 1)
        ]
        if corner_name is not None:
            t_entries[0][0] = mn.MathTex(corner_name, fill_color=cfg.txt_color)
        t_entries[0][1:] = [
            mn.MathTex(col_name, fill_color=cfg.txt_color) for col_name in col_names
        ]
        for rx, r_name in zip(range(n_rows), row_names):
            t_entries[rx + 1][0] = mn.MathTex(r_name, fill_color=cfg.txt_color)

        mobj_gen: t.Callable[[mn.VMobject], mn.VMobject] = lambda m: m

        table = mn.Table(
            t_entries,
            # Entries are already Mobjects, so pass them through unchanged.
            element_to_mobject=mobj_gen,
            include_inner_lines=False,
            include_outer_lines=True,
            # element_to_mobject_config={"color": cfg.txt_color},
        )
        self.table = table

    def h_line(self, y: float, width: int, cfg: Config) -> mn.Line:
        return mn.Line(
            (float(self.table.get_left()[0]), y, 0.0),
            (float(self.table.get_right()[0]), y, 0),
            color=cfg.txt_color,
            stroke_width=width,
        )

    def v_line(self, x: float, width: int, cfg: Config) -> mn.Line:
        return mn.Line(
            (x, float(self.table.get_top()[1]), 0),
            (x, float(self.table.get_bottom()[1]), 0),
            color=cfg.txt_color,
            stroke_width=width,
        )

    def _grouped_entries(self) -> tuple[dict[float, list[mn.Mobject]], list[float]]:
        """Entries grouped by row: maps each row's y-coordinate to its cells
        sorted left to right, plus the row y's sorted top to bottom."""
        entries = self.table.get_entries()
        # group cells by row via their y-coordinate (robust, no label API needed)
        rows: dict[float, list[mn.Mobject]] = {}
        for e in entries:
            y = round(float(e.get_center()[1]), 6)
            rows.setdefault(y, []).append(e)
        ys = sorted(rows.keys(), reverse=True)
        for row in rows.values():
            row.sort(key=lambda e: float(e.get_center()[0]))
        return rows, ys

    def cell(self, row: int, col: int) -> mn.Mobject:
        """Entry at body row `row` and body column `col` (0-based from the
        top-left cell below/right of the header row and corner column)."""
        rows, ys = self._grouped_entries()
        return rows[ys[row + 1]][col + 1]

    def add_grid(self, cfg: Config) -> None:
        """Draw every grid line of the table: strong (width 6) for the
        outer border, the header-row separator, and the first-column
        separator; thin (width 2) for all remaining inner lines."""
        rows, ys = self._grouped_entries()

        thin, _strong = 2, 6

        # all horizontal boundaries: outer top/bottom + one between each row pair
        row_borders: list[float] = (
            [rows[ys[0]][0].get_top()[1]]
            + [
                (rows[ys[i]][0].get_bottom()[1] + rows[ys[i + 1]][0].get_top()[1]) / 2
                for i in range(len(ys) - 1)
            ]
            + [rows[ys[-1]][0].get_bottom()[1]]
        )
        # all vertical boundaries: outer left/right + one between each column pair
        header_row = rows[ys[0]]
        col_borders: list[float] = (
            [header_row[0].get_left()[0]]
            + [
                (header_row[i].get_right()[0] + header_row[i + 1].get_left()[0]) / 2
                for i in range(len(header_row) - 1)
            ]
            + [header_row[-1].get_right()[0]]
        )

        # indices 0 and len-1 are the outer border; index 1 is the header
        # row / first column separator — those are strong, the rest thin
        grid = mn.VGroup(
            *(self.h_line(y, thin, cfg) for _i, y in enumerate(row_borders[1:2])),
            *(self.v_line(x, thin, cfg) for _i, x in enumerate(col_borders[1:2])),
        )
        _ = self.table.add(grid)


class SpecificInfo(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()

        pxy_table = PxTable(
            cfg,
            4,
            3,
            [r"x=1", r"x=2", r"x=3", r"x=4"],
            [r"y=1", r"y=2", r"y=3"],
            corner_name=r"p(x,y)",
        )
        pxy_table.add_grid(cfg)
        table = pxy_table.table
        _ = table.scale_to_fit_width(5)
        _ = table.move_to(mn.ORIGIN)

        px_table = PxTable(
            cfg,
            4,
            1,
            [r"x=1", r"x=2", r"x=3", r"x=4"],
            [r"p(x)"],
        )
        px_table.add_grid(cfg)
        px_marginal = px_table.table
        _ = px_marginal.scale_to_fit_height(table.height)
        _ = px_marginal.next_to(table, mn.LEFT, buff=0.4)

        py_table = PxTable(
            cfg,
            1,
            3,
            [r"p(y)"],
            [r"y=1", r"y=2", r"y=3"],
        )
        py_table.add_grid(cfg)
        py_marginal = py_table.table
        _ = py_marginal.scale_to_fit_width(table.width)
        _ = py_marginal.next_to(table, mn.DOWN, buff=0.35)

        pxy_title = (
            mn.MathTex(r"P(X,Y)", fill_color=cfg.txt_color)
            .next_to(table, mn.UP, buff=0.3)
            .scale(0.8)
        )
        px_title = (
            mn.MathTex(r"P(X)", fill_color=cfg.txt_color)
            .next_to(px_marginal, mn.LEFT, buff=0.3)
            .scale(0.8)
        )
        py_title = (
            mn.MathTex(r"P(Y)", fill_color=cfg.txt_color)
            .next_to(py_marginal, mn.LEFT, buff=0.3)
            .scale(0.8)
        )

        expr = mn.MathTex(
            _EXPR_TEX,
            fill_color=cfg.txt_color,
            substrings_to_isolate=[r"p(x,y)", r"p(x)", r"p(y)"],
        )
        _ = expr.scale_to_fit_width(3.6)
        # generous gap: the summation symbol appears here in the next section
        _ = expr.next_to(table, mn.RIGHT, buff=1.0)

        # center the whole ensemble once all relative positions are set
        _ = mn.VGroup(
            table, px_marginal, py_marginal, pxy_title, px_title, py_title, expr
        ).move_to(mn.ORIGIN)

        self.play(mn.Create(table), mn.Write(pxy_title))
        self.wait()
        self.next_section()
        # both marginals appear together
        self.play(
            mn.Create(px_marginal),
            mn.Write(px_title),
            mn.Create(py_marginal),
            mn.Write(py_title),
        )
        self.wait()
        self.next_section()
        self.play(mn.Write(expr))
        self.wait()
        self.next_section()
        # highlight the joint entry (x=3, y=2) and the matching marginal
        # entries; each box's copy then flies to its term in the expression
        joint_box = mn.SurroundingRectangle(
            pxy_table.cell(row=2, col=1),
            color=mn.BLUE,
            stroke_width=4,
            buff=0.12,
        )
        px_box = mn.SurroundingRectangle(
            px_table.cell(row=2, col=0),
            color=mn.RED,
            stroke_width=4,
            buff=0.12,
        )
        py_box = mn.SurroundingRectangle(
            py_table.cell(row=0, col=1),
            color=mn.ORANGE,
            stroke_width=4,
            buff=0.12,
        )
        self.play(mn.Create(joint_box), mn.Create(px_box), mn.Create(py_box))
        self.wait()
        self.next_section()
        xy_terms = _parts_by_tex(expr, r"p(x,y)")
        x_term = _parts_by_tex(expr, r"p(x)")[0]
        y_terms = _parts_by_tex(expr, r"p(y)")
        # each box's copy flies to its term in the expression, coloring it
        # on arrival; both occurrences of p(x,y) and of p(y) are tagged
        term_boxes = [
            *self._fly_box_copies(joint_box, xy_terms, mn.BLUE),
            *self._fly_box_copies(px_box, [x_term], mn.RED),
            *self._fly_box_copies(py_box, y_terms, mn.ORANGE),
        ]
        self.wait()
        self.next_section()
        # clear the per-term tagging, then generalize entry (x=3, y=2) to
        # the sum over all x: colors reset and the summation symbol appears
        # in the gap left of the expression
        self.play(
            mn.FadeOut(mn.VGroup(*term_boxes)),
            *(
                part.animate.set_color(cfg.txt_color)
                for part in xy_terms + [x_term] + y_terms
            ),
        )
        sum_all = mn.MathTex(r"\sum_{x \in X}", _EXPR_TEX, fill_color=cfg.txt_color)
        # scale + place so the expression body overlays the existing one
        # exactly; only the summation symbol is new (shifting the whole
        # mobject, since moving submobject [1] alone would leave [0] behind)
        _ = sum_all.scale(expr.width / sum_all[1].width)
        _ = sum_all.shift(expr.get_center() - sum_all[1].get_center())
        sum_sym = sum_all[0]
        self.play(mn.Write(sum_sym))
        # widen the entry boxes to their full columns: the y=2 column of the
        # joint table and the whole p(x) value column
        joint_col = mn.VGroup(*(pxy_table.cell(row, 1) for row in range(4)))
        px_col = mn.VGroup(*(px_table.cell(row, 0) for row in range(4)))
        self.play(
            mn.Transform(
                joint_box,
                mn.SurroundingRectangle(
                    joint_col,
                    color=mn.BLUE,
                    stroke_width=4,
                    buff=0.12,
                ),
            ),
            mn.Transform(
                px_box,
                mn.SurroundingRectangle(
                    px_col,
                    color=mn.RED,
                    stroke_width=4,
                    buff=0.12,
                ),
            ),
        )
        # copies of the two column boxes converge into one box around the
        # summation term
        whole_sum = mn.VGroup(sum_sym, expr)
        final_box = mn.SurroundingRectangle(
            whole_sum,
            color=cfg.txt_color,
            stroke_width=4,
            buff=0.12,
        )
        # TransformFromCopy mutates and adds its target argument, so pass
        # copies and keep final_box pristine for positioning the label
        self.play(
            mn.TransformFromCopy(joint_box, final_box.copy()),
            mn.TransformFromCopy(px_box, final_box.copy()),
        )
        self.wait()
        self.next_section()
        # name the boxed quantity, centered below the box
        is_label = mn.MathTex(r"I_s(y; X)", fill_color=cfg.txt_color).scale(0.9)
        _ = is_label.next_to(final_box, mn.DOWN, buff=0.3)
        self.play(mn.Write(is_label))
        self.wait()

    def _fly_box_copies(
        self,
        src: mn.Mobject,
        terms: list[mn.Mobject],
        color: mn.ManimColor,
    ) -> list[mn.Mobject]:
        """Animates a copy of `src` onto each of `terms` (simultaneously),
        coloring each term on arrival; returns the landed boxes."""
        landed = [src.copy() for _ in terms]
        for box in landed:
            _ = self.add(box)
        self.play(
            *(
                mn.Transform(
                    box,
                    mn.SurroundingRectangle(
                        term,
                        color=color,
                        stroke_width=4,
                        buff=0.07,
                    ),
                )
                for box, term in zip(landed, terms)
            ),
            *(term.animate.set_color(color) for term in terms),
        )
        return landed
