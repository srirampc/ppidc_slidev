import manim as mn

BKG_COLOR = mn.BLACK
DM_WIDTH = 2
DM_HEIGHT = 4
DM_GRID_STEP = 0.2
DM_GRID_STROKE = 1
DM_COLOR: mn.ManimColor = mn.RED # Color of the data matrix
G_SIZE = DM_WIDTH
G_COLOR : mn.ManimColor = mn.BLUE # Color of the

#BKG_COLOR: mn.ManimColor = mn.GRAY_A
#TXT_COLOR: str = "#343434"


BKG_COLOR: mn.ManimColor = mn.ManimColor.from_hex("#121212")
TXT_COLOR: str = "#dfdfd6"

def matrix_rect() -> mn.Rectangle:
    d_rect = mn.Rectangle(
        width=DM_WIDTH,
        height=DM_HEIGHT,
        grid_xstep=DM_GRID_STEP,
        grid_ystep=DM_GRID_STEP,
    )
    d_rect.grid_lines.set_stroke(width=DM_GRID_STROKE)
    return d_rect
