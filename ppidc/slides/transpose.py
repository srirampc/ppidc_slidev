import typing as t

import manim as mn
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import MatParams, MatrixRect, default_config, matrix_rect


class DataT(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        d_rect = matrix_rect(cfg).set_color(cfg.d_color).shift(3 * mn.LEFT)
        d_rect_t = (
            matrix_rect(cfg)
            .set_color(mn.GREEN)
            .shift(3 * mn.RIGHT)
            .rotate(-mn.PI / 2)
            .flip()
        )
        d_matrix = MatrixRect(
            d_rect,
            d_rect.get_vertices(),
            MatParams(d_rect.color, r"D", "m", r"n", 0.2, 0.2, text_bg_rect=True),
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
                text_bg_rect=True
            ),
        )

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
            run_time=3,
        )
        self.wait()
        self.next_section()
        self.play(mn.FadeIn(d_matrix_t.text_object()), run_time=3)
        self.wait()
