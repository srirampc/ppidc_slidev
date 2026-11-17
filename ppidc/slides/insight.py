import typing as t
from dataclasses import dataclass

import manim as mn
import numpy as np
from manim_themes import manim_theme as mtheme

from ppidc import (
    Config,
    PxTable,
    default_config,
    parts_by_tex,
    scene_header,
    theme_background,
)

# R is the original objective. The three lines of its derivation are A; B,
# which is A with the two summations swapped and p(y) distributed into both
# min arguments; and C, which writes each p(y)·I_s(y; ·) product as a single
# μ(y; ·).
_TEX_R = r"\sum_{Z \not\in \{X, Y\}} \rho((X, Z); Y)"
_TEX_A = r"\sum_Z \sum_y p(y) \min(I_s(y;X), I_s(y;Z))"
_TEX_A_FLIPPED = r"\sum_y \sum_Z p(y) \min(I_s(y;X), I_s(y;Z))"
_TEX_B = r"\sum_y \sum_Z \min(p(y) I_s(y;X), p(y) I_s(y;Z))"
_TEX_C = r"\sum_y \sum_Z \min(\mu(y;X), \mu(y;Z))"

# the two summations, which trade places between A and B
_SUMS = (r"\sum_Z", r"\sum_y")

# What each line exposes for its derivation: the pieces that get moved,
# split or morphed. Everything else is addressed as the line's residue.
_ISO_A = [*_SUMS, r"p(y)", r"I_s(y;X)", r"I_s(y;Z)"]
# B keeps p(y)·I_s in one piece, so that prefix can collapse into μ as a
# whole. The same line is also built with p(y) split out (_ISO_A) to receive
# the p(y) that A pulls inside; isolation does not affect typesetting, so
# both build to the same geometry.
_ISO_B = [*_SUMS, r"p(y) I_s"]
_ISO_C = [*_SUMS, r"\mu"]

# the column of equations left of the matrices, and the y of the four slots
_EQ_LEFT = -6.6
_EQ_WIDTH = 5.96
_SLOT_R = 2.7
_SLOT_A, _SLOT_B, _SLOT_C = 1.8, -0.4, -1.5
# Halfway between the bottom of the upper matrices and the top of the μ table.
_DIVIDER_Y = 0.4

# The lower calculation: the μ values for each choice of y, and the table
# that sorts them (S) and accumulates them (P). Both carry the same rows, so
# one target height keeps them aligned row for row.
_VM_HEIGHT = 3.9
# Each pass uses one entry from these lists. ⋮ stands for the rows the tables
# leave out, which have no value of their own.
_VM_VALUES = [
    {r"F": 1.37, r"D": 1.12, r"X": 1.86, r"W": 2.24},
    {r"F": 3.37, r"D": 1.42, r"X": 0.86, r"W": 2.14},
]
_VM_LABELS = [
    [r"F", r"D", r"X", r"\vdots", r"W", r"\vdots"],
    [r"W", r"X", r"D", r"\vdots", r"F", r"\vdots"],
]
# S is the same values in ascending order, which is what orders its rows — and
# the ⋮ rows go last so that the running total in P stays exact
_VMSP_LABELS = [
    [*sorted(vm_dict, key=vm_dict.__getitem__), r"\vdots", r"\vdots"]
    for vm_dict in _VM_VALUES
]
# the row the last section accounts for: everything below it, plus the rows
# tied with it, is the whole column
_BOXED_LABEL = r"X"
# width of the boxed expression in the margin right of the tables
_ROW_SUM_WIDTH = 1.4


def _value_cells(vmv_dict: dict[str, float], labels: list[str]) -> list[str]:
    """The tex of each row's μ(y; ·), top to bottom — a row that stands for
    others gets the column's continuation marker instead of a number."""
    return [
        f"{vmv_dict[label]:.2f}" if label in vmv_dict else r"\vdots" for label in labels
    ]


def _prefix_cells(vmv_dict: dict[str, float], labels: list[str]) -> list[str]:
    """The running total of the values *above* each row, top to bottom — the
    exclusive scan, so the first row is 0.

    Only exact while the ⋮ rows come last: once a row is elided, the total
    below it includes values the table does not show."""
    total = 0.0
    out: list[str] = []
    for label in labels:
        if label not in vmv_dict:
            out.append(r"\vdots")
            continue
        if out and out[-1] == r"\vdots":
            raise ValueError("the ⋮ rows have to stay last for P to be exact")
        out.append(f"{total:.2f}")
        total += vmv_dict[label]
    return out


