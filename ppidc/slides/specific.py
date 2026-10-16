import typing as t
from collections.abc import Iterable

import manim as mn
from manim_themes import manim_theme as mtheme

from ppidc import PxTable, default_config, parts_by_tex

_EXPR_TEX = r"\frac{p(x,y)}{p(y)} \log \left( \frac{p(x,y)}{p(x)\cdot p(y)} \right)"



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
        xy_terms = parts_by_tex(expr, r"p(x,y)")
        x_term = parts_by_tex(expr, r"p(x)")[0]
        y_terms = parts_by_tex(expr, r"p(y)")
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
        sum_sym: mn.VMobject = sum_all[0]  # pyright: ignore[reportAssignmentType]
        self.play(mn.Write(sum_sym))
        # widen the entry boxes to their full columns: the y=2 column of the
        # joint table and the whole p(x) value column
        joint_col = mn.VGroup(*(pxy_table.cell(row, 1) for row in range(4)))  # pyright: ignore[reportArgumentType]
        px_col = mn.VGroup(*(px_table.cell(row, 0) for row in range(4)))  # pyright: ignore[reportArgumentType]
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
        terms: Iterable[mn.VMobject],
        color: mn.ManimColor,
    ) -> list[mn.VMobject]:
        """Animates a copy of `src` onto each of `terms` (simultaneously),
        coloring each term on arrival; returns the landed boxes."""
        landed: list[mn.VMobject] = [src.copy() for _ in terms]  # pyright: ignore[reportAssignmentType]
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
