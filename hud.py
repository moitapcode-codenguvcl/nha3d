"""
hud.py — Giao diện HUD 2D thuần OpenGL (không cần thư viện bên ngoài).
Hiển thị:
- Tâm ngắm (Crosshair) chính giữa màn hình.
- Thanh túi đồ Hotbar (phím Q, số 1..8) với ô chọn nổi bật.
- Bảng gợi ý thao tác động (Mở cửa, Đặt đồ, Xoay chiều bằng Space, Cầm lên ngắm 3D bằng V).
- Tên phòng người chơi đang đứng.
- Font vector đường nét (GL_LINES) vẽ trực tiếp mọi chữ/số rõ nét.
"""

from OpenGL.GL import (
    glMatrixMode, glPushMatrix, glPopMatrix, glLoadIdentity,
    glBegin, glEnd, glVertex2f, glColor3f, glColor4f,
    glEnable, glDisable, glLineWidth, glBlendFunc,
    GL_PROJECTION, GL_MODELVIEW, GL_QUADS, GL_LINES,
    GL_BLEND, GL_LIGHTING, GL_DEPTH_TEST,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
)
from OpenGL.GLU import gluOrtho2D

from furniture import FURNITURE_TYPES, SLOT_KEYS
import inventory
import inspect
from doors import hint_text
from lights import find_room, ROOMS


# ───────────────────────────────────────────────
# FONT VECTOR ĐƠN GIẢN ĐỂ VẼ CHỮ TRÊN MÀN HÌNH
# Không cần file .ttf, chạy ổn định 100% trên mọi máy
# ───────────────────────────────────────────────
# Mỗi ký tự định nghĩa danh sách các nét vẽ (x1, y1, x2, y2) trên lưới 4x6
STROKES = {
    'A': [(0,6,0,2), (0,2,2,0), (2,0,4,2), (4,2,4,6), (0,4,4,4)],
    'B': [(0,0,0,6), (0,0,3,0), (3,0,4,1), (4,1,3,3), (3,3,0,3), (0,3,3,3), (3,3,4,4), (4,4,3,6), (3,6,0,6)],
    'C': [(4,0,0,0), (0,0,0,6), (0,6,4,6)],
    'D': [(0,0,0,6), (0,0,3,0), (3,0,4,2), (4,2,4,4), (4,4,3,6), (3,6,0,6)],
    'E': [(4,0,0,0), (0,0,0,6), (0,6,4,6), (0,3,3,3)],
    'F': [(4,0,0,0), (0,0,0,6), (0,3,3,3)],
    'G': [(4,0,0,0), (0,0,0,6), (0,6,4,6), (4,6,4,3), (4,3,2,3)],
    'H': [(0,0,0,6), (4,0,4,6), (0,3,4,3)],
    'I': [(1,0,3,0), (2,0,2,6), (1,6,3,6)],
    'J': [(3,0,3,5), (3,5,2,6), (2,6,1,6), (1,6,0,5)],
    'K': [(0,0,0,6), (4,0,0,3), (0,3,4,6)],
    'L': [(0,0,0,6), (0,6,4,6)],
    'M': [(0,6,0,0), (0,0,2,3), (2,3,4,0), (4,0,4,6)],
    'N': [(0,6,0,0), (0,0,4,6), (4,6,4,0)],
    'O': [(0,0,4,0), (4,0,4,6), (4,6,0,6), (0,6,0,0)],
    'P': [(0,6,0,0), (0,0,4,0), (4,0,4,3), (4,3,0,3)],
    'Q': [(0,0,4,0), (4,0,4,5), (4,5,1,5), (0,5,0,0), (2,4,4,6)],
    'R': [(0,6,0,0), (0,0,4,0), (4,0,4,3), (4,3,0,3), (2,3,4,6)],
    'S': [(4,0,0,0), (0,0,0,3), (0,3,4,3), (4,3,4,6), (4,6,0,6)],
    'T': [(0,0,4,0), (2,0,2,6)],
    'U': [(0,0,0,6), (0,6,4,6), (4,6,4,0)],
    'V': [(0,0,2,6), (2,6,4,0)],
    'W': [(0,0,1,6), (1,6,2,3), (2,3,3,6), (3,6,4,0)],
    'X': [(0,0,4,6), (4,0,0,6)],
    'Y': [(0,0,2,3), (4,0,2,3), (2,3,2,6)],
    'Z': [(0,0,4,0), (4,0,0,6), (0,6,4,6)],
    '0': [(0,0,4,0), (4,0,4,6), (4,6,0,6), (0,6,0,0), (4,0,0,6)],
    '1': [(1,1,2,0), (2,0,2,6), (0,6,4,6)],
    '2': [(0,0,4,0), (4,0,4,3), (4,3,0,3), (0,3,0,6), (0,6,4,6)],
    '3': [(0,0,4,0), (4,0,4,3), (0,3,4,3), (4,3,4,6), (0,6,4,6)],
    '4': [(0,0,0,3), (0,3,4,3), (4,0,4,6)],
    '5': [(4,0,0,0), (0,0,0,3), (0,3,4,3), (4,3,4,6), (4,6,0,6)],
    '6': [(4,0,0,0), (0,0,0,6), (0,6,4,6), (4,6,4,3), (4,3,0,3)],
    '7': [(0,0,4,0), (4,0,1,6)],
    '8': [(0,0,4,0), (4,0,4,6), (4,6,0,6), (0,6,0,0), (0,3,4,3)],
    '9': [(0,3,4,3), (0,0,4,0), (4,0,4,6), (0,0,0,3), (0,6,4,6)],
    '[': [(2,0,0,0), (0,0,0,6), (0,6,2,6)],
    ']': [(0,0,2,0), (2,0,2,6), (2,6,0,6)],
    ':': [(2,2,2,2.5), (2,4.5,2,5)],
    '-': [(0,3,4,3)],
    '+': [(2,1,2,5), (0,3,4,3)],
    '/': [(0,6,4,0)],
    '|': [(2,0,2,6)],
    '.': [(1.5,5.5,2.5,5.5)],
    ' ': []
}


