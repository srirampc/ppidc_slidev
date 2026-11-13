import os
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

import manim as mn
import manim.typing as mnt
from manim_themes import manim_theme as mtheme

type ThemeType = t.Literal["dark", "light"]


class Config:
    def __init__(self, theme: ThemeType = "dark"):
        # Setup theme
        self.theme: t.Literal["dark", "light"] = theme
        match self.theme:
            case "dark":
                self.manim_theme: str = "Catppuccin Mocha"
            case "light":
                self.manim_theme = "Catppuccin Latte"
        # load an convert the theme colors to hex
        theme_colors = mtheme.convert_colors_to_manim_colors(  # pyright: ignore[reportUnknownMemberType]
            mtheme.load_iterm2_theme(theme_name=self.manim_theme)  # pyright: ignore[reportAny]
        )

        self.txt_color: str = theme_colors["Ansi 7 Color"].to_hex()
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


g_DEFAULT_THEME: ThemeType = "light"
g_DEFAULT_CONFIG: Config | None = None


def default_theme() -> ThemeType:
    """The current default theme: PPIDC_THEME env override, else the
    module global (build_assets.py sets PPIDC_THEME per manim render)."""
    env_theme = os.environ.get("PPIDC_THEME")
    if env_theme in ("dark", "light"):
        return env_theme
    return g_DEFAULT_THEME


def set_default_theme(theme: ThemeType):
    global g_DEFAULT_THEME
    g_DEFAULT_THEME = theme


def default_config(theme: ThemeType | None = None) -> Config:
    global g_DEFAULT_CONFIG
    if g_DEFAULT_CONFIG is None or g_DEFAULT_CONFIG.theme != theme:
        g_DEFAULT_CONFIG = Config(theme=theme if theme else default_theme())
        return g_DEFAULT_CONFIG
    else:
        return g_DEFAULT_CONFIG


def theme_background() -> mn.ImageMobject:
    """The default Slidev theme background, fitted to the Manim frame."""
    background_path = (
        Path(__file__).resolve().parent.parent
        / "slides/ext/slidev-theme-spc-gt/assets/default-background.png"
    )
    background = mn.ImageMobject(str(background_path)).set(
        width=mn.config.frame_width, height=mn.config.frame_height
    )
    # Scene objects can deliberately use negative z-indices (PUC's tangents do).
    return background.set_z_index(-100)


def scene_header(title: str, cfg: Config, weight: str = mn.NORMAL) -> mn.Text:
    """A consistently positioned header for the animated slides."""
    return (
        mn.Text(title, font="Concourse T3", weight=weight)
        .set_color(cfg.txt_color)
        .move_to(3.5 * mn.UP)
    )


def parts_by_tex(expr: mn.MathTex, tex: str) -> list[mn.VGroup]:
    """All occurrences of `tex` isolated within `expr`. manim tags each
    isolated occurrence as its own SVG group, but `get_part_by_tex()` only
    returns the first one."""
    return [
        expr.id_to_vgroup_dict[match_id]
        for tex_str, match_id in expr.matched_strings_and_ids
        if tex_str == tex
    ]


@dataclass
class MatParams:
    color: mn.ManimColor
    name: str
    col_name: str
    row_name: str
    col_arrow_off: float
    row_arrow_off: float
    col_text_off: float = 0.2
    row_text_off: float = 0.2
    text_pos: mnt.Vector3D = field(default_factory=lambda: mn.ORIGIN)
    text_bg_rect: bool = True


