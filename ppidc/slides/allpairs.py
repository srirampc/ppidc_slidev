import typing as t
from dataclasses import dataclass

import manim as mn
import manim.typing as mnt
from manim_themes import manim_theme as mtheme

from ppidc import (
    MatParams,
    MatrixRect,
    default_config,
    scene_header,
    theme_background,
)

_D_WIDTH: float = 2
_D_HEIGHT: float = 4
_D_GRID_STEP: float = 0.2
_D_GRID_STROKE: float = 1
_G_SIZE: float = _D_WIDTH


def _matrix_rect() -> mn.Rectangle:
    d_rect = mn.Rectangle(
        width=_D_WIDTH,
        height=_D_HEIGHT,
        grid_xstep=_D_GRID_STEP,
        grid_ystep=_D_GRID_STEP,
    )
    _g = d_rect.grid_lines.set_stroke(width=_D_GRID_STROKE)
    return d_rect


def _matrix_square_width() -> mn.Square:
    d_rect = mn.Square(
        _D_WIDTH,
        grid_xstep=_D_GRID_STEP,
        grid_ystep=_D_GRID_STEP,
    )
    _g = d_rect.grid_lines.set_stroke(width=_D_GRID_STROKE)
    return d_rect


@dataclass
class _VecFunctionLines:
    group_y: mn.VGroup
    group_shift_x: mn.VGroup
    group_shift_y: mn.VGroup
    fn_txt: mn.VGroup
    rv_txt_x: mn.MathTex
    rv_txt_y: mn.MathTex
    group_txt: mn.VGroup


