"""
house.py — Ngôi nhà 2 tầng dựng từ các hình hộp (tường, sàn, cầu thang, mái, lan can, cửa sổ).
Đơn vị: mét. Nhà rộng 14m (trục X) x sâu 10m (trục Z), tâm ở gốc tọa độ.
Tầng trệt: y = 0 .. 2.8, sàn tầng 2 dày 0.2 (y 2.8..3.0), tầng 2: y = 3.0 .. 5.8, mái y 5.8..6.0.

Cách hoạt động: build_house() chạy MỘT LẦN, tạo danh sách PARTS gồm các hộp có màu.
draw_house() chỉ vẽ lại danh sách đó mỗi khung hình; collision dùng chính danh sách đó.
"""

from OpenGL.GL import (
    glColor3f, glColor4f, glEnable, glDisable,
    GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
)
from shapes import draw_box_at
import collision

# ── Kích thước nhà ──
HALF_W = 7.0       # nửa chiều rộng (trục X)
HALF_D = 5.0       # nửa chiều sâu (trục Z)
WALL_H = 2.8       # chiều cao tường mỗi tầng
WALL_T = 0.2       # độ dày tường
GROUND_TOP = 0.1   # mặt sàn tầng trệt
UPPER_TOP = 3.0    # mặt sàn tầng 2

# ── Cửa ──
DOOR_W = 1.0
DOOR_H = 2.1
WIN_W = 1.4
WIN_BOTTOM = 1.0   # mép dưới cửa sổ cách sàn tầng
WIN_TOP = 2.0      # mép trên cửa sổ cách sàn tầng

# ── Cầu thang: đầu thấp ở x=-2.0 (phía phòng khách), đi lên theo -X, sát tường sau ──
STEPS = 14                                    # số lần "bước lên" từ tầng trệt tới tầng 2
STEP_RISE = (UPPER_TOP - GROUND_TOP) / STEPS  # độ cao mỗi bậc (~0.207)
STEP_RUN = 0.35                               # chiều sâu mỗi bậc
STAIR_X0 = -HALF_W + WALL_T / 2               # mép trong tường trái = -6.9
STAIR_Z0 = -HALF_D + WALL_T / 2               # mép trong tường sau  = -4.9
STAIR_W = 1.2                                 # bề rộng cầu thang (theo Z)
STAIR_X1 = STAIR_X0 + STEPS * STEP_RUN        # đầu thấp của cầu thang = -2.0
STAIR_Z1 = STAIR_Z0 + STAIR_W                 # = -3.7
HOLE_X0 = STAIR_X0 + STEP_RUN                 # lỗ sàn tầng 2 (chừa 1 dải sàn sát tường trái)
HOLE_X1 = STAIR_X1

# ── Danh sách hộp của cả ngôi nhà ──
PARTS = []                 # mỗi phần tử: (màu, x0, x1, y0, y1, z0, z1)
_color = (1.0, 1.0, 1.0)   # màu hiện tại, các hộp tạo sau sẽ dùng màu này


def door(center):
    """Lỗ cửa ra vào: (tâm, rộng, cao_dưới, cao_trên)."""
    return (center, DOOR_W, 0.0, DOOR_H)


def window(center):
    """Lỗ cửa sổ: nằm lửng giữa tường."""
    return (center, WIN_W, WIN_BOTTOM, WIN_TOP)


def _set_color(r, g, b):
    global _color
    _color = (r, g, b)


def _box_range(x0, x1, y0, y1, z0, z1):
    """Thêm một hộp (theo 2 góc đối diện) vào danh sách, bỏ qua hộp rỗng."""
    if x1 - x0 <= 0 or y1 - y0 <= 0 or z1 - z0 <= 0:
        return
    PARTS.append((_color, x0, x1, y0, y1, z0, z1))


def _wall_segment(axis, fixed, a, b, y0, y1, base):
    """
    Một đoạn tường = 1 hộp.
    axis='x': tường chạy dọc X, đứng yên tại z=fixed.
    axis='z': tường chạy dọc Z, đứng yên tại x=fixed.
    base: cao độ chân tường (0 cho tầng trệt, 3.0 cho tầng 2).
    """
    t = WALL_T / 2.0
    if axis == 'x':
        _box_range(a, b, base + y0, base + y1, fixed - t, fixed + t)
    else:
        _box_range(fixed - t, fixed + t, base + y0, base + y1, a, b)


