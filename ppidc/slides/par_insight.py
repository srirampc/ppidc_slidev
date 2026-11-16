import itertools
import typing as t

import manim as mn
from manim_themes import manim_theme as mtheme

from ppidc import (
    Config,
    PxTable,
    default_config,
    parts_by_tex,
    scene_header,
    theme_background,
)

_VM_HEIGHT = 2.9
# the values of the rows the tables spell out; ⋮ stands for the rows they leave
# out, which have no value of their own
_VM_VALUES = [
    {r"F": 1.37, r"D": 1.12, r"X": 1.86, r"W": 2.24},
    {r"F": 3.37, r"D": 1.42, r"X": 0.86, r"W": 2.14},
]
_VM_LABELS = [r"F", r"D", r"X", r"\vdots", r"W", r"\vdots"]
# S is the same values in ascending order, which is what orders its rows — and
# the ⋮ rows go last so that the running total in P stays exact
_VMSP_LABELS = [
    [*sorted(vm_dict, key=vm_dict.__getitem__), r"\vdots"] for vm_dict in _VM_VALUES
]
#
#


def _const_cells(c_val: str, labels: list[str], vm_dict: dict[str, float]) -> list[str]:
    return [c_val if label in vm_dict else r"\vdots" for label in labels]


def _value_cells(labels: list[str], vm_dict: dict[str, float]) -> list[str]:
    """The tex of each row's μ(y=1; ·), top to bottom — a row that stands for
    others gets the column's continuation marker instead of a number."""
    return [
        f"{vm_dict[label]:.2f}" if label in vm_dict else r"\vdots" for label in labels
    ]


def _prefix_cells(labels: list[str], vm_dict: dict[str, float]) -> list[str]:
    """The running total of the values *above* each row, top to bottom — the
    exclusive scan, so the first row is 0.

    Only exact while the ⋮ rows come last: once a row is elided, the total
    below it includes values the table does not show."""
    total = 0.0
    out: list[str] = []
    for label in labels:
        if label not in vm_dict:
            out.append(r"\vdots")
            continue
        if out and out[-1] == r"\vdots":
            raise ValueError("the ⋮ rows have to stay last for P to be exact")
        out.append(f"{total:.2f}")
        total += vm_dict[label]
    return out


def _vm_table_cells(y: int) -> tuple[list[str], list[str], list[str], list[str]]:
    vm_dict = _VM_VALUES[y]
    vm_labels = _VMSP_LABELS[y]
    y_cells = _const_cells("y=" + str(y + 1), vm_labels, vm_dict)
    s_cells = _value_cells(vm_labels, vm_dict)
    p_cells = _prefix_cells(vm_labels, vm_dict)
    return vm_labels, y_cells, s_cells, p_cells


def _vm_label_cells(y: int) -> list[str]:
    vm_dict = _VM_VALUES[y]
    return [
        f"{vm_dict[label]:.2f}" if label in vm_dict else r"\vdots"
        for label in _VM_LABELS
    ]