def draw_text_2d(x: float, y: float, text: str, scale: float = 2.0, r=1.0, g=1.0, b=1.0, a=1.0):
    """Vẽ một dòng chữ ASCII bằng các nét vector 2D."""
    glColor4f(r, g, b, a)
    glLineWidth(max(1.0, scale * 0.8))
    glBegin(GL_LINES)
    curr_x = x
    for ch in text.upper():
        strokes = STROKES.get(ch, STROKES[' '])
        for x1, y1, x2, y2 in strokes:
            glVertex2f(curr_x + x1 * scale, y + y1 * scale)
            glVertex2f(curr_x + x2 * scale, y + y2 * scale)
        curr_x += 5.5 * scale
    glEnd()


def draw_box_2d(x: float, y: float, w: float, h: float, r=0.0, g=0.0, b=0.0, a=0.6):
    """Vẽ hình chữ nhật 2D nền mờ."""
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def draw_border_2d(x: float, y: float, w: float, h: float, r=1.0, g=1.0, b=1.0, a=0.8, line_w=1.5):
    """Vẽ viền khung 2D."""
    glColor4f(r, g, b, a)
    glLineWidth(line_w)
    glBegin(GL_LINES)
    # Trên
    glVertex2f(x, y); glVertex2f(x + w, y)
    # Dưới
    glVertex2f(x, y + h); glVertex2f(x + w, y + h)
    # Trái
    glVertex2f(x, y); glVertex2f(x, y + h)
    # Phải
    glVertex2f(x + w, y); glVertex2f(x + w, y + h)
    glEnd()


def draw_crosshair(cx: int, cy: int):
    """Vẽ tâm ngắm chữ thập ở giữa màn hình."""
    size = 7
    glColor4f(1.0, 1.0, 1.0, 0.8)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(cx - size, cy)
    glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size)
    glVertex2f(cx, cy + size)
    glEnd()


# Tên ngắn gọn không dấu để vẽ font nét
NAME_MAP = {
    "table": "BAN",
    "chair": "GHE",
    "sofa": "SOFA",
    "bed": "GIUONG",
    "wardrobe": "TU AO",
    "shelf": "KE SACH",
    "fridge": "TU LANH",
    "tv": "KE TV",
    "lamp": "DEN BAN",
}


