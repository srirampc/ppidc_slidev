import manim as mn
import numpy as np

from ppidc import cfg
from ppidc.data import MatParams, MatrixRect


class DataT(mn.Scene):
    def construct(self) -> None:
        d_rect = cfg.matrix_rect().set_color(cfg.DM_COLOR).shift(3 * mn.LEFT)
        d_rect_t = (
            cfg.matrix_rect()
            .set_color(cfg.G_COLOR)
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

        self.add(
            *(
                mobj
                for mobj in [d_rect, d_matrix.text_bg_rect, d_matrix.text]
                if mobj is not None
            )
        )
        self.add(*d_matrix.arrows)
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
            # mn.Transform(d_rect.copy(), d_rect_t),
            # mn.Transform(d_matrix.row_arrow.copy(), d_matrix_t.col_arrow),
            # mn.Transform(d_matrix.col_arrow.copy(), d_matrix_t.row_arrow),
            # mn.Transform(d_matrix.row_txt.copy(), d_matrix_t.col_txt),
            # mn.Transform(d_matrix.col_txt.copy(), d_matrix_t.row_txt),
            # mn.FadeIn(mat_d_t.text),
            run_time=3,
        )
        self.wait()
        self.next_section()
        #if d_matrix_t.text_bg_rect:
        #    self.add(d_matrix_t.text_bg_rect)
        self.play(mn.FadeIn(d_matrix_t.text_object()), run_time=3)
        # self.wait()
