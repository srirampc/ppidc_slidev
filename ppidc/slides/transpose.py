import manim as mn
import numpy as np

from ppidc import cfg
from ppidc.data import MatParams, MatrixRect


class DataT(mn.Scene):
    def construct(self) -> None:
        rect_d = cfg.matrix_rect().set_color(cfg.DM_COLOR).shift(3 * mn.LEFT)
        rect_dc = rect_d.copy()
        rect_d_t = (
            cfg.matrix_rect()
            .set_color(cfg.G_COLOR)
            .shift(3 * mn.RIGHT)
            .rotate(-mn.PI / 2)
            .flip()
        )
        mat_d = MatrixRect(
            rect_d,
            rect_d.get_vertices(),
            MatParams(rect_d.color, r"D", "m", r"n", 0.2, 0.2),
        )

        mat_d_t = MatrixRect(
            rect_d_t,
            np.roll(rect_d_t.get_vertices(), shift=-1, axis=0),
            MatParams(
                rect_d_t.color,
                r"D^T",
                r"n",
                r"m",
                -0.2,
                0.2,
            ),
        )

        self.add(rect_d, mat_d.text, *mat_d.arrows)
        self.wait()
        self.next_section()
        self.play(
            mn.Transform(rect_dc, rect_d_t),
            mn.Transform(mat_d.row_arrow.copy(), mat_d_t.col_arrow),
            mn.Transform(mat_d.col_arrow.copy(), mat_d_t.row_arrow),
            mn.Transform(mat_d.row_txt.copy(), mat_d_t.col_txt),
            mn.Transform(mat_d.col_txt.copy(), mat_d_t.row_txt),
            # mn.FadeIn(mat_d_t.text),
            run_time=3,
        )
        self.wait()
        self.next_section()
        self.play(mn.FadeIn(mat_d_t.text), run_time=3)
        # self.wait()
