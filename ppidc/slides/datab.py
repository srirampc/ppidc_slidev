import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import (
    MatParams,
    MatrixRect,
    default_config,
    scene_header,
    theme_background,
)

_D_WIDTH: float = 3
_D_HEIGHT: float = 6
_D_GRID_STEP: float = 0.1
_D_GRID_STROKE: float = 0.8
_S_GRID_STEP: float = 0.6
_S_POS = 3.5 * mn.LEFT + 2.2 * mn.DOWN


def _matrix_rect() -> mn.Rectangle:
    d_rect = mn.Rectangle(
        width=_D_WIDTH,
        height=_D_HEIGHT,
        grid_xstep=_D_GRID_STEP,
        grid_ystep=_D_GRID_STEP,
    )
    _g = d_rect.grid_lines.set_stroke(width=_D_GRID_STROKE)
    return d_rect


def _matrix_square() -> mn.Square:
    d_square = mn.Square(_D_WIDTH, grid_xstep=_S_GRID_STEP, grid_ystep=_S_GRID_STEP)
    _g = d_square.grid_lines.set_stroke(width=1)
    return d_square


class DataB(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    def vec_with_name(
        self, src_rect: mn.Rectangle, h_shift: mnt.Vector3D, txt: str
    ) -> tuple[mn.VGroup, mn.Line]:
        line_v = (
            mn.Line(src_rect.get_left(), src_rect.get_right())
            .set_color(mn.BLACK)
            .shift(h_shift)
        )
        txt_v = mn.MathTex(txt, fill_color=default_config().txt_color).move_to(
            line_v.get_start() + 0.5 * mn.LEFT, mn.LEFT
        )
        group_v = mn.VGroup(line_v, txt_v)
        return group_v, line_v

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        x_name = r"\vec{x}"
        y_name = r"\vec{y}"
        header_txt = scene_header("Handling Large Datasets", cfg).shift(2.5 * mn.RIGHT)
        self.play(mn.Create(header_txt))
        d_rect = (
            _matrix_rect().set_color(cfg.d_color).shift(3.5 * mn.LEFT + 2.75 * mn.UP)
        )
        d_rect_t = (
            _matrix_rect()
            .set_color(mn.GREEN)
            .shift(2 * mn.RIGHT + 2.2 * mn.DOWN)
            .rotate(-mn.PI / 2)
            .flip()
        )
        d_matrix = MatrixRect(
            d_rect,
            d_rect.get_vertices(),
            MatParams(
                d_rect.color, r"D", "m", r"n", 0.2, -_D_HEIGHT + 0.2, text_bg_rect=True
            ),
        )

        d_matrix_t = MatrixRect(
            d_rect_t,
            np.roll(d_rect_t.get_vertices(), shift=-1, axis=0),
            MatParams(
                d_rect_t.color,
                r"D^T",
                r"n",
                r"m",
                -0.2,
                0.2,
                col_text_off=-0.2,
                text_bg_rect=True,
            ),
        )
        group_x, _line_x = self.vec_with_name(d_rect_t, -0.8 * mn.DOWN, x_name)
        group_y, _line_y = self.vec_with_name(d_rect_t, 0.7 * mn.DOWN, y_name)

        joint_prob = mn.MathTex(r"P(X, Y)", fill_color=cfg.txt_color).shift(
            _S_POS
        )
        d_square = _matrix_square().shift(_S_POS)

        _a = self.add(
            *(
                mobj
                for mobj in [d_rect, d_matrix.text_bg_rect, d_matrix.text]
                if mobj is not None
            )
        )
        _a = self.add(*d_matrix.arrows)
        self.wait()
        self.next_section()
        self.play(
            *(
                mn.Transform(from_obj.copy(), to_obj)
                for from_obj, to_obj in zip(
                    [d_rect] + d_matrix.arrows,
                    [d_rect_t] + d_matrix_t.arrows,
                )
            ),
            # run_time=3,
        )
        self.play(mn.FadeIn(d_matrix_t.text_object()))
        self.next_section()
        self.play(mn.Write(joint_prob), mn.Create(group_x), mn.Create(group_y))
        self.next_section()
        self.play(mn.Uncreate(joint_prob), mn.Uncreate(group_x), mn.Uncreate(group_y))
        self.play(mn.Create(d_square))
        self.wait()
