import typing as t

import manim as mn
import manim.typing as mnt
from manim_themes import manim_theme as mtheme

from ppidc import (
    MatParams,
    MatrixRect,
    default_config,
    matrix_rect,
    matrix_square_width,
)


class MINet(mn.Scene):

    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    def data_matrix(self, rect_d: mn.Rectangle) -> MatrixRect:
        return MatrixRect(
            rect_d,
            rect_d.get_vertices(),
            MatParams(
                rect_d.color,
                r"D",
                r"m",
                r"n",
                0.2,
                0.2,
                text_pos=mn.ORIGIN,
                text_bg_rect=True,
            ),
        )

    def adj_matrix(self, square_n: mn.Square) -> MatrixRect:
        return MatrixRect(
            square_n,
            square_n.get_vertices(),
            MatParams(square_n.color, r"G", r"n", r"n", 0.2, 0.2, text_pos=mn.DOWN),
        )

    def vec_with_name(
        self, src_rect: mn.Rectangle, v_shift: mnt.Vector3D, txt: str
    ) -> tuple[mn.VGroup, mn.Line]:
        line_v = (
            mn.Line(src_rect.get_bottom(), src_rect.get_top())
            .set_color(mn.GRAY_C)
            .shift(v_shift)
        )
        txt_v = mn.MathTex(txt, fill_color=default_config().txt_color).move_to(
            line_v.get_start() + 0.2 * mn.DOWN, mn.UP
        )
        group_v = mn.VGroup(line_v, txt_v)
        return group_v, line_v

    def square_vline(
        self,
        square_n: mn.Square,
        v_shift: mnt.Vector3D,
        color: mn.ManimColor,
    ) -> mn.Line:
        return (
            mn.Line(square_n.get_bottom(), square_n.get_top())
            .set_color(color)
            .shift(v_shift)
        )

    def square_hline(
        self,
        square_n: mn.Square,
        h_shift: mnt.Vector3D,
        color: mn.ManimColor,
    ) -> mn.Line:
        return (
            mn.Line(square_n.get_left(), square_n.get_right())
            .set_color(color)
            .shift(h_shift)
        )

    def square_lines(
        self,
        square_n: mn.Square,
        v_shift: mnt.Vector3D,
        h_shift: mnt.Vector3D,
        color: mn.ManimColor,
    ) -> tuple[mn.Line, mn.Line]:
        return (
            self.square_vline(square_n, v_shift, color),
            self.square_hline(square_n, h_shift, color),
        )

    def dot_in_square(
        self,
        square_n: mn.Square,
        v_shift: mnt.Vector3D,
        h_shift: mnt.Vector3D,
        color: mn.ManimColor,
    ) -> mn.Dot:
        return mn.Dot(
            point=square_n.get_bottom() + v_shift + h_shift,
            color=color,
        )

    def mi_function_text(
        self, shift_line_x: mn.Line, shift_line_y: mn.Line, y_rv: str
    ) -> tuple[mn.VGroup, mn.MathTex, mn.MathTex]:
        cfg = default_config()
        fn_text = mn.VGroup(
            mn.MathTex("f(", fill_color=cfg.txt_color).move_to(
                shift_line_x.get_end() + 0.2 * mn.LEFT + 0.35 * mn.UP, mn.RIGHT
            ),
            mn.MathTex(",", fill_color=cfg.txt_color).move_to(
                0.5 * shift_line_x.get_end()
                + 0.5 * shift_line_y.get_end()
                + 0.25 * mn.UP,
                mn.UP,
            ),
            mn.MathTex(")", fill_color=cfg.txt_color).move_to(
                shift_line_y.get_end() + 0.2 * mn.RIGHT + 0.35 * mn.UP, mn.LEFT
            ),
        )
        rv_text_x = mn.MathTex("X", fill_color=cfg.txt_color).move_to(
            shift_line_x.get_end() + 0.2 * mn.UP, mn.DOWN
        )
        rv_text_y = mn.MathTex(y_rv, fill_color=cfg.txt_color).move_to(
            shift_line_y.get_end() + 0.2 * mn.UP, mn.DOWN
        )
        return fn_text, rv_text_x, rv_text_y

    def net_lines(
        self,
        square_n: mn.Square,
    ) -> mn.VGroup:
        net_x = self.square_vline(square_n, 0.4 * mn.LEFT, mn.GRAY_C)
        net_y = self.square_vline(square_n, 0.4 * mn.RIGHT, mn.GRAY_D)
        net_x_t = self.square_hline(square_n, 0.4 * mn.UP, mn.GRAY_C)
        net_y_t = self.square_hline(square_n, 0.4 * mn.DOWN, mn.GRAY_D)

        net_lines = mn.VGroup(net_x, net_y, net_x_t, net_y_t)
        return net_lines

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        x_name = r"\vec{x}"
        rect_d = matrix_rect(cfg).set_color(cfg.d_color).shift(4 * mn.LEFT)
        square_n = matrix_square_width(cfg).set_color(mn.BLUE).shift(4 * mn.RIGHT)
        matrix_d = self.data_matrix(rect_d)
        mat_n = self.adj_matrix(square_n)
        y_names = [r"\vec{y}", r"\vec{w}", r"\vec{z}"]
        rv_names = [r"Y", r"W", r"Z"]
        y_shifts = [0.4, 0.6, 0.8]
        mi_points = [
            self.dot_in_square(square_n, 0.4 * mn.LEFT, 0.6 * mn.UP, square_n.color),
            self.dot_in_square(square_n, 0.4 * mn.LEFT, 0.4 * mn.UP, square_n.color),
            self.dot_in_square(square_n, 0.4 * mn.LEFT, 0.2 * mn.UP, square_n.color),
        ]
        txt_groups: list[mn.VGroup] = []

        self.play(
            *(
                mn.Create(mobj)
                for mobj in [rect_d, matrix_d.text_bg_rect, matrix_d.text, *matrix_d.arrows]
                if mobj is not None
            )
        )
        self.next_section()
        #self.play(*[mn.Create(arx) for arx in matrix_d.arrows])
        #self.next_section()
        group_x, _line_x = self.vec_with_name(rect_d, 0.4 * mn.LEFT, x_name)
        self.play(mn.Create(group_x))
        for ix, (y_name, y_rv, mi_dot, r_shift) in enumerate(zip(
            y_names, rv_names, mi_points, y_shifts
        )):
            shift_grp_x, shift_line_x = self.vec_with_name(
                rect_d, 3.6 * mn.RIGHT, x_name
            )
            group_y, _line_y = self.vec_with_name(rect_d, r_shift * mn.RIGHT, y_name)
            shift_grp_y, shift_line_y = self.vec_with_name(
                rect_d, 4.4 * mn.RIGHT, y_name
            )
            mi_fn_txt, rv_text_x, rv_text_y = self.mi_function_text(
                shift_line_x, shift_line_y, y_rv
            )
            x_copy = group_x.copy()
            y_copy = group_y.copy()
            self.play(mn.Create(group_y))
            #self.next_section()
            self.play(
                mn.Transform(x_copy, shift_grp_x),
                mn.Transform(y_copy, shift_grp_y),
            )
            #self.next_section()
            self.play(
                mn.Transform(shift_grp_x, rv_text_x),
                mn.Transform(shift_grp_y, rv_text_y),
            )
            self.next_section()
            self.play(mn.Create(mi_fn_txt))
            self.next_section()
            txt_g = mn.VGroup(mi_fn_txt, rv_text_x, rv_text_y)
            self.play(mn.Transform(txt_g, mi_dot))
            txt_groups.append(txt_g)
            if ix == 0:
                self.next_section()
            self.play(
                *[
                    mn.Uncreate(mobj)
                    for mobj in [
                        # group_x,
                        group_y,
                        # _line_x,
                        _line_y,
                        shift_grp_x,
                        shift_grp_y,
                        shift_line_x,
                        shift_line_y,
                        x_copy,
                        y_copy,
                    ]
                ]
            )
            if ix == 0:
              self.next_section()
        net_vx, _net_hx = self.square_lines(
            square_n, 0.4 * mn.LEFT, 0.4 * mn.UP, mn.GRAY_C
        )
        self.play(mn.Create(net_vx))
        self.next_section()
        self.play(
            mn.Transform(mn.VGroup(*txt_groups), square_n),
            mn.Uncreate(group_x),
            mn.Uncreate(_line_x),
        )
        self.play(mn.FadeIn(mat_n.text, *mat_n.arrows), mn.FadeOut(net_vx))
        self.wait()