def build_wall(axis, fixed, start, end, openings=(), base=0.0):
    """Tường từ start tới end, khoét lỗ theo danh sách openings."""
    cursor = start
    for (center, width, low, high) in sorted(openings):
        o1 = center - width / 2.0
        o2 = center + width / 2.0
        _wall_segment(axis, fixed, cursor, o1, 0.0, WALL_H, base)   # tường đặc trước lỗ
        if low > 0:                                                  # bệ dưới lỗ
            _wall_segment(axis, fixed, o1, o2, 0.0, low, base)
        if high < WALL_H:                                            # lanh tô trên lỗ
            _wall_segment(axis, fixed, o1, o2, high, WALL_H, base)
        cursor = o2
    _wall_segment(axis, fixed, cursor, end, 0.0, WALL_H, base)       # tường đặc sau lỗ cuối


# ───────────────────────── SÀN ─────────────────────────

def build_ground_floors():
    """Sàn tầng trệt, mỗi phòng một màu. Dày 0.1m, mặt trên y=0.1."""
    _set_color(0.65, 0.45, 0.25)   # phòng khách: gỗ
    _box_range(-HALF_W, 1.0, 0.0, GROUND_TOP, -HALF_D, HALF_D)
    _set_color(0.55, 0.55, 0.75)   # phòng ăn: xanh tím nhạt
    _box_range(1.0, HALF_W, 0.0, GROUND_TOP, -HALF_D, 0.0)
    _set_color(0.85, 0.80, 0.65)   # bếp: be
    _box_range(1.0, HALF_W, 0.0, GROUND_TOP, 0.0, HALF_D)


def build_upper_slab():
    """
    Sàn tầng 2 (dày 0.2m, y 2.8..3.0) có LỖ CẦU THANG: x từ HOLE_X0 tới HOLE_X1,
    z từ STAIR_Z0 tới STAIR_Z1. Ghép 4 hộp bao quanh cái lỗ.
    """
    _set_color(0.80, 0.72, 0.58)
    y0, y1 = UPPER_TOP - 0.2, UPPER_TOP
    ex = HALF_W + WALL_T / 2.0
    ez = HALF_D + WALL_T / 2.0
    _box_range(-ex, ex, y0, y1, STAIR_Z1, ez)           # A: phía trước lỗ (cả chiều ngang)
    _box_range(HOLE_X1, ex, y0, y1, -ez, STAIR_Z1)      # B: bên phải lỗ
    _box_range(-ex, HOLE_X1, y0, y1, -ez, STAIR_Z0)     # C: phía sau lỗ (trên tường sau)
    _box_range(-ex, HOLE_X0, y0, y1, STAIR_Z0, STAIR_Z1)  # D: bên trái lỗ (dải sàn sát tường)


def build_stairs():
    """
    Cầu thang: 13 bậc, mỗi bậc là 1 hộp đặc từ sàn tầng trệt cao lên.
    Bậc i (i=0 là bậc thấp nhất, ở x=-2.0) có đỉnh ở GROUND_TOP + (i+1)*STEP_RISE.
    Từ bậc cuối (đỉnh 2.79) bước sang ngang là lên sàn tầng 2 (cao 3.0).
    """
    _set_color(0.55, 0.38, 0.22)
    for i in range(STEPS - 1):
        h = (i + 1) * STEP_RISE
        x1 = STAIR_X1 - i * STEP_RUN
        x0 = x1 - STEP_RUN
        _box_range(x0, x1, GROUND_TOP, GROUND_TOP + h, STAIR_Z0, STAIR_Z1)


