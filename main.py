"""
main.py — Cửa sổ GLFW, vòng lặp chính, xử lý input, hệ thống Đặt đồ và Quan sát 3D.
"""

import sys
import glfw
from OpenGL.GL import (
    glClearColor, glClear, glEnable, glDisable,
    glMatrixMode, glLoadIdentity, glViewport,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST, glBegin, glEnd, glNormal3f, glVertex3f,
    glColor3f, GL_QUADS, GL_PROJECTION, GL_MODELVIEW
)
from OpenGL.GLU import gluPerspective

from camera import Camera
from house import draw_house, build_house, draw_windows
from doors import build_doors, update_doors, draw_doors, toggle_nearest_door
from lights import setup_all_lights, apply_lights, toggle_room_light, draw_bulbs
from furniture import setup_default_house_furniture, draw_all_placed_items
import inventory
import inspect
import hud

camera = Camera(-3.0, 12.0)

# ───────────────────────────────────────────────
# HẰNG SỐ & BIẾN CỬA SỔ
# ───────────────────────────────────────────────
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE  = "Nhà 3D — Tham quan, Đặt đồ & Quan sát 3D"

cur_width = WINDOW_WIDTH
cur_height = WINDOW_HEIGHT


# ───────────────────────────────────────────────
# THIẾT LẬP CAMERA (PROJECTION)
# ───────────────────────────────────────────────
def setup_projection(width: int, height: int) -> None:
    """Thiết lập ma trận phối cảnh (perspective projection)."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = width / height if height > 0 else 1.0
    gluPerspective(60.0, aspect, 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)


# ───────────────────────────────────────────────
# CALLBACKS GLFW
# ───────────────────────────────────────────────
def on_resize(window, width: int, height: int) -> None:
    """Cập nhật viewport và ma trận chiếu khi đổi kích thước cửa sổ."""
    global cur_width, cur_height
    if height == 0:
        height = 1
    cur_width, cur_height = width, height
    glViewport(0, 0, width, height)
    setup_projection(width, height)


_last_raw_mx = None
_last_raw_my = None

def on_mouse_move(window, xpos, ypos):
    """Xử lý chuột: Nếu đang Inspect thì xoay vật thể 3D; nếu không thì xoay camera."""
    global _last_raw_mx, _last_raw_my
    if _last_raw_mx is None:
        _last_raw_mx, _last_raw_my = xpos, ypos
    dx = xpos - _last_raw_mx
    dy = ypos - _last_raw_my
    _last_raw_mx, _last_raw_my = xpos, ypos

    if inspect.is_inspecting:
        inspect.on_mouse_inspect(dx, dy)
    else:
        camera.on_mouse(xpos, ypos)


def on_mouse_button(window, button, action, mods):
    """Xử lý nhấp chuột trái / phải."""
    if action == glfw.PRESS:
        if button == glfw.MOUSE_BUTTON_LEFT:
            if inspect.is_inspecting:
                inspect.stop_inspect()
            else:
                # Nếu đang cầm đồ trong tay: Đặt đồ xuống sàn
                if inventory.get_active_item_type():
                    inventory.try_place_item(camera)
                else:
                    # Nếu đang nhìn vào đồ vật trên sàn: thu hồi vào túi
                    looked = inventory.find_looked_at_item(camera)
                    if looked:
                        inventory.pickup_item(camera)
                    else:
                        toggle_nearest_door(camera)

        elif button == glfw.MOUSE_BUTTON_RIGHT:
            if inspect.is_inspecting:
                inspect.stop_inspect()
            else:
                # Chuột phải để bỏ chọn đồ vật đang cầm
                if inventory.active_slot is not None:
                    inventory.active_slot = None


def on_key(window, key, scancode, action, mods) -> None:
    """Xử lý phím bấm."""
    if action == glfw.PRESS:
        # ESC: Thoát chế độ inspect hoặc thoát chương trình
        if key == glfw.KEY_ESCAPE:
            if inspect.is_inspecting:
                inspect.stop_inspect()
            else:
                glfw.set_window_should_close(window, True)

        # Phím F: Bật/tắt đèn phòng hiện tại (theo đúng ý muốn của bạn)
        elif key == glfw.KEY_F:
            toggle_room_light(camera)

        # Phím Q: Bật/tắt menu túi đồ
        elif key == glfw.KEY_Q:
            inventory.toggle_inventory()

        # Phím Space: Xoay hướng đồ vật theo chiều kim đồng hồ (+90 độ)
        elif key == glfw.KEY_SPACE:
            if inventory.get_active_item_type():
                inventory.rotate_placement()

        # Phím E: Tương tác thế giới (Thu hồi đồ vật đang nhìn / Mở đóng cửa)
        elif key == glfw.KEY_E:
            looked = inventory.find_looked_at_item(camera)
            if looked:
                inventory.pickup_item(camera)
            else:
                toggle_nearest_door(camera)

        # Phím V: Cầm đồ vật lên trước mắt để xoay chuột quan sát 3D 360 độ
        elif key == glfw.KEY_V:
            if inspect.is_inspecting:
                inspect.stop_inspect()
            else:
                item_type = inventory.get_active_item_type()
                if not item_type:
                    looked = inventory.find_looked_at_item(camera)
                    if looked:
                        item_type = looked.item_type
                    else:
                        item_type = "table"
                inspect.start_inspect(item_type)

        # Các phím số 1..9: Chọn đồ vật trong túi đồ
        elif glfw.KEY_1 <= key <= glfw.KEY_9:
            slot_idx = key - glfw.KEY_1
            inventory.select_slot(slot_idx)


# ───────────────────────────────────────────────
# VẼ SÀN & KHUNG HÌNH (Render Frame)
# ───────────────────────────────────────────────
def draw_floor(size: int = 40) -> None:
    """Sàn cỏ/đất caro xung quanh nhà."""
    half = size // 2
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    for i in range(-half, half):
        for j in range(-half, half):
            if (i + j) % 2 == 0:
                glColor3f(0.42, 0.58, 0.35)  # Xanh cỏ sáng
            else:
                glColor3f(0.35, 0.48, 0.28)  # Xanh cỏ sẫm
            glVertex3f(i, 0.0, j)
            glVertex3f(i + 1, 0.0, j)
            glVertex3f(i + 1, 0.0, j + 1)
            glVertex3f(i, 0.0, j + 1)
    glEnd()


def render_frame(window, delta_time: float) -> None:
    """Vẽ một khung hình."""
    # ── Xóa màn hình (bầu trời xanh dịu nhẹ + depth buffer) ──
    glClearColor(0.55, 0.78, 0.90, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # ── Reset ma trận mô hình ──
    glLoadIdentity()

    # ── Cập nhật camera (nếu không đang Inspect) ──
    if not inspect.is_inspecting:
        camera.update(window, delta_time)
    camera.apply()

    # Đặt đèn sau camera để đèn cố định trong thế giới
    apply_lights()

    update_doors(delta_time)

    # 1. Vẽ cảnh quan thế giới 3D
    draw_floor(44)
    draw_house()
    draw_windows()
    draw_doors()
    draw_bulbs()
    draw_all_placed_items()

    # 2. Vẽ hình chiếu xem trước vị trí đặt đồ (Ghost preview) nếu đang cầm đồ
    if not inspect.is_inspecting:
        inventory.draw_placement_preview(camera)

    # 3. Vẽ vật thể cầm lên quan sát 3D (Inspect mode) nếu đang bật
    if inspect.is_inspecting:
        inspect.render_inspected_object(cur_width, cur_height)

    # 4. Vẽ toàn bộ giao diện 2D HUD (tâm ngắm, túi đồ, phím gợi ý, tên phòng)
    hud.draw_hud(cur_width, cur_height, camera)


# ───────────────────────────────────────────────
# HÀM CHÍNH (Main)
# ───────────────────────────────────────────────
def main() -> None:
    global cur_width, cur_height

    # ── Khởi tạo GLFW ──
    if not glfw.init():
        print("[LỖI] Không thể khởi tạo GLFW!")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
    if not window:
        print("[LỖI] Không thể tạo cửa sổ GLFW!")
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    # ── Đăng ký callbacks ──
    glfw.set_framebuffer_size_callback(window, on_resize)
    glfw.set_key_callback(window, on_key)
    glfw.set_cursor_pos_callback(window, on_mouse_move)
    glfw.set_mouse_button_callback(window, on_mouse_button)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # ── Khởi tạo OpenGL ──
    glEnable(GL_DEPTH_TEST)
    setup_projection(WINDOW_WIDTH, WINDOW_HEIGHT)
    setup_all_lights()
    build_house()
    build_doors()
    setup_default_house_furniture()

    print("=" * 60)
    print(f"  {WINDOW_TITLE}")
    print("  [WASD] Di chuyển | [Shift] Chạy nhanh")
    print("  [F] Bật/tắt đèn phòng")
    print("  [Q] Mở/đóng túi đồ | Phím [1..8] Chọn đồ vật")
    print("  [Space] Xoay chiều đồ vật theo chiều kim đồng hồ")
    print("  [Chuột Trái / E] Đặt đồ vật xuống sàn / Thu hồi / Mở cửa")
    print("  [V] Cầm đồ vật lên quan sát 3D (rê chuột xoay 360 độ)")
    print("  [ESC] Thoát")
    print("=" * 60)

    last_time: float = glfw.get_time()

    while not glfw.window_should_close(window):
        current_time: float = glfw.get_time()
        delta_time: float = current_time - last_time
        last_time = current_time

        if delta_time > 0.1:
            delta_time = 0.1

        glfw.poll_events()
        render_frame(window, delta_time)
        glfw.swap_buffers(window)

    glfw.destroy_window(window)
    glfw.terminate()
    print("Đã thoát chương trình. Tạm biệt!")


if __name__ == "__main__":
    main()
