import typing as t

import manim as mn
from manim_themes import manim_theme as mtheme

from ppidc import Config, PxTable, default_config, parts_by_tex

# The three lines of the derivation. B is A with the two summations swapped
# and p(y) distributed into both min arguments; C writes each resulting
# p(y)·I_s(y; ·) product as a single μ(y; ·).
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

# the column of equations left of the matrices, and the y of the three slots
_EQ_LEFT = -6.6
_EQ_WIDTH = 5.96
_SLOT_A, _SLOT_B, _SLOT_C = 1.8, -0.4, -1.9

# The bottom row: the μ(y=1; ·) values of the n-2 rows, and the table that
# sorts them (S) and accumulates them (P). Both carry the same rows, so one
# target height keeps them aligned row for row.
_VM_HEIGHT = 3.9
# the values of the rows the tables spell out; ⋮ stands for the rows they leave
# out, which have no value of their own
_VM_VALUES = {r"F": 1.37, r"D": 1.12, r"X": 1.86, r"W": 2.24}
_VM_LABELS = [r"F", r"D", r"X", r"\vdots", r"W", r"\vdots"]
# S is the same values in ascending order, which is what orders its rows — and
# the ⋮ rows go last so that the running total in P stays exact
_VMSP_LABELS = [*sorted(_VM_VALUES, key=_VM_VALUES.__getitem__), r"\vdots", r"\vdots"]
# the row the last section accounts for: everything below it, plus the rows
# tied with it, is the whole column
_BOXED_LABEL = r"X"
# width of the boxed expression in the margin right of the tables
_ROW_SUM_WIDTH = 1.4


def _value_cells(labels: list[str]) -> list[str]:
    """The tex of each row's μ(y=1; ·), top to bottom — a row that stands for
    others gets the column's continuation marker instead of a number."""
    return [
        f"{_VM_VALUES[label]:.2f}" if label in _VM_VALUES else r"\vdots"
        for label in labels
    ]


def _prefix_cells(labels: list[str]) -> list[str]:
    """The running total of the values *above* each row, top to bottom — the
    exclusive scan, so the first row is 0.

    Only exact while the ⋮ rows come last: once a row is elided, the total
    below it includes values the table does not show."""
    total = 0.0
    out: list[str] = []
    for label in labels:
        if label not in _VM_VALUES:
            out.append(r"\vdots")
            continue
        if out and out[-1] == r"\vdots":
            raise ValueError("the ⋮ rows have to stay last for P to be exact")
        out.append(f"{total:.2f}")
        total += _VM_VALUES[label]
    return out


def _equation(cfg: Config, tex: str, isolate: list[str]) -> mn.MathTex:
    """One line of the derivation, with `isolate` exposed as named parts."""
    return mn.MathTex(tex, fill_color=cfg.txt_color, substrings_to_isolate=isolate)


def _residue(line: mn.MathTex, *handled: mn.Mobject) -> mn.VGroup:
    """The glyphs of `line` that `handled` does not cover, in reading order.

    A derived line differs from its predecessor in the pieces passed as
    `handled` plus the odd shifted comma and bracket. Everything else keeps
    its reading order, so transforming these glyphs maps them one-to-one
    instead of smearing two whole equations into each other."""
    skip = {id(glyph) for mob in handled for glyph in mob.family_members_with_points()}
    return mn.VGroup(*(g for g in line.family_members_with_points() if id(g) not in skip))


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