def build_railing():
    """
    Lan can an toàn bảo vệ quanh lỗ cầu thang ở tầng 2.
    LỐI RA CẦU THANG (x từ -6.9 đến -5.3) để trống hoàn toàn để người chơi bước lên tầng 2.
    Lan can chỉ rào:
    - Cạnh trước (dọc z = STAIR_Z1 = -3.7) từ x = -5.3 đến x = STAIR_X1 (-2.0).
    - Cạnh bên (dọc x = STAIR_X1 = -2.0) từ z = STAIR_Z0 (-4.9) đến z = STAIR_Z1 (-3.7).
    """
    _set_color(0.42, 0.26, 0.14)
    r_start_x = -5.3
    r_end_x = STAIR_X1

    # 1. Lan can cạnh trước (z = STAIR_Z1): từ x = -5.3 đến -2.0
    # Tay vịn trên cùng
    _box_range(r_start_x, r_end_x + 0.05, UPPER_TOP + 0.85, UPPER_TOP + 0.90, STAIR_Z1 - 0.03, STAIR_Z1 + 0.03)
    # Các nan đứng cách đều
    num_bars = 7
    step_x = (r_end_x - r_start_x) / (num_bars - 1)
    for k in range(num_bars):
        bx = r_start_x + k * step_x
        _box_range(bx - 0.02, bx + 0.02, UPPER_TOP, UPPER_TOP + 0.85, STAIR_Z1 - 0.02, STAIR_Z1 + 0.02)

    # 2. Lan can cạnh bên (x = STAIR_X1): từ z = STAIR_Z0 đến z = STAIR_Z1
    _box_range(STAIR_X1 - 0.03, STAIR_X1 + 0.03, UPPER_TOP + 0.85, UPPER_TOP + 0.90, STAIR_Z0, STAIR_Z1)
    num_side_bars = 4
    step_z = (STAIR_Z1 - STAIR_Z0) / (num_side_bars - 1)
    for k in range(num_side_bars):
        bz = STAIR_Z0 + k * step_z
        _box_range(STAIR_X1 - 0.02, STAIR_X1 + 0.02, UPPER_TOP, UPPER_TOP + 0.85, bz - 0.02, bz + 0.02)


# ───────────────────────── TƯỜNG ─────────────────────────

def build_partitions(base):
    """Tường ngăn phòng (giống nhau ở cả hai tầng)."""
    # Tường x=1 chia phòng khách/sảnh với phần bên phải; 2 cửa thông sang 2 phòng
    build_wall('z', 1.0, -HALF_D, HALF_D, [door(-2.5), door(2.5)], base)
    # Tường z=0 chia phần bên phải làm đôi (phòng ăn/bếp hoặc ngủ 1/ngủ 2)
    build_wall('x', 0.0, 1.0, HALF_W, base=base)


def build_ground_walls():
    """Tường tầng trệt."""
    _set_color(0.93, 0.90, 0.80)
    e = HALF_W + WALL_T / 2.0       # kéo dài tường trước/sau để che góc nhà
    # Trước (z=+5): cửa chính x=-3, cửa sổ phòng khách x=-0.5, cửa sổ bếp x=4
    build_wall('x', HALF_D, -e, e, [door(-3.0), window(-0.5), window(4.0)])
    # Sau (z=-5): cửa sổ phòng khách x=-0.5, cửa sổ phòng ăn x=4
    build_wall('x', -HALF_D, -e, e, [window(-0.5), window(4.0)])
    # Trái (x=-7): 1 cửa sổ
    build_wall('z', -HALF_W, -HALF_D, HALF_D, [window(1.5)])
    # Phải (x=7): cửa sổ phòng ăn z=-2.5, cửa sổ bếp z=2.5
    build_wall('z', HALF_W, -HALF_D, HALF_D, [window(-2.5), window(2.5)])
    build_partitions(0.0)


def build_upper_walls():
    """Tường tầng 2 (chân tường ở y = UPPER_TOP)."""
    _set_color(0.93, 0.90, 0.80)
    e = HALF_W + WALL_T / 2.0
    b = UPPER_TOP
    build_wall('x', HALF_D, -e, e, [window(-3.0), window(4.0)], b)
    build_wall('x', -HALF_D, -e, e, [window(-0.5), window(4.0)], b)
    build_wall('z', -HALF_W, -HALF_D, HALF_D, [window(0.0)], b)
    build_wall('z', HALF_W, -HALF_D, HALF_D, [window(-2.5), window(2.5)], b)
    build_partitions(b)


def build_roof():
    """Mái phẳng trên đỉnh tường tầng 2, nhô ra 0.3m mỗi bên."""
    _set_color(0.45, 0.25, 0.20)
    _box_range(-HALF_W - 0.3, HALF_W + 0.3, UPPER_TOP + WALL_H, UPPER_TOP + WALL_H + 0.2,
               -HALF_D - 0.3, HALF_D + 0.3)


