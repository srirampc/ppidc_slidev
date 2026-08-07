import manim as mn
import numpy as np

from ppidc import cfg
from ppidc.data import MatParams, MatrixRect

mn.config.background_color = cfg.BKG_COLOR


class TransposeTransform(mn.Scene):
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


class AllPairsMI(mn.Scene):
    def create_line_x(
        self, src_rect: mn.Rectangle, l_shift: float = 0.4
    ) -> tuple[mn.VGroup, mn.Line]:
        line_x = (
            mn.Line(src_rect.get_bottom(), src_rect.get_top())
            .set_color(mn.GRAY_C)
            .shift(l_shift * mn.LEFT)
        )
        txt_x = mn.MathTex("x", fill_color=cfg.TXT_COLOR).move_to(
            line_x.get_start() + 0.2 * mn.DOWN, mn.UP
        )
        group_x = mn.VGroup(line_x, txt_x)
        return group_x, line_x

    def create_line_y(
        self, src_rect: mn.Rectangle, r_shift: float = 0.4
    ) -> tuple[mn.VGroup, mn.Line]:
        line_y = (
            mn.Line(src_rect.get_bottom(), src_rect.get_top())
            .set_color(mn.GRAY_C)
            .shift(r_shift * mn.RIGHT)
        )
        txt_y = mn.MathTex("y", fill_color=cfg.TXT_COLOR).move_to(
            line_y.get_start() + 0.2 * mn.DOWN, mn.UP
        )
        group_y = mn.VGroup(line_y, txt_y)
        return group_y, line_y

    def net_lines(
        self,
        square_n: mn.Square,
    ) -> mn.VGroup:


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

        net_lines = mn.VGroup(net_x, net_y, net_x_t, net_y_t)
        return net_lines

    def graph_matrix(
        self,
    ) -> tuple[mn.Square, MatrixRect, mn.VGroup]:
        square_n = cfg.matrix_square_width().set_color(mn.BLUE).shift(4 * mn.RIGHT)
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
        net_lines = self.net_lines(square_n)
        return square_n, mat_n, net_lines

    def lines_text(
        self, shift_line_x, shift_line_y
    ) -> tuple[mn.VGroup, mn.MathTex, mn.MathTex]:
        fn_text = mn.VGroup(
            mn.MathTex("MI(", fill_color=cfg.TXT_COLOR).move_to(
                shift_line_x.get_end() + 0.2 * mn.LEFT + 0.35 * mn.UP, mn.RIGHT
            ),
            mn.MathTex(",", fill_color=cfg.TXT_COLOR).move_to(
                0.5 * shift_line_x.get_end()
                + 0.5 * shift_line_y.get_end()
                + 0.25 * mn.UP,
                mn.UP,
            ),
            mn.MathTex(")", fill_color=cfg.TXT_COLOR).move_to(
                shift_line_y.get_end() + 0.2 * mn.RIGHT + 0.35 * mn.UP, mn.LEFT
            ),
        )
        rv_text_x = mn.MathTex("X", fill_color=cfg.TXT_COLOR).move_to(
            shift_line_x.get_end() + 0.2 * mn.UP, mn.DOWN
        )
        rv_text_y = mn.MathTex("Y", fill_color=cfg.TXT_COLOR).move_to(
            shift_line_y.get_end() + 0.2 * mn.UP, mn.DOWN
        )
        return fn_text, rv_text_x, rv_text_y

    def construct(self) -> None:
        rect_d = cfg.matrix_rect().set_color(cfg.DM_COLOR).shift(4 * mn.LEFT)
        matrix_d = MatrixRect(
            rect_d,
            rect_d.get_vertices(),
            MatParams(rect_d.color, r"D", r"m", r"n", 0.2, 0.2, text_pos=mn.ORIGIN),
        )
        group_x, _line_x = self.create_line_x(rect_d)
        group_y, _line_y = self.create_line_y(rect_d)
        shift_grp_x, shift_line_x = self.create_line_x(rect_d, -3.6)
        shift_grp_y, shift_line_y = self.create_line_y(rect_d, 4.4)
        fn_text, rv_text_x, rv_text_y = self.lines_text(shift_line_x, shift_line_y)
        square_n, mat_n, net_lines = self.graph_matrix()

        self.play(mn.Create(rect_d), mn.Create(matrix_d.text))
        self.next_section()
        self.play(*[mn.Create(arx) for arx in matrix_d.arrows])
        self.next_section()
        self.play(mn.Create(group_x))
        self.play(mn.Create(group_y))
        self.next_section()
        self.play(
            mn.Transform(group_x.copy(), shift_grp_x),
            mn.Transform(group_y.copy(), shift_grp_y),
        )
        self.next_section()
        self.play(
            mn.Transform(shift_grp_x, rv_text_x), mn.Transform(shift_grp_y, rv_text_y)
        )
        self.next_section()
        self.play(mn.Create(fn_text))
        self.next_section()
        self.play(mn.Create(net_lines))
        self.next_section()
        self.play(
            mn.Create(square_n),
        )
        self.play(
            mn.FadeIn(mat_n.text, *mat_n.arrows)
        )
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