def _equation(cfg: Config, tex: str, isolate: list[str]) -> mn.MathTex:
    """One line of the derivation, with `isolate` exposed as named parts."""
    return mn.MathTex(
        tex,
        color=cfg.txt_color,
        fill_color=cfg.txt_color,
        substrings_to_isolate=isolate,
    )


def _residue(line: mn.MathTex, *handled: mn.Mobject) -> mn.VGroup:
    """The glyphs of `line` that `handled` does not cover, in reading order.

    A derived line differs from its predecessor in the pieces passed as
    `handled` plus the odd shifted comma and bracket. Everything else keeps
    its reading order, so transforming these glyphs maps them one-to-one
    instead of smearing two whole equations into each other."""
    skip = {id(glyph) for mob in handled for glyph in mob.family_members_with_points()}
    return mn.VGroup(
        *(g for g in line.family_members_with_points() if id(g) not in skip)  # pyright: ignore[reportArgumentType]
    )


def _source_rows(original: list[str], reordered: list[str]) -> list[int]:
    """For each row of `reordered`, the index of the row it came from in
    `original`. Labels repeat (the ⋮ rows stand for all rows not shown), so
    repeats are matched in the order they appear."""
    unused = list(range(len(original)))
    out: list[int] = []
    for label in reordered:
        match = next((i for i in unused if original[i] == label), None)
        if match is None:
            raise ValueError(f"row {label!r} has no counterpart in {original}")
        unused.remove(match)
        out.append(match)
    return out


@dataclass
class _VMCalculation:
    """The lower tables, sorting moves, and final callouts for one choice of y."""

    vm_table: PxTable
    vmsp_table: PxTable
    labels: list[mn.VMobject]
    label_slots: list[np.ndarray]
    row_order: list[int]
    sp_columns: mn.VGroup
    row_box: mn.SurroundingRectangle
    row_sum: mn.VGroup
    sum_box: mn.SurroundingRectangle

    @property
    def mu_table(self) -> mn.Table:
        return self.vm_table.table

    @property
    def sorted_table(self) -> mn.Table:
        return self.vmsp_table.table

    @property
    def all_parts(self) -> mn.VGroup:
        """Everything shown for this pass, so it can be cleared in one move."""
        return mn.VGroup(
            self.mu_table,
            self.sorted_table,
            self.sp_columns,
            self.row_box,
            self.row_sum,
            self.sum_box,
        )

    def sort_animation(self) -> mn.AnimationGroup:
        """Slide rows that change place past each other on opposite arcs."""
        return mn.AnimationGroup(
            *(  # pyright: ignore[reportArgumentType]
                self.labels[row]
                .animate(path_arc=mn.PI / 2)  # pyright: ignore[reportCallIssue, reportUnknownMemberType]
                .move_to(self.label_slots[row])
                for row, from_row in enumerate(self.row_order)
                if from_row != row
            )
        )