class ParAlgoInsight(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)
        _ = self.add(theme_background())

    @t.override
    def construct(self) -> None:
        cfg = default_config()
        header_txt = scene_header("Parallel Algorithm", cfg, weight=mn.BOLD)

        labels1, y_cells1, s_cells1, p_cells1 = _vm_table_cells(0)
        labels2, y_cells2, s_cells2, p_cells2 = _vm_table_cells(1)
        vms1_table = PxTable(
            cfg,
            len(y_cells1),
            3,
            y_cells1,
            [r"\mathsf{R}_{y=1}", r"\mathsf{S}_{y=1}", r"\mathsf{P}_{y=1}"],
            body=[
                [c, s, p] for c, s, p in zip(labels1, s_cells1, p_cells1, strict=True)
            ],
        )
        vms1_table.add_grid(cfg, column=False)
        _ = vms1_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vms1_table.table.move_to(4.5 * mn.LEFT + 1.45 * mn.UP)

        vms2_table = PxTable(
            cfg,
            len(y_cells2),
            3,
            y_cells2,
            [r"\mathsf{R}_{y=2}", r"\mathsf{S}_{y=2}", r"\mathsf{P}_{y=2}"],
            body=[
                [c, s, p] for c, s, p in zip(labels2, s_cells2, p_cells2, strict=True)
            ],
        )
        vms2_table.add_grid(cfg, column=False)
        _ = vms2_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vms2_table.table.next_to(vms1_table.table, mn.DOWN, buff=0.2)

        vm1_table = PxTable(
            cfg,
            len(_VM_LABELS),
            1,
            _VM_LABELS,
            [r"\mu(y=1; \cdot)"],
            body=[[cell] for cell in _vm_label_cells(0)],
        )
        vm1_table.add_grid(cfg)
        _ = vm1_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vm1_table.table.next_to(vms1_table.table, mn.RIGHT, buff=0.2)
        vmsp1_table = PxTable(
            cfg,
            len(labels1),
            2,
            labels1,
            [r"\mathsf{S}_{y=1}", r"\mathsf{P}_{y=1}"],
            body=[[s, p] for s, p in zip(s_cells1, p_cells1, strict=True)],
        )
        vmsp1_table.add_grid(cfg)
        _ = vmsp1_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vmsp1_table.table.next_to(vm1_table.table, mn.RIGHT, buff=0.2)
        vm1_group = mn.VGroup(vm1_table.table, vmsp1_table.table)
        vm2_table = PxTable(
            cfg,
            len(_VM_LABELS),
            1,
            _VM_LABELS,
            [r"\mu(y=2; \cdot)"],
            body=[[cell] for cell in _vm_label_cells(1)],
        )
        vm2_table.add_grid(cfg)
        _ = vm2_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vm2_table.table.next_to(vm1_table.table, mn.DOWN, buff=0.2)
        vmsp2_table = PxTable(
            cfg,
            len(labels2),
            2,
            labels1,
            [r"\mathsf{S}_{y=2}", r"\mathsf{P}_{y=2}"],
            body=[[s, p] for s, p in zip(s_cells2, p_cells2, strict=True)],
        )
        vmsp2_table.add_grid(cfg)
        _ = vmsp2_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vmsp2_table.table.next_to(vm2_table.table, mn.RIGHT, buff=0.2)

        vm2_group = mn.VGroup(vm2_table.table, vmsp2_table.table)

        vms_full_table = PxTable(
            cfg,
            len(y_cells1 + y_cells2),
            3,
            y_cells1 + y_cells2,
            [r"\mathsf{R}", r"\mathsf{S}", r"\mathsf{P}"],
            corner_name=r"\mathsf{Q}",
            body=[
                [c, s, p]
                for c, s, p in zip(
                    labels1 + labels2,
                    s_cells1 + s_cells2,
                    p_cells1 + p_cells2,
                    strict=True,
                )
            ],
        )
        vms_full_table.add_grid(cfg, column=False)
        _ = vms_full_table.table.scale_to_fit_height(2.2 * _VM_HEIGHT)
        _ = vms_full_table.table.next_to(vm1_table.table, mn.LEFT, buff=0.2).shift(
            0.5 * vms1_table.table.height * mn.DOWN
        )

        tuple_list = [
            [yl.replace("y=", ""), str(idx), c, s, p]
            if s != r"\vdots"
            else ["9", idx, "Z", "", ""]
            for yl, idx, c, s, p in zip(
                y_cells1 + y_cells2,
                itertools.chain(range(len(y_cells1)), range(len(y_cells2))),
                labels1 + labels2,
                s_cells1 + s_cells2,
                p_cells1 + p_cells2,
                strict=True,
            )
        ]
        sorted_tuple_list = sorted(tuple_list, key=lambda x: (x[2], x[0]))
        # For each destination row, find the matching original row. Repeated
        # tuples are matched in their original order.
        unused_source_rows = list(range(len(tuple_list)))
        source_row_by_target: list[int] = []
        for target in sorted_tuple_list:
            source_row = next(
                row for row in unused_source_rows if tuple_list[row] == target
            )
            unused_source_rows.remove(source_row)
            source_row_by_target.append(source_row)

        tuple_table = PxTable(
            cfg,
            len(y_cells1 + y_cells2),
            1,
            None,
            [r"\rho \mathsf{-tuples}"],
            body=[
                [rf"\langle Y, {c}, {yl}, ({idx}, {s}, {p}) \rangle"]
                if s
                else [r"\langle \dots, \dots, \dots, \dots   \rangle"]
                for yl, idx, c, s, p in tuple_list
            ],
        )
        tuple_table.add_grid(cfg, column=False)
        _ = tuple_table.table.scale_to_fit_height(2.2 * _VM_HEIGHT)
        _ = tuple_table.table.next_to(vms_full_table.table, mn.RIGHT, buff=0.3)

        sorted_tuple_table = PxTable(
            cfg,
            len(y_cells1 + y_cells2),
            1,
            None,
            [r"\textrm{sorted } \rho \mathsf{-tuples}"],
            body=[
                [rf"\langle Y, {c}, {yl.replace('y=', '')}, ({idx}, {s}, {p}) \rangle"]  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                if s
                else [r"\langle \dots, \dots, \dots, \dots   \rangle"]
                for yl, idx, c, s, p in sorted_tuple_list
            ],
        )
        sorted_tuple_table.add_grid(cfg, column=False)
        _ = sorted_tuple_table.table.scale_to_fit_height(2.2 * _VM_HEIGHT)
        _ = sorted_tuple_table.table.next_to(tuple_table.table, mn.RIGHT, buff=0.3)
        tuple_cells = [tuple_table.cell(row, 0) for row in range(len(tuple_list))]
        sorted_cells = [
            sorted_tuple_table.cell(row, 0) for row in range(len(sorted_tuple_list))
        ]
        # Keep the sorted table's grid and header, but hold its values back so
        # the sorting animation creates them from the matching source rows.
        sorted_entries = sorted_tuple_table.table.get_entries()
        for cell in sorted_cells:
            sorted_entries.remove(cell)

        # Four horizontal cuts divide the complete table, and therefore the
        # two tuple views aligned with it, into p logical partitions.
        row_ys = [label.get_y() for label in vms_full_table.row_labels()]
        cut_specs = [
            ("0", (row_ys[1] + row_ys[2]) / 2),  # between the second and third rows
            ("1", (row_ys[3] + row_ys[4]) / 2),  # below the fourth row
            ("p-2", (row_ys[-3] + row_ys[-2]) / 2),  # above the final two rows
            ("p-1", float(vms_full_table.table.get_bottom()[1]) - 0.1),
        ]
        cut_lines: list[mn.Line] = []
        cut_labels: list[mn.MathTex] = []
        label_x = float(sorted_tuple_table.table.get_right()[0]) + 1.5
        for name, y in cut_specs:
            line = mn.Line(
                [float(vms_full_table.table.get_left()[0]), y, 0],  # pyright: ignore[reportArgumentType]
                [float(sorted_tuple_table.table.get_right()[0]) + 2.0, y, 0],  # pyright: ignore[reportArgumentType]
                color=mn.RED,
                stroke_width=4,
            )
            label = (
                mn.MathTex(rf"{name}", fill_color=mn.RED)
                .scale(0.65)
                .move_to([label_x, y + 0.2, 0])  # pyright: ignore[reportArgumentType]
            )
            cut_lines.append(line)
            cut_labels.append(label)
        cut_dots = (
            mn.MathTex(r"\vdots", fill_color=mn.RED)
            .scale(0.65)
            .move_to([label_x, (cut_specs[1][1] + cut_specs[2][1]) / 2, 0])  # pyright: ignore[reportArgumentType]
        )

        gamma_boxes: list[mn.SurroundingRectangle] = []
        gamma_labels: list[mn.MathTex] = []
        for first_row, name in [(0, "D"), (2, "F"), (4, "W"), (6, "X")]:
            box = mn.SurroundingRectangle(
                mn.VGroup(*sorted_cells[first_row : first_row + 2]),  # pyright: ignore[reportArgumentType]
                color=mn.BLUE,
                stroke_width=4,
                buff=0.08,
            )
            label = (
                mn.MathTex(rf"\gamma(Y, {name})", fill_color=mn.BLUE)
                .scale(0.65)
                .next_to(box, mn.RIGHT, buff=0.2)
            )
            gamma_boxes.append(box)
            gamma_labels.append(label)

        self.play(mn.Create(header_txt))
        self.play(
            mn.Create(vm1_group),
            mn.Create(vm2_group),
        )
        self.wait()
        self.next_section()
        self.play(
            mn.TransformFromCopy(vm1_group, vms1_table.table),
        )
        self.play(
            mn.TransformFromCopy(vm2_group, vms2_table.table),
        )
        self.wait()
        self.next_section()
        self.play(
            mn.Uncreate(vm1_group),
            mn.Uncreate(vm2_group),
            mn.Uncreate(vms1_table.table),
            mn.Uncreate(vms2_table.table),
            mn.Create(vms_full_table.table),
        )
        self.wait()
        self.next_section()
        self.play(
            *(mn.Create(line) for line in cut_lines),
            *(mn.Write(label) for label in cut_labels),
            mn.Write(cut_dots),
        )
        self.wait()
        self.next_section()
        self.play(
            mn.Create(tuple_table.table),
        )
        self.wait()
        self.next_section()
        self.play(
           mn.Create(sorted_tuple_table.table),
        )
        sort_motions = [
            mn.TransformFromCopy(
                tuple_cells[source_row],
                sorted_cells[target_row],
                path_arc=0
                if source_row == target_row
                else mn.PI / 12
                if target_row > source_row
                else -mn.PI / 12,
            )
            for target_row, source_row in enumerate(source_row_by_target)
        ]
        self.play(mn.LaggedStart(*sort_motions, lag_ratio=0.08, run_time=4))
        self.wait()
        self.next_section()
        self.play(
            mn.LaggedStart(
                *(
                    mn.AnimationGroup(mn.Create(box), mn.Write(label))
                    for box, label in zip(gamma_boxes, gamma_labels, strict=True)
                ),
                lag_ratio=0.12,
                run_time=3,
            )
        )
        self.wait()
