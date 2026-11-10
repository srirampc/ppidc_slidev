import typing as t

import manim as mn
import manim.typing as mnt
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import default_config, scene_header, theme_background


class Tangents:
    line_bottom: mn.Line
    line_top: mn.Line
    line_mid: mn.Line
    dot_bottom: mn.Dot
    dot_top: mn.Dot
    dot_mid: mn.Dot
    nu_label: mn.MathTex
    rho_label: mn.MathTex

    def __init__(
        self,
        src_pt: mnt.Point3D,
        z_pt: mnt.Point3D,
        z_circle: mn.Circle,
        color: mn.ManimColor,
        label: str,
    ) -> None:
        r: float = z_circle.radius
        pt_bottom: mnt.Vector3D = z_pt + r * mn.DOWN
        pt_top: mnt.Vector3D = z_pt + r * (
            mn.UP + mn.LEFT if src_pt[0] < 0 else mn.UP + mn.RIGHT
        ) / float(np.sqrt(2))  # pyright: ignore[reportAny]
        # Line aimed at the circle bottom
        self.line_bottom = mn.Line(src_pt, pt_bottom, color=color)
        self.line_bottom.z_index = z_circle.z_index - 1
        self.dot_bottom = mn.Dot(pt_bottom, color=color, radius=0.04)
        mid_bottom = (src_pt + pt_bottom) / 2
        self.nu_label = mn.MathTex(rf"\nu({label})", fill_color=color).next_to(
            mid_bottom, 2 * mn.DOWN, buff=0.15
        )
        # Line aimed at the circle top
        self.line_top = mn.Line(src_pt, pt_top, color=color)
        self.line_top.z_index = z_circle.z_index - 1
        self.dot_top = mn.Dot(pt_top, color=color, radius=0.04)
        mid_top = (src_pt + pt_top) / 2
        self.rho_label = mn.MathTex(rf"\rho({label})", fill_color=color).next_to(
            mid_top, 3.5 * mn.UP, buff=0.15
        )
        # Line aimed at the circle center, ending at the circle's edge
        to_center: mnt.Vector3D = z_pt - src_pt
        pt_mid = z_pt - r * to_center / float(np.linalg.norm(to_center))
        self.line_mid = mn.Line(src_pt, pt_mid, color=color)
        self.line_mid.z_index = z_circle.z_index - 1
        self.dot_mid = mn.Dot(pt_mid, color=color, radius=0.04)


class PUC(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        header_txt = scene_header("Partial Unique Contribution (PUC)", cfg)
        x_pt = 3 * mn.LEFT + 1 * mn.DOWN
        y_pt = 3 * mn.RIGHT + 1 * mn.DOWN
        line_xy = mn.Line(x_pt, y_pt).set_color(cfg.txt_color)
        mid_xy = line_xy.get_midpoint()
        x_dot = mn.Dot(x_pt, color=cfg.txt_color)
        y_dot = mn.Dot(y_pt, color=cfg.txt_color)
        x_label = mn.MathTex("X", fill_color=cfg.txt_color).next_to(
            line_xy.get_start(), mn.LEFT
        )
        y_label = mn.MathTex("Y", fill_color=cfg.txt_color).next_to(
            line_xy.get_end(), mn.RIGHT
        )
        xy_label = mn.MathTex("I(X, Y)", fill_color=cfg.txt_color).next_to(
            mid_xy, 1.2 * mn.DOWN
        )
        z_pt = line_xy.get_midpoint() + 3 * mn.UP
        # z_dot = mn.Dot(z_pt, color=cfg.txt_color)
        z_circle = mn.Circle(radius=0.5, color=cfg.txt_color).move_to(z_pt)
        z_label = mn.MathTex("Z", fill_color=cfg.txt_color).move_to(z_pt)
        puc_label = mn.MathTex(
            r"\gamma(X, Y) = \frac{\nu(X)}{I(X,Y)} + \frac{\nu(Y)}{I(X,Y)}",
            fill_color=cfg.txt_color
        ).next_to(xy_label, mn.DOWN)
        puc_box = mn.SurroundingRectangle(puc_label, color=mn.YELLOW, buff=0.15)

        x_tangents = Tangents(x_pt, z_pt, z_circle, mn.RED, "X")
        y_tangents = Tangents(y_pt, z_pt, z_circle, mn.BLUE, "Y")

        # Halves of the XY line used as transform sources for the tangents
        half_x = mn.Line(x_pt, mid_xy)
        half_y = mn.Line(mid_xy, y_pt)

        self.play(mn.Create(header_txt))
        self.play(
            mn.Create(line_xy),
            mn.Create(x_dot),
            mn.Create(y_dot),
            mn.Write(x_label),
            mn.Write(y_label),
            mn.Write(xy_label),
        )
        self.next_section()
        self.play(mn.Create(z_circle), mn.Write(z_label))
        self.next_section()
        self.play(
            mn.TransformFromCopy(half_y, x_tangents.line_bottom),
            mn.TransformFromCopy(half_x, x_tangents.line_top),
        )
        self.play(
            mn.FadeIn(x_tangents.dot_bottom),
            mn.FadeIn(x_tangents.dot_top),
            mn.Write(x_tangents.nu_label),
            mn.Write(x_tangents.rho_label),
        )
        self.next_section()
        self.play(
            mn.TransformFromCopy(half_y.reverse_direction(), y_tangents.line_bottom),
            mn.TransformFromCopy(half_y.reverse_direction(), y_tangents.line_top),
        )
        self.play(
            mn.FadeIn(y_tangents.dot_bottom),
            mn.FadeIn(y_tangents.dot_top),
            mn.Write(y_tangents.nu_label),
            mn.Write(y_tangents.rho_label),
        )
        self.next_section()
        self.play(
            mn.FadeOut(x_tangents.line_top),
            mn.FadeOut(y_tangents.line_top),
            mn.FadeOut(x_tangents.dot_top),
            mn.FadeOut(y_tangents.dot_top),
            mn.FadeOut(x_tangents.rho_label),
            mn.FadeOut(y_tangents.rho_label),
        )
        self.next_section()
        self.play(
            mn.Transform(x_tangents.line_bottom, x_tangents.line_mid),
            mn.Transform(y_tangents.line_bottom, y_tangents.line_mid),
            mn.Transform(x_tangents.dot_bottom, x_tangents.dot_mid),
            mn.Transform(y_tangents.dot_bottom, y_tangents.dot_mid),
            x_tangents.nu_label.animate.shift(1.5 * mn.UP),
            y_tangents.nu_label.animate.shift(1.5 * mn.UP),
            mn.Write(puc_label),
            mn.Create(puc_box),
        )
        self.wait()