def _make_vm_calculation(cfg: Config, index: int) -> _VMCalculation:
    """Lay out one lower calculation; dataset zero is shown for y=1."""
    y = index + 1
    vm_values = _VM_VALUES[index]
    vm_labels = _VM_LABELS[index]
    vmsp_labels = _VMSP_LABELS[index]

    vm_table = PxTable(
        cfg,
        len(vm_labels),
        1,
        vm_labels,
        [rf"\mu(y={y}; \cdot)"],
        corner_name="Z",
        body=[[cell] for cell in _value_cells(vm_values, vm_labels)],
    )
    vm_table.add_grid(cfg)
    _ = vm_table.table.scale_to_fit_height(_VM_HEIGHT)
    # Keep the lower-right table and its row sum clear of the theme logo.
    _ = vm_table.table.move_to(0.7 * mn.RIGHT + 1.8 * mn.DOWN)

    s_cells = _value_cells(vm_values, vmsp_labels)
    p_cells = _prefix_cells(vm_values, vmsp_labels)
    vmsp_table = PxTable(
        cfg,
        len(vmsp_labels),
        2,
        vmsp_labels,
        [rf"\mathsf{{S}}_{{y={y}}}", rf"\mathsf{{P}}_{{y={y}}}"],
        corner_name="Z",
        body=[[s, p] for s, p in zip(s_cells, p_cells, strict=True)],
    )
    vmsp_table.add_grid(cfg)
    _ = vmsp_table.table.scale_to_fit_height(_VM_HEIGHT)
    _ = vmsp_table.table.next_to(vm_table.table, mn.RIGHT, buff=0.2)

    # S and P are two columns, but add_grid only separates the row labels
    # from them; draw the divider between the two here.
    s_head, p_head = vmsp_table.column_headers()
    sp_divider = vmsp_table.v_line(
        (float(s_head.get_right()[0]) + float(p_head.get_left()[0])) / 2,  # pyright: ignore[reportAny]
        2,
        cfg,
    )

    # vmsp starts as its index column alone, holding the rows in the order
    # they appear in the μ table; S, P and the divider are held back until
    # the sort has happened, then revealed as one group.
    labels = t.cast(list[mn.VMobject], vmsp_table.row_labels())
    label_slots = [label.get_center().copy() for label in labels]
    row_order = _source_rows(vm_labels, vmsp_labels)
    for row, from_row in enumerate(row_order):
        if from_row != row:
            _ = labels[row].move_to(label_slots[from_row])
    # Collect every held-back piece before dropping any of them: the table
    # indexes its own entries, so it has to be whole while it is asked.
    entries = vmsp_table.table.get_entries()
    sp_rows = [
        (vmsp_table.cell(row, 0), vmsp_table.cell(row, 1))
        for row in range(len(vmsp_labels))
    ]
    sp_columns = mn.VGroup(
        *vmsp_table.column_headers(),  # pyright: ignore[reportArgumentType]
        *(cell for pair in sp_rows for cell in pair),  # pyright: ignore[reportArgumentType]
        sp_divider,
    )
    for mob in sp_columns:
        if any(entry is mob for entry in entries):
            entries.remove(mob)  # pyright: ignore[reportUnusedCallResult]

    # Box the row whose value stands for the whole tail of the ordering: P is
    # everything sorted below it, and the n-5 remaining rows are tied with it,
    # so the value summed over all n-2 rows is this expression.
    boxed = vmsp_labels.index(_BOXED_LABEL)
    s_cell, p_cell = sp_rows[boxed]
    row_box = mn.SurroundingRectangle(
        mn.VGroup(t.cast(mn.VMobject, s_cell), t.cast(mn.VMobject, p_cell)),
        color=mn.ORANGE,
        stroke_width=4,
        buff=0.12,
    )
    # The margin right of the tables is narrow, so the sum is stacked one row
    # per term instead of written on one line: the width it must fit is then
    # the widest row's — the product alone, not the whole sum — which is what
    # lets it set at a readable size.
    row_sum = mn.VGroup(
        mn.MathTex(p_cells[boxed], color=cfg.txt_color, fill_color=cfg.txt_color),
        mn.MathTex(r"+", color=cfg.txt_color, fill_color=cfg.txt_color),
        mn.MathTex(
            rf"{s_cells[boxed]} \times (n - {2 + boxed})",
            color=cfg.txt_color,
            fill_color=cfg.txt_color,
        ),
    ).arrange(mn.DOWN, buff=0.12)
    # Anchor it to the table's edge, not to the box (the box sits inside the
    # table), then centre it on the boxed row.
    _ = row_sum.scale_to_fit_width(_ROW_SUM_WIDTH)
    _ = row_sum.next_to(vmsp_table.table, mn.RIGHT, buff=0.18)
    _ = row_sum.set_y(row_box.get_center()[1])  # pyright: ignore[reportAny]
    sum_box = mn.SurroundingRectangle(
        row_sum,
        color=mn.GREEN,
        stroke_width=4,
        buff=0.12,
    )

    return _VMCalculation(
        vm_table=vm_table,
        vmsp_table=vmsp_table,
        labels=labels,
        label_slots=label_slots,
        row_order=row_order,
        sp_columns=sp_columns,
        row_box=row_box,
        row_sum=row_sum,
        sum_box=sum_box,
    )


