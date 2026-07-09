from typing import NamedTuple

import manim as mn
import manim.typing as mnt

class MatParams(NamedTuple):
    color: mn.ManimColor
    name: str
    col_name: str
    row_name: str
    col_off: float
    row_off: float


class MatrixRect:
    def __init__(self, rect: mn.Rectangle, vertices: mnt.Point3D_Array, rp: MatParams):
        self.rect = rect
        self.vertices = vertices
        self.rp = rp
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
        self.arrows = [row_arrow, col_arrow, row_txt, col_txt]
