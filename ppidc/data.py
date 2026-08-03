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
    text_pos: mnt.Vector3D = field(default_factory=mnt.Vector3D)  # pyright: ignore[reportCallIssue, reportArgumentType]


class MatrixRect:
    def __init__(self, rect: mn.Rectangle, vertices: mnt.Point3D_Array, rp: MatParams):
        self.rect = rect
        self.vertices = vertices
        self.rp = rp
        if (rp.text_pos == mn.DOWN).all():
            self.text = mn.MathTex(
                rp.name, fill_color=rp.color
            ).move_to(rect.get_bottom() + 0.2 * mn.DOWN, mn.UP)
        else:
            self.text = mn.MathTex(rp.name, fill_color=rp.color).move_to(rect.get_center())
        col_arrow = (
            mn.DoubleArrow(vertices[2], vertices[1], stroke_width=2.5, tip_length=0.2)
            .set_color(rp.color)
            .shift(rp.col_off * mn.LEFT)
        )
        row_arrow = (
            mn.DoubleArrow(vertices[0], vertices[1], stroke_width=2.5, tip_length=0.2)
            .set_color(rp.color)
            .shift(rp.row_off * mn.UP)
        )
        col_txt = (
            mn.MathTex(rp.col_name, fill_color=rp.color)
            .move_to(col_arrow.get_midpoint())
            .rotate(mn.PI / 2)
            .shift(rp.col_off * mn.LEFT)
        )
        row_txt = (
            mn.MathTex(rp.row_name, fill_color=rp.color)
            .move_to(row_arrow.get_midpoint())
            .shift(rp.row_off * mn.UP)
        )
        self.row_arrow = row_arrow
        self.col_arrow = col_arrow
        self.row_txt = row_txt
        self.col_txt = col_txt
        self.arrows = [self.row_arrow, self.col_arrow, self.row_txt, self.col_txt]