class AlgoInsight(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        header_txt = scene_header("Algorithm: Key Insight", cfg, weight=mn.BOLD)

        # All four equations share a font size, fitted to the column left of
        # the tables, and a common left edge, so that each derivation reads as
        # a rewrite of the line above it rather than as a new line.
        eq_scale = _EQ_WIDTH / _equation(cfg, _TEX_B, _ISO_B).width

        def place(tex: str, isolate: list[str], y: float) -> mn.MathTex:
            line = _equation(cfg, tex, isolate)
            _ = line.scale(eq_scale)
            return line.move_to(mn.RIGHT * _EQ_LEFT + mn.UP * y, aligned_edge=mn.LEFT)

        eq_r = place(_TEX_R, [], _SLOT_R)
        eq_a = place(_TEX_A, _ISO_A, _SLOT_A)
        eq_b = place(_TEX_B, _ISO_B, _SLOT_B)
        eq_c = place(_TEX_C, _ISO_C, _SLOT_C)

        mx_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; X)"],
        )
        mx_table.add_grid(cfg)
        _ = mx_table.table.scale_to_fit_width(2.5)
        _ = mx_table.table.move_to(0.8 * mn.RIGHT + 1.8 * mn.UP)

        mz_table = PxTable(
            cfg,
            3,
            1,
            [r"y=1", r"y=2", r"y=3"],
            [r"I_s(y; Z)"],
        )
        mz_table.add_grid(cfg)
        _ = mz_table.table.scale_to_fit_width(2.5)
        _ = mz_table.table.next_to(mx_table.table, mn.RIGHT, buff=0.3)

        mx_dots_mid = (
            mn.MathTex(r"\cdots", color=cfg.txt_color, fill_color=cfg.txt_color)
            .next_to(mz_table.table, mn.RIGHT, buff=0.3)
            .scale(0.8)
        )

        mx_dots_end = (
            mn.MathTex(r"\cdots", color=cfg.txt_color, fill_color=cfg.txt_color)
            .next_to(mx_dots_mid, mn.RIGHT, buff=0.3)
            .scale(0.8)
        )
        top_brace = mn.BraceBetweenPoints(
            mz_table.table.get_top() + 1.2 * mn.LEFT,
            mz_table.table.get_top() + 2.8 * mn.RIGHT,
            direction=mn.UP,
        )
        br_size = (
            mn.MathTex(r"n-2", color=cfg.txt_color, fill_color=cfg.txt_color)
            .next_to(top_brace, mn.UP, buff=0.1)
            .scale(0.8)
        )

        first = _make_vm_calculation(cfg, 0)
        second = _make_vm_calculation(cfg, 1)

        box_eq_a = mn.SurroundingRectangle(
            eq_a,
            color=mn.BLUE,
            stroke_width=2,
            buff=0.1,
        )
        seq_complexity = (
            mn.MathTex(
                r"O(n) \textsf{ time per pair}",
                color=cfg.txt_color,
                fill_color=cfg.txt_color,
            )
            .next_to(eq_a, 0.5 * mn.DOWN, buff=0.3)
            .scale(0.8)
        )
        box_eq_c = mn.SurroundingRectangle(
            eq_c,
            color=mn.BLUE,
            stroke_width=2,
            buff=0.1,
        )
        novel_complexity = (
            mn.MathTex(
                r"O(1) \textsf{ time per pair}",
                color=cfg.txt_color,
                fill_color=cfg.txt_color,
            )
            .next_to(eq_c, 0.5 * mn.DOWN, buff=0.3)
            .scale(0.8)
        )
        novel_condition = (
            mn.MathTex(
                r"\textsf{given }  O(n^2 \log n ) \textsf{ prep. time}",
                color=cfg.txt_color,
                fill_color=cfg.txt_color,
            )
            .next_to(novel_complexity, 0.5 * mn.DOWN, buff=0.3)
            .scale(0.8)
        )

        section_divider = mn.Line(
            6.6 * mn.LEFT + _DIVIDER_Y * mn.UP,
            6.6 * mn.RIGHT + _DIVIDER_Y * mn.UP,
            color=mn.RED,
            stroke_width=4,
        )
        _ = header_txt.align_to(eq_r, mn.LEFT)

        self.play(mn.Create(header_txt))
        self.play(mn.Write(eq_r))
        self.next_section()
        # The objective expands into A; the two I_s(y; ·) columns come from
        # the n×n matrices.
        self.play(
            mn.TransformFromCopy(eq_r, eq_a),
        )
        self.next_section()
        self.play(
            mn.Create(mx_table.table),
            mn.Write(mx_dots_mid),
            mn.Write(mx_dots_end),
            mn.Create(mz_table.table),
            mn.Create(top_brace),
            mn.Write(br_size),
        )
        self.wait()
        self.next_section()
        self.play(
            mn.Create(box_eq_a),
            mn.Write(seq_complexity),
        )
        # Separate the original objective and matrices from the derivation
        # before A supplies the first line below the divider.
        self.play(mn.Create(section_divider))
        self.wait()
        self.next_section()
        # A -> B, part one: a copy of A drops into B's slot, still written as
        # A, and the two summations trade places there. They are equally wide
        # and no B-side piece is involved yet, so nothing else on the line
        # moves.
        a_at_b = eq_a.copy().move_to(eq_b, aligned_edge=mn.LEFT)
        self.play(mn.TransformFromCopy(eq_a, a_at_b))
        self.wait()
        a_flipped = place(_TEX_A_FLIPPED, _ISO_A, _SLOT_B)
        sums_a = [parts_by_tex(a_at_b, s)[0] for s in _SUMS]
        # Both sums arc through a half circle: they travel in opposite
        # directions, so one bows over the line and the other under it and
        # they pass each other instead of colliding.
        self.play(
            *(
                mn.Transform(src, parts_by_tex(a_flipped, s)[0], path_arc=mn.PI)
                for src, s in zip(sums_a, _SUMS, strict=True)
            )
        )
        self.wait()
        # A -> B, part two: p(y) is pulled inside the min. One copy becomes
        # the factor of the first argument, a second copy flies onto the
        # other, and the rest of the line slides to where B typesets it.
        b_targets = place(_TEX_B, _ISO_A, _SLOT_B)
        py_front = parts_by_tex(a_at_b, r"p(y)")[0]
        b_py = parts_by_tex(b_targets, r"p(y)")
        # the summations already sit where B wants them: the flip moved them
        sums_b = [parts_by_tex(b_targets, s)[0] for s in _SUMS]
        residue_a = _residue(a_at_b, py_front, *sums_a)
        self.play(
            mn.Transform(residue_a, _residue(b_targets, *b_py, *sums_b)),
            mn.Transform(py_front, b_py[0]),
            # the copy arcs over the first argument instead of dragging through
            # it on its way to the second (TransformFromCopy reverses time, so
            # its arc bows opposite to Transform's for the same sign)
            mn.TransformFromCopy(py_front, b_py[1], path_arc=mn.PI / 2),
        )
        self.wait()
        # The animated pieces have landed exactly on B's layout. Swap them for
        # the real B so the next section can cut B up by sub-expression; the
        # part groups above were registered with the scene, so they have to go
        # with the line they were cut from.
        self.remove(a_at_b, py_front, residue_a, *sums_a, b_py[1])  # pyright: ignore[reportUnusedCallResult]
        self.add(eq_b)  # pyright: ignore[reportUnusedCallResult]
        self.wait()
        self.next_section()
        # B -> C: a copy of B drops into C's slot, then each p(y)·I_s prefix
        # collapses into a single μ while its (y; ·) argument stays put.
        b_at_c = eq_b.copy().move_to(eq_c, aligned_edge=mn.LEFT)
        self.play(mn.TransformFromCopy(eq_b, b_at_c))
        self.wait()
        heads = parts_by_tex(b_at_c, r"p(y) I_s")
        mus = parts_by_tex(eq_c, r"\mu")
        residue_c = _residue(b_at_c, *heads)
        self.play(
            mn.Transform(residue_c, _residue(eq_c, *mus)),
            *(mn.Transform(head, mu) for head, mu in zip(heads, mus, strict=True)),
        )
        self.wait()
        self.next_section()

        def play_sort_and_summary(calculation: _VMCalculation) -> None:
            """Give each pass the same sort, S/P, and final-answer steps."""
            self.play(calculation.sort_animation())
            # S and P appear only after the index column has reached its order.
            self.play(mn.Create(calculation.sp_columns))
            self.wait()
            self.next_section()
            self.play(
                mn.Create(calculation.row_box),
            )
            self.wait()
            self.next_section()
            self.play(
                mn.Create(calculation.sum_box),
                mn.Write(calculation.row_sum),
            )
            self.wait()

        # First pass: μ(y=1; ·), with the S/P table's index column initially
        # holding the μ table's unsorted row order.
        self.play(mn.Create(first.mu_table))
        self.wait()
        self.next_section()
        self.play(mn.Create(first.sorted_table))
        play_sort_and_summary(first)
        self.next_section()

        # Clear the first tables and both callouts, and bring in the second
        # pass from outside the right edge; the upper derivation stays intact.
        second_tables = mn.VGroup(second.mu_table, second.sorted_table)
        _ = second_tables.shift(mn.config.frame_width * mn.RIGHT)
        old_parts = first.all_parts
        self.play(
            mn.FadeOut(old_parts, shift=mn.LEFT),
            second_tables.animate.shift(mn.config.frame_width * mn.LEFT),
        )
        _ = self.remove(old_parts)
        self.wait()
        play_sort_and_summary(second)
        self.next_section()
        self.play(
            mn.Create(box_eq_c),
            mn.Write(novel_complexity),
            mn.Write(novel_condition),
        )
