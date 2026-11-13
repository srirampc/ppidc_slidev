import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import (
    Config,
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


def _sub_rectangle(
    src_rect: mn.Rectangle, color: mn.ManimColor = mn.BLUE, offset: float = 0.0
):
    rct = mn.Rectangle(
        width=src_rect.width,
        height=src_rect.height / 5,
        grid_xstep=_D_GRID_STEP,
        grid_ystep=_D_GRID_STEP,
    ).set_color(color)
    _ = rct.grid_lines.set_stroke(width=_D_GRID_STROKE * 2)
    _ = rct.align_to(src_rect, mn.UP + mn.LEFT).shift(offset * mn.DOWN)
    return rct


def _matrix_rect(width: int = _D_WIDTH, height: int = _D_HEIGHT) -> mn.Rectangle:
    d_rect = mn.Rectangle(
        width=width,
        height=height,
        grid_xstep=_D_GRID_STEP,
        grid_ystep=_D_GRID_STEP,
    )
    _g = d_rect.grid_lines.set_stroke(width=_D_GRID_STROKE)
    return d_rect


def _comp_matrix() -> tuple[mn.Square, mn.Polygon]:
    # d_square = mn.Square(_D_WIDTH, grid_xstep=_S_GRID_STEP, grid_ystep=_S_GRID_STEP)
    # _g = d_square.grid_lines.set_stroke(width=1)
    d_square = mn.Square(_D_WIDTH).shift(_S_POS)
    d_triangle = mn.Polygon(
        d_square.get_corner(mn.UP + mn.LEFT),
        d_square.get_corner(mn.UP + mn.RIGHT),
        d_square.get_corner(mn.DOWN + mn.RIGHT),
        fill_color=mn.GRAY_A,
    ).set_opacity(0.5)
    return d_square, d_triangle


type _BulletPart = tuple[str, t.Literal["text", "math"]]


def _bullet_row(
    cfg: Config, parts: list[_BulletPart], font_size: float = 24
) -> mn.VGroup:
    runs = [
        mn.MathTex(text, font_size=font_size, fill_color=cfg.txt_color)
        if kind == "math"
        else mn.Text(text, font="Concourse T3", font_size=font_size).set_color(
            cfg.txt_color
        )
        for text, kind in parts
    ]
    body = mn.VGroup(*runs).arrange(mn.RIGHT, buff=0.12)

    dot = mn.Text("•", font="Concourse T3", font_size=font_size).set_color(
        cfg.txt_color
    )
    dot.next_to(body, mn.LEFT, buff=0.16)  # pyright: ignore[reportUnusedCallResult]
    return mn.VGroup(dot, body)


def _bullet_points(cfg: Config) -> list[mn.VGroup]:
    return [
        _bullet_row(
            cfg,
            [
                ("Compute ", "text"),
                (r"P(X,Y) \forall X, Y,\ X < Y", "math"),
                (" (assuming an order in ", "text"),
                (r"\mathcal{X}", "math"),
                (")", "text"),
            ],
        ),
        _bullet_row(
            cfg,
            [
                ("Block-wise distribution of work limits ", "text"),
                (r"O\left(\frac{m}{p}\right)", "math"),
                (" data", "text"),
            ],
        ),
        _bullet_row(cfg, [("Read corresponding rows", "text")]),
        _bullet_row(cfg, [("Batch distribution scheme", "text")]),
    ]


def _upper_triangular_cells(
    d_square: mn.Square,
) -> tuple[list[list[mn.Square]], mn.VGroup]:
    cells_per_side = round(_D_WIDTH / _S_GRID_STEP)
    top_left = d_square.get_corner(mn.UP + mn.LEFT)
    ut_cells = [
        [
            mn.Square(
                side_length=_S_GRID_STEP,
                fill_color=mn.GRAY_A,
                fill_opacity=1,
                stroke_color=mn.GRAY_D,
                stroke_width=1,
            ).move_to(
                top_left
                + (col + 0.5) * _S_GRID_STEP * mn.RIGHT
                + (row + 0.5) * _S_GRID_STEP * mn.DOWN
            )
            for col in range(row, cells_per_side)
        ]
        for row in range(cells_per_side)
    ]
    return ut_cells, mn.VGroup(
        *(
            ut_cells[row][col]
            for row in range(len(ut_cells))
            for col in range(len(ut_cells[row]))
        )
    )


class DataB(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    def vec_with_name(
        self, src_rect: mn.Rectangle, h_shift: mnt.Vector3D, txt: str
    ) -> tuple[mn.VGroup, mn.Line]:
        line_v = mn.Line(src_rect.get_left(), src_rect.get_right()).shift(h_shift)
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
        bullets = mn.VGroup(*_bullet_points(cfg)).arrange(
            mn.DOWN, aligned_edge=mn.LEFT, buff=0.18
        )
        _ = bullets.next_to(header_txt, mn.DOWN, aligned_edge=mn.RIGHT, buff=0.35)
        self.play(mn.Create(header_txt))
        d_rect = (
            _matrix_rect().set_color(cfg.d_color).shift(3.5 * mn.LEFT + 2.75 * mn.UP)
        )
        d_rect_t = (
            _matrix_rect()
            .set_color(mn.GRAY_BROWN)
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

        joint_prob = mn.MathTex(r"P(X, Y)", fill_color=cfg.txt_color).shift(_S_POS)
        d_square, d_triangle = _comp_matrix()

        sub_rect_list = [
            _sub_rectangle(d_rect_t, mn.BLUE, ofx) for ofx in [0, 0.5, 1, 1.5, 2]
        ]
        # top_d_rect_t = mn.Rectangle(
        #    width=d_rect_t.width,
        #    height=d_rect_t.height / 5,
        #    grid_xstep=_D_GRID_STEP,
        #    grid_ystep=_D_GRID_STEP,
        # ).set_color(mn.BLUE)
        # _ = top_d_rect_t.grid_lines.set_stroke(width=_D_GRID_STROKE * 2)
        # _ = top_d_rect_t.align_to(d_rect_t, mn.UP + mn.LEFT).shift(0.5 * mn.DOWN)

        # bot_d_rect_t = top_d_rect_t.copy()
        # _ = bot_d_rect_t.grid_lines.set_stroke(width=_D_GRID_STROKE * 2)
        # _ = top_d_rect_t.align_to(d_rect_t, mn.DOWN + mn.LEFT)

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
            mn.FadeIn(d_matrix_t.text_object()),
            # run_time=3,
        )
        self.next_section()
        self.play(mn.Write(joint_prob), mn.Create(group_x), mn.Create(group_y))
        self.play(mn.FadeIn(bullets[0]))
        self.next_section()
        self.play(mn.Uncreate(joint_prob), mn.Uncreate(group_x), mn.Uncreate(group_y))
        self.play(mn.Create(d_square), mn.Create(d_triangle))
        self.next_section()
        ut_cells, ut_cells_vgroup = _upper_triangular_cells(d_square)
        self.play(
            mn.Uncreate(d_triangle),
            mn.LaggedStart(
                *(mn.FadeIn(cell) for cell in ut_cells_vgroup),
                lag_ratio=0.1,
            ),
        )
        self.play(mn.FadeIn(bullets[1]))
        self.next_section()
        self.play(
            mn.FadeToColor(ut_cells[1][3], color=mn.BLUE),  # pyright: ignore[reportArgumentType]
            mn.Create(sub_rect_list[1]),
            mn.Create(sub_rect_list[4]),
        )
        self.play(mn.FadeIn(bullets[2]), mn.FadeIn(bullets[3]))
        self.wait()
