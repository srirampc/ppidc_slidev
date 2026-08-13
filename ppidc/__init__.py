import typing as t
from dataclasses import dataclass, field

import manim as mn
import manim.typing as mnt
from manim_themes import manim_theme as mtheme

type ThemeType = t.Literal["dark", "light"]


class Config:
    def __init__(self, theme: ThemeType = "dark"):
        self.d_width = 2
        self.d_height = 4
        self.d_grid_step = 0.2
        self.d_grid_stroke = 1
        self.g_size = self.d_width

        self.theme: t.Literal["dark", "light"] = theme
        match self.theme:
            case "dark":
                self.manim_theme: str = "Catppuccin Mocha"
            case "light":
                self.manim_theme = "Catppuccin Latte"
        theme = mtheme.load_iterm2_theme(theme_name=self.manim_theme)
        # convert the theme colors to hex
        theme_colors = mtheme.convert_colors_to_manim_colors(theme)

        self.txt_color = theme_colors["Ansi 7 Color"].to_hex()
        # m.BLACK = theme_manim_colors['Ansi 0 Color']
        self.bkg_color: mn.ManimColor = theme_colors["Background Color"]
        self.d_color: mn.ManimColor = theme_colors[
            "Ansi 1 Color"
        ]  # mn.RED  # Color of the data matrix
        self.g_color: mn.ManimColor = theme_colors[
            "Ansi 4 Color"
        ]  # mn.BLUE  # Color of the graph adjacency matrix
        #
        # Set background
        mn.config.background_color = self.bkg_color


def default_theme() -> ThemeType:
    return "dark"


def default_config(theme: ThemeType | None = None) -> Config:
    return Config(theme=theme if theme else default_theme())


def matrix_rect(cfg: Config) -> mn.Rectangle:
    d_rect = mn.Rectangle(
        width=cfg.d_width,
        height=cfg.d_height,
        grid_xstep=cfg.d_grid_step,
        grid_ystep=cfg.d_grid_step,
    )
    d_rect.grid_lines.set_stroke(width=cfg.d_grid_stroke)
    return d_rect


def matrix_square_width(cfg: Config) -> mn.Square:
    d_rect = mn.Square(
        cfg.d_width,
        grid_xstep=cfg.d_grid_step,
        grid_ystep=cfg.d_grid_step,
    )
    d_rect.grid_lines.set_stroke(width=cfg.d_grid_stroke)
    return d_rect


@dataclass
class MatParams:
    color: mn.ManimColor
    name: str
    col_name: str
    row_name: str
    col_off: float
    row_off: float
    text_pos: mnt.Vector3D = field(default_factory=lambda: mn.ORIGIN)
    text_bg_rect: bool = True


class MatrixRect:
    def __init__(
        self, rect: mn.Rectangle, vertices: mnt.Point3D_Array, params: MatParams
    ):
        self.rect = rect
        self.vertices = vertices
        self.rp = params
        self.col_arrow = (
            mn.DoubleArrow(vertices[2], vertices[1], stroke_width=2.5, tip_length=0.2)
            .set_color(params.color)
            .shift(params.col_off * mn.LEFT)
        )
        self.row_arrow = (
            mn.DoubleArrow(vertices[0], vertices[1], stroke_width=2.5, tip_length=0.2)
            .set_color(params.color)
            .shift(params.row_off * mn.UP)
        )
        self.col_txt = (
            mn.MathTex(params.col_name, fill_color=params.color)
            .move_to(self.col_arrow.get_midpoint())
            .rotate(mn.PI / 2)
            .shift(params.col_off * mn.LEFT)
        )
        self.row_txt = (
            mn.MathTex(params.row_name, fill_color=params.color)
            .move_to(self.row_arrow.get_midpoint())
            .shift(params.row_off * mn.UP)
        )
        if (params.text_pos == mn.DOWN).all():
            self.text = mn.MathTex(params.name, fill_color=params.color).move_to(
                rect.get_bottom() + 0.2 * mn.DOWN, mn.UP
            )
        elif (params.text_pos == mn.UP).all():
            self.text = mn.MathTex(params.name, fill_color=params.color).move_to(
                self.row_txt.get_top() + 0.2 * mn.UP, mn.DOWN
            )
        else:
            self.text = mn.MathTex(params.name, fill_color=params.color).move_to(
                rect.get_center()
            )
        self.arrows = [self.row_arrow, self.col_arrow, self.row_txt, self.col_txt]
        self.text_bg_rect = None
        if params.text_bg_rect:
            self.text_bg_rect = mn.BackgroundRectangle(self.text)

    def text_object(self) -> mn.Mobject:
        if self.text_bg_rect is None:
            return self.text
        return mn.VGroup(self.text_bg_rect, self.text)