class MatrixRect:
    def __init__(
        self, rect: mn.Rectangle, vertices: mnt.Point3D_Array, params: MatParams
    ):
        self.rect: mn.Rectangle = rect
        self.vertices: mnt.Point3D_Array = vertices
        self.rp: MatParams = params
        self.col_arrow: mn.DoubleArrow = (
            mn.DoubleArrow(vertices[2], vertices[1], stroke_width=2.5, tip_length=0.2)
            .set_color(params.color)
            .shift(params.col_arrow_off * mn.LEFT)
        )
        self.row_arrow: mn.DoubleArrow = (
            mn.DoubleArrow(vertices[0], vertices[1], stroke_width=2.5, tip_length=0.2)
            .set_color(params.color)
            .shift(params.row_arrow_off * mn.UP)
        )
        self.col_txt: mn.MathTex = (
            mn.MathTex(params.col_name, fill_color=params.color)
            .move_to(self.col_arrow.get_midpoint())
            .rotate(mn.PI / 2)
            .shift(params.col_text_off * mn.LEFT)
        )
        self.row_txt: mn.MathTex = (
            mn.MathTex(params.row_name, fill_color=params.color)
            .move_to(self.row_arrow.get_midpoint())
            .shift(params.row_text_off * mn.UP)
        )
        if (params.text_pos == mn.DOWN).all():  # pyright: ignore[reportAny]
            self.text: mn.MathTex = mn.MathTex(
                params.name, fill_color=params.color
            ).move_to(rect.get_bottom() + 0.2 * mn.DOWN, mn.UP)
        elif (params.text_pos == mn.UP).all():  # pyright: ignore[reportAny]
            self.text = mn.MathTex(params.name, fill_color=params.color).move_to(
                self.row_txt.get_top() + 0.2 * mn.UP, mn.DOWN
            )
        else:
            self.text = mn.MathTex(params.name, fill_color=params.color).move_to(
                rect.get_center()
            )
        self.arrows: list[mn.VMobject] = [
            self.row_arrow,
            self.col_arrow,
            self.row_txt,
            self.col_txt,
        ]
        self.text_bg_rect: mn.BackgroundRectangle | None = None
        if params.text_bg_rect:
            self.text_bg_rect = mn.BackgroundRectangle(self.text)

    def text_object(self) -> mn.Mobject:
        if self.text_bg_rect is None:
            return self.text
        return mn.VGroup(self.text_bg_rect, self.text)