def draw_hotbar(width: int, height: int):
    """Vẽ thanh túi đồ Hotbar ở đáy màn hình."""
    if not inventory.inventory_open:
        return

    num_slots = len(SLOT_KEYS)
    slot_w = 70
    slot_h = 42
    spacing = 8
    total_w = num_slots * slot_w + (num_slots - 1) * spacing
    start_x = (width - total_w) // 2
    start_y = height - slot_h - 18

    # Vẽ nền thanh Hotbar
    draw_box_2d(start_x - 10, start_y - 8, total_w + 20, slot_h + 16, 0.08, 0.10, 0.14, 0.75)
    draw_border_2d(start_x - 10, start_y - 8, total_w + 20, slot_h + 16, 0.3, 0.4, 0.5, 0.6)

    for i, key in enumerate(SLOT_KEYS):
        sx = start_x + i * (slot_w + spacing)
        sy = start_y
        is_active = (inventory.active_slot == i)

        # Màu nền ô
        if is_active:
            draw_box_2d(sx, sy, slot_w, slot_h, 0.15, 0.45, 0.25, 0.9)
            draw_border_2d(sx, sy, slot_w, slot_h, 0.3, 1.0, 0.4, 1.0, line_w=2.5)
        else:
            draw_box_2d(sx, sy, slot_w, slot_h, 0.18, 0.20, 0.25, 0.75)
            draw_border_2d(sx, sy, slot_w, slot_h, 0.4, 0.45, 0.5, 0.5, line_w=1.0)

        # Số thứ tự [1..8]
        draw_text_2d(sx + 4, sy + 4, f"[{i+1}]", scale=1.3, r=1.0, g=0.9, b=0.2)

        # Tên món đồ
        short_name = NAME_MAP.get(key, key)
        draw_text_2d(sx + 4, sy + 22, short_name, scale=1.4, r=1.0, g=1.0, b=1.0)


