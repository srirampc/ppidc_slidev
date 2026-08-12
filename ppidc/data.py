from dataclasses import dataclass, field

import manim as mn
import manim.typing as mnt


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
            self.text_bg_rect =  mn.BackgroundRectangle(self.text)

    def text_object(self) -> mn.Mobject:
        if self.text_bg_rect is None:
            return self.text
        return mn.VGroup(self.text_bg_rect, self.text)