class PxTable:
    table: mn.Table

    def __init__(
        self,
        cfg: Config,
        n_rows: int,
        n_cols: int,
        row_names: list[str] | None,
        col_names: list[str],
        corner_name: str | None = None,
        body: list[list[str]] | None = None,
    ) -> None:
        """A table of `n_rows` x `n_cols` body cells. `body` gives the tex of
        every body cell, row-major; without it each cell holds a `·`
        placeholder for the caller to animate into. Pass `row_names=None` to
        omit the index column."""
        self._has_index = row_names is not None
        self._body_col_start = 1 if self._has_index else 0
        if row_names is None and corner_name is not None:
            raise ValueError("corner_name requires an index column")
        assert len(col_names) == n_cols
        if row_names is not None:
            assert len(row_names) == n_rows
        if body is not None:
            assert len(body) == n_rows
            assert all(len(row) == n_cols for row in body)
        t_entries = [
            [
                mn.MathTex(r"\cdot", fill_color=cfg.txt_color)
                for _y in range(n_cols + self._body_col_start)
            ]
            for _x in range(n_rows + 1)
        ]
        if corner_name is not None:
            t_entries[0][0] = mn.MathTex(corner_name, fill_color=cfg.txt_color)
        t_entries[0][self._body_col_start:] = [
            mn.MathTex(col_name, fill_color=cfg.txt_color) for col_name in col_names
        ]
        if row_names is not None:
            for rx, r_name in zip(range(n_rows), row_names):
                t_entries[rx + 1][0] = mn.MathTex(r_name, fill_color=cfg.txt_color)
        if body is not None:
            for rx, row_tex in enumerate(body):
                for cx, tex in enumerate(row_tex):
                    t_entries[rx + 1][cx + self._body_col_start] = mn.MathTex(
                        tex, fill_color=cfg.txt_color
                    )

        mobj_gen: t.Callable[[mn.VMobject], mn.VMobject] = lambda m: m

        table = mn.Table(
            t_entries,
            # Entries are already Mobjects, so pass them through unchanged.
            element_to_mobject=mobj_gen,
            include_inner_lines=False,
            include_outer_lines=True,
            # element_to_mobject_config={"color": cfg.txt_color},
        )
        self.table = table

    def h_line(self, y: float, width: int, cfg: Config) -> mn.Line:
        return mn.Line(
            (float(self.table.get_left()[0]), y, 0.0),  # pyright: ignore[reportAny]
            (float(self.table.get_right()[0]), y, 0),  # pyright: ignore[reportAny]
            color=cfg.txt_color,
            stroke_width=width,
        )

    def v_line(self, x: float, width: int, cfg: Config) -> mn.Line:
        return mn.Line(
            (x, float(self.table.get_top()[1]), 0),  # pyright: ignore[reportAny]
            (x, float(self.table.get_bottom()[1]), 0),  # pyright: ignore[reportAny]
            color=cfg.txt_color,
            stroke_width=width,
        )

    def _grouped_entries(self) -> tuple[dict[float, list[mn.Mobject]], list[float]]:
        """Entries grouped by row: maps each row's y-coordinate to its cells
        sorted left to right, plus the row y's sorted top to bottom."""
        entries = self.table.get_entries()
        # group cells by row via their y-coordinate (robust, no label API needed)
        rows: dict[float, list[mn.Mobject]] = {}
        for e in entries:
            y = round(float(e.get_center()[1]), 6)  # pyright: ignore[reportAny]
            rows.setdefault(y, []).append(e)
        ys = sorted(rows.keys(), reverse=True)
        for row in rows.values():
            row.sort(key=lambda e: float(e.get_center()[0]))  # pyright: ignore[reportAny]
        return rows, ys

    def cell(self, row: int, col: int) -> mn.Mobject:
        """Entry at body row `row` and body column `col` (0-based from the
        top-left cell below/right of the header row and corner column)."""
        rows, ys = self._grouped_entries()
        return rows[ys[row + 1]][col + self._body_col_start]

    def row_labels(self) -> list[mn.Mobject]:
        """The entry naming each body row, top to bottom."""
        if not self._has_index:
            return []
        rows, ys = self._grouped_entries()
        return [rows[y][0] for y in ys[1:]]

    def column_headers(self) -> list[mn.Mobject]:
        """The header entry above each body column, left to right. The corner
        cell heading the row labels is not one of them."""
        rows, ys = self._grouped_entries()
        return rows[ys[0]][self._body_col_start:]

    def add_grid(self, cfg: Config, column: bool = True, row: bool = True) -> None:
        """Draw every grid line of the table: strong (width 6) for the
        outer border, the header-row separator, and the first-column
        separator; thin (width 2) for all remaining inner lines."""
        assert column == True or row == True
        rows, ys = self._grouped_entries()

        thin, _strong = 2, 6

        # all horizontal boundaries: outer top/bottom + one between each row pair
        row_borders: list[float] = (
            [rows[ys[0]][0].get_top()[1]]
            + [
                (rows[ys[i]][0].get_bottom()[1] + rows[ys[i + 1]][0].get_top()[1]) / 2
                for i in range(len(ys) - 1)
            ]
            + [rows[ys[-1]][0].get_bottom()[1]]
        )
        # all vertical boundaries: outer left/right + one between each column pair
        header_row = rows[ys[0]]
        col_borders: list[float] = (
            [header_row[0].get_left()[0]]
            + [
                (header_row[i].get_right()[0] + header_row[i + 1].get_left()[0]) / 2
                for i in range(len(header_row) - 1)
            ]
            + [header_row[-1].get_right()[0]]
        )

        # indices 0 and len-1 are the outer border; index 1 is the header
        # row / first column separator — those are strong, the rest thin
        grid = mn.VGroup(
            *(self.h_line(y, thin, cfg) for _i, y in enumerate(row_borders[1:2]))
            if row
            else (),
            *(self.v_line(x, thin, cfg) for _i, x in enumerate(col_borders[1:2]))
            if column
            else (),
        )
        _ = self.table.add(grid)