# ───────────────────────── CỬA SỔ & KÍNH ─────────────────────────

WINDOWS = [
    # (axis, fixed, center, base)
    # Tầng trệt (base = 0.0)
    ('x', HALF_D, -0.5, 0.0),
    ('x', HALF_D,  4.0, 0.0),
    ('x', -HALF_D, -0.5, 0.0),
    ('x', -HALF_D,  4.0, 0.0),
    ('z', -HALF_W,  1.5, 0.0),
    ('z', HALF_W,  -2.5, 0.0),
    ('z', HALF_W,   2.5, 0.0),
    # Tầng 2 (base = UPPER_TOP)
    ('x', HALF_D, -3.0, UPPER_TOP),
    ('x', HALF_D,  4.0, UPPER_TOP),
    ('x', -HALF_D, -0.5, UPPER_TOP),
    ('x', -HALF_D,  4.0, UPPER_TOP),
    ('z', -HALF_W,  0.0, UPPER_TOP),
    ('z', HALF_W,  -2.5, UPPER_TOP),
    ('z', HALF_W,   2.5, UPPER_TOP),
]


def draw_windows():
    """Vẽ khung gỗ và kính bán trong suốt cho tất cả các cửa sổ."""
    win_h = WIN_TOP - WIN_BOTTOM
    # 1. Vẽ khung gỗ mỏng
    glColor3f(0.35, 0.22, 0.12)
    for axis, fixed, center, base in WINDOWS:
        cy = base + (WIN_BOTTOM + WIN_TOP) / 2.0
        if axis == 'x':
            # Thanh ngang trên & dưới
            draw_box_at(center, base + WIN_BOTTOM, fixed, WIN_W, 0.04, WALL_T + 0.02)
            draw_box_at(center, base + WIN_TOP, fixed, WIN_W, 0.04, WALL_T + 0.02)
            # Thanh dọc 2 bên & nan giữa
            draw_box_at(center - WIN_W / 2.0, cy, fixed, 0.04, win_h, WALL_T + 0.02)
            draw_box_at(center + WIN_W / 2.0, cy, fixed, 0.04, win_h, WALL_T + 0.02)
            draw_box_at(center, cy, fixed, 0.03, win_h, WALL_T + 0.01)
        else:
            draw_box_at(fixed, base + WIN_BOTTOM, center, WALL_T + 0.02, 0.04, WIN_W)
            draw_box_at(fixed, base + WIN_TOP, center, WALL_T + 0.02, 0.04, WIN_W)
            draw_box_at(fixed, cy, center - WIN_W / 2.0, WALL_T + 0.02, win_h, 0.04)
            draw_box_at(fixed, cy, center + WIN_W / 2.0, WALL_T + 0.02, win_h, 0.04)
            draw_box_at(fixed, cy, center, WALL_T + 0.01, win_h, 0.03)

    # 2. Vẽ mặt kính bán trong suốt
    glEnable(GL_BLEND)
    glColor4f(0.65, 0.85, 0.95, 0.35)
    for axis, fixed, center, base in WINDOWS:
        cy = base + (WIN_BOTTOM + WIN_TOP) / 2.0
        if axis == 'x':
            draw_box_at(center, cy, fixed, WIN_W - 0.04, win_h - 0.04, 0.02)
        else:
            draw_box_at(fixed, cy, center, 0.02, win_h - 0.04, WIN_W - 0.04)
    glDisable(GL_BLEND)


# ───────────────────────── GỌI TỪ main.py ─────────────────────────

def build_house():
    """Dựng danh sách hộp MỘT LẦN và đăng ký toàn bộ vào hệ thống va chạm."""
    PARTS.clear()
    collision.clear()
    build_ground_floors()
    build_stairs()
    build_upper_slab()
    build_railing()
    build_ground_walls()
    build_upper_walls()
    build_roof()
    for (_color_unused, x0, x1, y0, y1, z0, z1) in PARTS:
        collision.add_box(x0, x1, y0, y1, z0, z1)


def draw_house():
    """Vẽ lại danh sách hộp mỗi khung hình."""
    for (color, x0, x1, y0, y1, z0, z1) in PARTS:
        glColor3f(*color)
        draw_box_at((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0,
                    x1 - x0, y1 - y0, z1 - z0)