def draw_hud(width: int, height: int, cam):
    """Hàm vẽ chính của HUD 2D."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    cx = width // 2
    cy = height // 2

    # 1. Tâm ngắm nếu không đang Inspect
    if not inspect.is_inspecting:
        draw_crosshair(cx, cy)

    # 2. Thông báo chế độ Inspect
    if inspect.is_inspecting:
        item_name = inspect.get_inspected_name().upper()
        # Khung thông báo giữa màn hình phía trên
        bar_w = 480
        bar_x = (width - bar_w) // 2
        draw_box_2d(bar_x, 40, bar_w, 48, 0.1, 0.12, 0.18, 0.85)
        draw_border_2d(bar_x, 40, bar_w, 48, 0.3, 0.7, 1.0, 0.9, line_w=2.0)
        draw_text_2d(bar_x + 18, 48, f"QUAN SAT 3D: {item_name}", scale=2.0, r=0.4, g=0.9, b=1.0)
        draw_text_2d(bar_x + 18, 70, "[RE CHUOT] XOAY 360  |  [V] DONG", scale=1.4, r=0.85, g=0.85, b=0.85)

    # 3. Gợi ý hành động khi đang chơi bình thường
    else:
        # Nếu đang cầm đồ trong tay để chuẩn bị đặt
        active_type = inventory.get_active_item_type()
        if active_type:
            name = NAME_MAP.get(active_type, active_type)
            rot = int(inventory.rotation_angle)
            can_place, reason = inventory.check_can_place(cam)

            bar_w = 600
            bar_x = (width - bar_w) // 2

            if can_place:
                draw_box_2d(bar_x, cy + 30, bar_w, 46, 0.08, 0.16, 0.10, 0.85)
                draw_border_2d(bar_x, cy + 30, bar_w, 46, 0.3, 0.95, 0.4, 0.95, line_w=2.0)
                draw_text_2d(bar_x + 16, cy + 36, f"DANG CAM: {name} (XOAY {rot} DEG) - HOP LE", scale=1.7, r=0.3, g=1.0, b=0.4)
                draw_text_2d(bar_x + 16, cy + 56, "[CHUOT TRAI] DAT XUONG | [SPACE] XOAY | [V] SOI 3D | [CHUOT PHAI] HUY", scale=1.3, r=1.0, g=1.0, b=1.0)
            else:
                draw_box_2d(bar_x, cy + 30, bar_w, 46, 0.20, 0.06, 0.06, 0.88)
                draw_border_2d(bar_x, cy + 30, bar_w, 46, 1.0, 0.25, 0.25, 1.0, line_w=2.2)
                reason_clean = reason.upper()
                draw_text_2d(bar_x + 16, cy + 36, f"CANH BAO: {reason_clean} (KHONG THE DAT)", scale=1.7, r=1.0, g=0.3, b=0.3)
                draw_text_2d(bar_x + 16, cy + 56, "[SPACE] XOAY HUONG KHAC | DI RA VI TRI TRONG | [CHUOT PHAI] HUY", scale=1.3, r=0.9, g=0.9, b=0.9)

        else:
            # Kiểm tra nhìn vào cửa
            d_hint = hint_text(cam)
            looked_item = inventory.find_looked_at_item(cam)

            if looked_item is not None:
                item_name = NAME_MAP.get(looked_item.item_type, looked_item.item_type)
                bar_w = 460
                bar_x = (width - bar_w) // 2
                draw_box_2d(bar_x, cy + 30, bar_w, 40, 0.10, 0.12, 0.16, 0.85)
                draw_border_2d(bar_x, cy + 30, bar_w, 40, 0.9, 0.8, 0.3, 0.9, line_w=1.8)
                draw_text_2d(bar_x + 16, cy + 36, f"{item_name}: [E] THU HOI VAO TUI", scale=1.6, r=1.0, g=0.9, b=0.3)
                draw_text_2d(bar_x + 16, cy + 54, "[V] CAM LEN SOI 3D", scale=1.3, r=0.8, g=0.9, b=1.0)

            elif d_hint is not None:
                text_clean = "MO CUA" if "Mở" in d_hint else "DONG CUA"
                bar_w = 220
                bar_x = (width - bar_w) // 2
                draw_box_2d(bar_x, cy + 30, bar_w, 36, 0.10, 0.12, 0.16, 0.85)
                draw_border_2d(bar_x, cy + 30, bar_w, 36, 0.3, 0.7, 1.0, 0.9, line_w=1.8)
                draw_text_2d(bar_x + 18, cy + 39, f"[E] {text_clean}", scale=1.8, r=0.3, g=0.9, b=1.0)

    # 4. Tên phòng người chơi đang đứng (góc trên bên trái)
    room_idx = find_room(cam)
    if room_idx is not None:
        r_name, _, _, _, _, floor = ROOMS[room_idx]
        floor_txt = "T1" if floor == 0 else "T2"
        # Bỏ dấu tiếng Việt để vẽ font vector sạch đẹp
        r_map = {
            "Phòng khách": "PHONG KHACH",
            "Phòng ăn": "PHONG AN",
            "Bếp": "BEP",
            "Sảnh tầng 2": "SANH TANG 2",
            "Phòng ngủ 1": "PHONG NGU 1",
            "Phòng ngủ 2": "PHONG NGU 2",
        }
        clean_rname = r_map.get(r_name, r_name.upper())
        draw_box_2d(16, 16, 250, 32, 0.08, 0.10, 0.14, 0.7)
        draw_border_2d(16, 16, 250, 32, 0.3, 0.5, 0.7, 0.6)
        draw_text_2d(26, 24, f"{clean_rname} - {floor_txt}", scale=1.6, r=0.9, g=0.95, b=1.0)

    # 5. Thanh túi đồ ở dưới
    draw_hotbar(width, height)

    # 6. Gợi ý phím tắt tổng quát ở góc trên bên phải
    info_w = 330
    info_x = width - info_w - 16
    draw_box_2d(info_x, 16, info_w, 52, 0.08, 0.10, 0.14, 0.6)
    draw_text_2d(info_x + 10, 22, "[WASD] DI LAI | [SHIFT] CHAY", scale=1.3, r=0.8, g=0.8, b=0.8)
    draw_text_2d(info_x + 10, 36, "[F] DEN PHONG | [Q] TUI DO (1-8)", scale=1.3, r=0.8, g=0.8, b=0.8)
    draw_text_2d(info_x + 10, 50, "[V] SOI 3D | [ESC] THOAT", scale=1.3, r=0.8, g=0.8, b=0.8)

    # Khôi phục trạng thái OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