class AlgoInsight(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()

        # All three equations share a font size, fitted to the column left of
        # the tables, and a common left edge, so that each derivation reads as
        # a rewrite of the line above it rather than as a new line.
        eq_scale = _EQ_WIDTH / _equation(cfg, _TEX_B, _ISO_B).width

        def place(tex: str, isolate: list[str], y: float) -> mn.MathTex:
            line = _equation(cfg, tex, isolate)
            _ = line.scale(eq_scale)
            return line.move_to(mn.RIGHT * _EQ_LEFT + mn.UP * y, aligned_edge=mn.LEFT)

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
            mn.MathTex(r"\cdots", fill_color=cfg.txt_color)
            .next_to(mz_table.table, mn.RIGHT, buff=0.3)
            .scale(0.8)
        )

        mx_dots_end = (
            mn.MathTex(r"\cdots", fill_color=cfg.txt_color)
            .next_to(mx_dots_mid, mn.RIGHT, buff=0.3)
            .scale(0.8)
        )
        top_brace = mn.BraceBetweenPoints(
            mz_table.table.get_top() + 1.2 * mn.LEFT,
            mz_table.table.get_top() + 2.8 * mn.RIGHT,
            direction=mn.UP,
        )
        br_size = (
            mn.MathTex(r"n-2", fill_color=cfg.txt_color)
            .next_to(top_brace, mn.UP, buff=0.1)
            .scale(0.8)
        )

        vm1_table = PxTable(
            cfg,
            len(_VM_LABELS),
            1,
            _VM_LABELS,
            [r"\mu(y=1; \cdot)"],
            body=[[cell] for cell in _value_cells(_VM_LABELS)],
        )
        vm1_table.add_grid(cfg)
        _ = vm1_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vm1_table.table.move_to(mn.RIGHT + 1.8 * mn.DOWN)

        s_cells = _value_cells(_VMSP_LABELS)
        p_cells = _prefix_cells(_VMSP_LABELS)
        vmsp_table = PxTable(
            cfg,
            len(_VMSP_LABELS),
            2,
            _VMSP_LABELS,
            [r"\mathsf{S}_{y=1}", r"\mathsf{P}_{y=1}"],
            body=[[s, p] for s, p in zip(s_cells, p_cells, strict=True)],
        )
        vmsp_table.add_grid(cfg)
        _ = vmsp_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vmsp_table.table.next_to(vm1_table.table, mn.RIGHT, buff=0.2)

        # S and P are two columns, but add_grid only separates the row labels
        # from them; draw the divider between the two here.
        s_head, p_head = vmsp_table.column_headers()
        sp_divider = vmsp_table.v_line(
            (float(s_head.get_right()[0]) + float(p_head.get_left()[0])) / 2, 2, cfg
        )

        # vmsp starts as its index column alone, holding the rows in the order
        # they appear in the μ table; S, P and the divider are held back until
        # the sort has happened, then revealed as one group.
        labels = vmsp_table.row_labels()
        label_slots = [label.get_center().copy() for label in labels]
        row_order = _source_rows(_VM_LABELS, _VMSP_LABELS)
        for row, from_row in enumerate(row_order):
            if from_row != row:
                _ = labels[row].move_to(label_slots[from_row])
        # collect every held-back piece before dropping any of them: the table
        # indexes its own entries, so it has to be whole while it is asked
        entries = vmsp_table.table.get_entries()
        sp_rows = [
            (vmsp_table.cell(row, 0), vmsp_table.cell(row, 1))
            for row in range(len(_VMSP_LABELS))
        ]
        sp_columns = mn.VGroup(
            *vmsp_table.column_headers(),
            *(cell for pair in sp_rows for cell in pair),
            sp_divider,
        )
        for mob in sp_columns:
            if any(entry is mob for entry in entries):
                entries.remove(mob)

        self.play(mn.Write(eq_a))
        self.wait()
        self.next_section()
        # the two I_s(y; ·) columns of the n×n matrices
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
        self.remove(a_at_b, py_front, residue_a, *sums_a, b_py[1])
        self.add(eq_b)
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
        # the μ(y=1; ·) values of the n-2 rows, and the table that will hold
        # them sorted (its index column still in the μ table's row order)
        self.play(
            mn.Create(vm1_table.table),
            mn.Create(vmsp_table.table),
        )
        self.wait()
        self.next_section()
        # the index column is sorted: rows that change place slide past each
        # other on opposite sides (same arc sign, opposite directions)
        self.play(
            *(
                labels[row].animate(path_arc=mn.PI / 2).move_to(label_slots[row])
                for row, from_row in enumerate(row_order)
                if from_row != row
            )
        )
        self.wait()
        self.next_section()
        # S and P appear: the sorted values, and their running totals
        self.play(mn.Create(sp_columns))
        self.wait()
        self.next_section()
        # Box the row whose value stands for the whole tail of the ordering:
        # P is everything sorted below it, and the n-5 remaining rows are tied
        # with it, so the value summed over all n-2 rows is this expression.
        boxed = _VMSP_LABELS.index(_BOXED_LABEL)
        s_cell, p_cell = sp_rows[boxed]
        box = mn.SurroundingRectangle(
            mn.VGroup(s_cell, p_cell),
            color=mn.ORANGE,
            stroke_width=4,
            buff=0.12,
        )
        row_sum = mn.MathTex(
            rf"{p_cells[boxed]} + {s_cells[boxed]} \times (n - 5)",
            fill_color=cfg.txt_color,
        )
        # The margin right of the tables is narrow, so the annotation is sized
        # to it rather than to the equations. Anchor it to the table's edge, not
        # to the box (the box sits inside the table), then line it up with the
        # box vertically.
        _ = row_sum.scale_to_fit_width(_ROW_SUM_WIDTH)
        _ = row_sum.next_to(vmsp_table.table, mn.RIGHT, buff=0.18)
        _ = row_sum.set_y(box.get_center()[1])
        self.play(mn.Create(box), mn.Write(row_sum))
        self.wait()
