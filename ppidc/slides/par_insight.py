import typing as t

import manim as mn
from manim_themes import manim_theme as mtheme

from ppidc import Config, PxTable, default_config, parts_by_tex

_VM_HEIGHT = 3.8
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


def _const_cells(c_val: str, labels: list[str],  vm_dict: dict[str, float]) -> list[str]:
    return [c_val if label in vm_dict else r"\vdots" for label in labels]


def _value_cells(labels: list[str], vm_dict: dict[str, float]) -> list[str]:
    """The tex of each row's μ(y=1; ·), top to bottom — a row that stands for
    others gets the column's continuation marker instead of a number."""
    return [
        f"{vm_dict[label]:.2f}" if label in vm_dict else r"\vdots"
        for label in labels
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
    y_cells = _const_cells(str(y + 1), vm_labels, vm_dict)
    s_cells = _value_cells(vm_labels, vm_dict)
    p_cells = _prefix_cells(vm_labels, vm_dict)
    return vm_labels, y_cells, s_cells, p_cells


class ParAlgoInsight(mn.Scene):
    @t.override
    def setup(self) -> None:
        mtheme.apply_theme(self, theme_name=default_config().manim_theme)

    @t.override
    def construct(self) -> None:
        cfg = default_config()

        labels1, y_cells1, s_cells1, p_cells1 = _vm_table_cells(0)
        vms1_table = PxTable(
            cfg,
            len(y_cells1),
            3,
            y_cells1,
            [r"\mathsf{R}", r"\mathsf{S}_y", r"\mathsf{P}_{y}"],
            corner_name=r"\mathsf{Q}",
            body=[[c, s, p] for c, s, p in zip(labels1, s_cells1, p_cells1, strict=True)],
        )
        vms1_table.add_grid(cfg, column=False)
        _ = vms1_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vms1_table.table.move_to(3 * mn.LEFT + 2 * mn.UP)

        labels2, y_cells2, s_cells2, p_cells2 = _vm_table_cells(1)
        vms2_table = PxTable(
            cfg,
            len(y_cells2),
            3,
            y_cells2,
            [r"\mathsf{R}", r"\mathsf{S}_y", r"\mathsf{P}_{y}"],
            corner_name=r"\mathsf{Q}",
            body=[[c, s, p] for c, s, p in zip(labels2, s_cells2, p_cells2, strict=True)],
        )
        vms2_table.add_grid(cfg, column=False)
        _ = vms2_table.table.scale_to_fit_height(_VM_HEIGHT)
        _ = vms2_table.table.move_to(3 * mn.LEFT + 2 * mn.DOWN)

        self.play(
            mn.Create(vms1_table.table),
            mn.Create(vms2_table.table),
        )
        self.wait()