class PairwiseNet(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

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
    ) -> mn.VGroup:
        line_v = (
            mn.Line(src_rect.get_bottom(), src_rect.get_top())
            .set_color(mn.GRAY_BROWN)
            .shift(v_shift)
        )
        txt_v = mn.MathTex(txt, fill_color=default_config().txt_color).move_to(
            line_v.get_start() + 0.2 * mn.DOWN, mn.UP
        )
        group_v = mn.VGroup(line_v, txt_v)
        return group_v

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

    def function_text(
        self, shift_line_x: mn.VMobject, shift_line_y: mn.VMobject, y_rv: str
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

    def vec_function_lines(
        self,
        rect_d: mn.Rectangle,
        x_name: str,
        y_name: str,
        y_rv: str,
        y_shift: float,
    ) -> _VecFunctionLines:
        vec_y = self.vec_with_name(rect_d, y_shift * mn.RIGHT, y_name)
        vec_shift_x = self.vec_with_name(rect_d, 3.6 * mn.RIGHT, x_name)
        vec_shift_y = self.vec_with_name(rect_d, 4.4 * mn.RIGHT, y_name)
        fn_txt, rv_txt_x, rv_txt_y = self.function_text(
            vec_shift_x[0], vec_shift_y[0], y_rv
        )
        txt_g = mn.VGroup(fn_txt, rv_txt_x, rv_txt_y)
        return _VecFunctionLines(
            group_y=vec_y,
            group_shift_x=vec_shift_x,
            group_shift_y=vec_shift_y,
            fn_txt=fn_txt,
            rv_txt_x=rv_txt_x,
            rv_txt_y=rv_txt_y,
            group_txt=txt_g,
        )

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        header_txt = scene_header(
            "Network Construction by Pair-wise Evaluation", cfg, weight=mn.BOLD
        )

        x_name = r"\vec{x}"
        rect_d = _matrix_rect().set_color(cfg.d_color).shift(4 * mn.LEFT + 0.2 * mn.UP)
        square_n = (
            _matrix_square_width().set_color(mn.BLUE).shift(4 * mn.RIGHT + 0.2 * mn.UP)
        )
        matrix_d = self.data_matrix(rect_d)
        mat_n = self.adj_matrix(square_n)
        y_names = [r"\vec{y}", r"\vec{w}", r"\vec{z}"]
        rv_names = [r"Y", r"W", r"Z"]
        y_vec_shifts = [0.4, 0.6, 0.8]
        mi_points = [
            self.dot_in_square(square_n, 0.4 * mn.LEFT, 0.6 * mn.UP, square_n.color),
            self.dot_in_square(square_n, 0.4 * mn.LEFT, 0.4 * mn.UP, square_n.color),
            self.dot_in_square(square_n, 0.4 * mn.LEFT, 0.2 * mn.UP, square_n.color),
        ]
        group_x = self.vec_with_name(rect_d, 0.4 * mn.LEFT, x_name)
        y_vec_objects = [
            self.vec_function_lines(rect_d, x_name, y_name, y_rv, y_shift)
            for y_name, y_rv, y_shift in zip(y_names, rv_names, y_vec_shifts)
        ]
        net_vx, _net_hx = self.square_lines(
            square_n, 0.4 * mn.LEFT, 0.4 * mn.UP, mn.GRAY_C
        )
        src_net_groups: list[mn.VMobject] = [net_vx]

        self.play(mn.Create(header_txt))
        self.play(
            *(
                mn.Create(mobj)
                for mobj in [
                    rect_d,
                    matrix_d.text_bg_rect,
                    matrix_d.text,
                    *matrix_d.arrows,
                ]
                if mobj is not None
            )
        )
        self.wait()
        self.next_section()
        # self.play(*[mn.Create(arx) for arx in matrix_d.arrows])
        # self.next_section()
        self.play(mn.Create(group_x))
        for ix, (yvd, mi_dot, txt_dir) in enumerate(
            zip(y_vec_objects, mi_points, [mn.RIGHT, mn.LEFT, mn.RIGHT])
        ):
            self.play(mn.Create(yvd.group_y))
            # self.next_section()
            self.play(
                mn.TransformFromCopy(group_x, yvd.group_shift_x),
                mn.TransformFromCopy(yvd.group_y, yvd.group_shift_y),
            )
            # self.next_section()
            self.play(
                mn.TransformFromCopy(yvd.group_shift_x, yvd.rv_txt_x),
                mn.TransformFromCopy(yvd.group_shift_y, yvd.rv_txt_y),
            )
            if ix == 0:
                self.wait()
                self.next_section()
            self.play(mn.Create(yvd.fn_txt))
            if ix == 0:
                self.wait()
                self.next_section()
            # self.play(mn.Transform(yvd.group_txt, mi_dot))
            fn_grp_txt = yvd.group_txt
            self.play(
                mn.Create(mi_dot),
                mn.Transform(
                    fn_grp_txt,
                    fn_grp_txt.copy()
                    .scale_to_fit_height(0.3)
                    .next_to(mi_dot, txt_dir, buff=0.1),
                ),
            )
            src_net_groups.append(fn_grp_txt)
            src_net_groups.append(mi_dot)
            if ix == 0:
                self.play(mn.Create(net_vx))
            self.wait()
            self.next_section()
            self.play(
                mn.Uncreate(yvd.group_y),
                mn.Uncreate(yvd.group_shift_x),
                mn.Uncreate(yvd.group_shift_y),
            )
            #if ix == 0:
            #    self.next_section()
        #self.next_section()
        self.play(
            mn.Transform(mn.VGroup(*src_net_groups), square_n),
            mn.Uncreate(group_x),
        )
        self.play(mn.FadeIn(mat_n.text, *mat_n.arrows))
        self.wait()
        self.next_section("Pairwise evaluation complexity")
        call_count_txt = mn.VGroup(
            mn.MathTex(r"f(\cdot, \cdot)"),
            mn.Text("called", font="Concourse T3"),
            mn.MathTex(r"\binom{n}{2} = O(n^2)"),
            mn.Text("times", font="Concourse T3"),
        )
        _ = call_count_txt.arrange(mn.RIGHT, buff=0.2).set_color(cfg.txt_color)
        _ = call_count_txt.move_to(2.8 * mn.DOWN)
        self.play(
            mn.Write(call_count_txt),
            mn.Create(
                mn.SurroundingRectangle(
                    call_count_txt,
                    color=mn.BLUE,
                    stroke_width=3,
                    buff=0.12,
                )
            ),
        )
        self.wait()
