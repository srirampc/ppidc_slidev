import manim as mn
import numpy as np

import ppidc.cfg as cfg
from ppidc.data import MatParams, MatrixRect

mn.config.background_color = cfg.BKG_COLOR

class BasicExample(mn.Scene):
    def construct(self):
        circle = mn.Circle(radius=3, color=mn.BLUE)
        dot = mn.Dot()

        self.play(mn.GrowFromCenter(circle))
        self.next_section()
        self.play(mn.MoveAlongPath(dot, circle), run_time=2, rate_func=mn.linear)
        self.next_section()  # This will start a new non-looping slide

        self.play(dot.animate.move_to(mn.ORIGIN))

class TransposeTransform(mn.Scene):
    def data_rect(self):
        return mn.Rectangle(width=cfg.DM_WIDTH, height=cfg.DM_HEIGHT)

    def construct(self) -> None:
        rect_d = self.data_rect().set_color(cfg.DM_COLOR).shift(3 * mn.LEFT)
        rect_dc = rect_d.copy()
        rect_d_t = (
            self.data_rect()
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
        self.play(mn.Transform(rect_dc, rect_d_t), run_time=3)
        self.wait()
        self.next_section()
        self.play(mn.FadeIn(mat_d_t.text, *mat_d_t.arrows), run_time=3)
        self.wait()

# Command to run:
class AllPairsEvaluation(mn.Scene):
    def data_rect(self):
        return mn.Rectangle(width=cfg.DM_WIDTH, height=cfg.DM_HEIGHT)

    def net_square(self):
        return mn.Square(cfg.DM_WIDTH)

    def construct(self) -> None:
        rect_d = self.data_rect().set_color(cfg.DM_COLOR).shift(3 * mn.LEFT)

        mat_d = MatrixRect(
            rect_d,
            rect_d.get_vertices(),
            MatParams(rect_d.color, r"D", "m", r"n", 0.2, 0.2),
        )
        square_n = self.net_square().set_color(mn.BLUE).shift(3 * mn.RIGHT)
        mat_n = MatrixRect(
            square_n,
            square_n.get_vertices(),
            MatParams(
                square_n.color,
                r"G",
                r"n",
                r"n",
                0.2,
                0.2,
            ),
        )

        line_x = (
            mn.Line(rect_d.get_bottom(), rect_d.get_top())
            .set_color(mn.GRAY_C)
            .shift(0.4 * mn.LEFT)
        )
        line_y = (
            mn.Line(rect_d.get_bottom(), rect_d.get_top())
            .set_color(mn.GRAY_D)
            .shift(0.4 * mn.RIGHT)
        )
        txt_x = (
            mn.MathTex("x", fill_color=cfg.TXT_COLOR)
            .move_to(line_x.get_start())
            .shift(0.2 * mn.DOWN)
        )
        txt_y = (
            mn.MathTex("y", fill_color=cfg.TXT_COLOR)
            .move_to(line_y.get_start())
            .shift(0.2 * mn.DOWN)
        )

        net_x = (
            mn.Line(square_n.get_bottom(), square_n.get_top())
            .set_color(mn.GRAY_C)
            .shift(0.4 * mn.LEFT)
        )
        net_y = (
            mn.Line(square_n.get_bottom(), square_n.get_top())
            .set_color(mn.GRAY_D)
            .shift(0.4 * mn.RIGHT)
        )

        ntxt_x = (
            mn.MathTex("X", fill_color=cfg.TXT_COLOR)
            .move_to(net_x.get_start())
            .shift(0.2 * mn.DOWN)
        )
        ntxt_y = (
            mn.MathTex("Y", fill_color=cfg.TXT_COLOR)
            .move_to(net_y.get_start())
            .shift(0.2 * mn.DOWN)
        )

        net_x_t = (
            mn.Line(square_n.get_left(), square_n.get_right())
            .set_color(mn.GRAY_C)
            .shift(0.4 * mn.UP)
        )
        net_y_t = (
            mn.Line(square_n.get_left(), square_n.get_right())
            .set_color(mn.GRAY_D)
            .shift(0.4 * mn.DOWN)
        )

        ntxt_x_t = (
            mn.MathTex("x", fill_color=cfg.TXT_COLOR)
            .move_to(net_x_t.get_end())
            .shift(0.2 * mn.RIGHT)
        )
        ntxt_y_t = (
            mn.MathTex("y", fill_color=cfg.TXT_COLOR)
            .move_to(net_y_t.get_end())
            .shift(0.2 * mn.RIGHT)
        )


        self.play(mn.Create(rect_d), mn.Create(mat_d.text))
        self.next_section()
        self.play(*[mn.Create(arx) for arx in mat_d.arrows])
        self.next_section()
        self.play(
            mn.Create(line_x),
            mn.Create(txt_x),
        )
        self.play(
            mn.Create(line_y),
            mn.Create(txt_y),
        )
        self.next_section()
        self.add(
            net_x,
            ntxt_x,
            net_y,
            ntxt_y,
            net_x_t,
            ntxt_x_t,
            net_y_t,
            ntxt_y_t,
        )
        self.add(square_n, mat_n.text, *mat_n.arrows)
        self.wait()
        #
