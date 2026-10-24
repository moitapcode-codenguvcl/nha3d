"""
inspect.py — Chế độ Cầm đồ vật lên quan sát 3D (Inspect Mode).
Tính năng:
- Bấm phím V: Cầm đồ vật đang chọn (hoặc đồ vật đang nhìn tới) lên trước màn hình.
- Rê chuột qua lại: Xoay đồ vật 360 độ quanh mọi hướng để ngắm nghía chi tiết (kể cả bàn, ghế, sofa, giường...).
- Bấm V hoặc Chuột phải: Thoát chế độ quan sát, quay trở lại điều khiển bình thường.
"""

from OpenGL.GL import (
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef,
    glClear, GL_DEPTH_BUFFER_BIT, glEnable, glDisable,
    glMatrixMode, glLoadIdentity, GL_PROJECTION, GL_MODELVIEW
)
from OpenGL.GLU import gluPerspective, gluLookAt
from furniture import FURNITURE_TYPES

# Trạng thái quan sát
is_inspecting = False
inspected_type = None

# Góc xoay 3D của vật thể khi đưa chuột qua lại
rot_x = 20.0     # Nghiêng trên/dưới
rot_y = -35.0    # Xoay trái/phải


def start_inspect(item_type: str):
    """Bắt đầu cầm đồ vật lên trước mắt để quan sát."""
    global is_inspecting, inspected_type, rot_x, rot_y
    if item_type in FURNITURE_TYPES:
        is_inspecting = True
        inspected_type = item_type
        rot_x = 15.0
        rot_y = -30.0


def stop_inspect():
    """Thoát chế độ quan sát 3D."""
    global is_inspecting, inspected_type
    is_inspecting = False
    inspected_type = None


def toggle_inspect(current_item_type):
    """Bật/tắt chế độ quan sát khi ấn phím V."""
    global is_inspecting
    if is_inspecting:
        stop_inspect()
    else:
        if current_item_type:
            start_inspect(current_item_type)


def on_mouse_inspect(dx, dy):
    """Khi rê chuột trong chế độ Inspect, xoay vật thể 3D."""
    global rot_x, rot_y
    rot_y += dx * 0.4
    rot_x += dy * 0.4
    # Giới hạn góc nghiêng để không bị lật ngược
    rot_x = max(-85.0, min(85.0, rot_x))


def get_inspected_name():
    """Tên tiếng Việt của vật thể đang quan sát."""
    if is_inspecting and inspected_type in FURNITURE_TYPES:
        return FURNITURE_TYPES[inspected_type]["name"]
    return ""


def render_inspected_object(window_width, window_height):
    """
    Vẽ vật thể lơ lửng giữa màn hình ở cự ly gần để người dùng ngắm nghía.
    Xóa bộ đệm độ sâu để vật thể luôn hiển thị rõ ràng trên cùng.
    """
    if not is_inspecting or inspected_type is None:
        return

    # Xóa depth buffer riêng để vật thể cầm trên tay không bị tường xung quanh che
    glClear(GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    aspect = window_width / window_height if window_height > 0 else 1.0
    gluPerspective(45.0, aspect, 0.05, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Đặt camera nhìn vào vật thể cách 2.2m
    gluLookAt(0.0, 0.0, 2.2,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

    # Xoay vật thể theo chuột của người dùng
    glRotatef(rot_x, 1.0, 0.0, 0.0)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    # Tịnh tiến để tâm hình học của vật thể nằm đúng ở gốc tọa độ
    size = FURNITURE_TYPES[inspected_type]["size"]
    h = size[1]
    glTranslatef(0.0, -h / 2.0, 0.0)

    # Vẽ vật thể
    draw_fn = FURNITURE_TYPES[inspected_type]["draw"]
    draw_fn(preview=False)

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
