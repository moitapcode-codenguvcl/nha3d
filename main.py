"""
main.py — Cửa sổ GLFW, vòng lặp chính, xử lý input.
Bước 0: Kiểm tra bằng hình hộp xoay chậm giữa màn hình.
"""

import sys
import glfw
# import numpy as np

from OpenGL.GL import (
    glClearColor, glClear, glEnable, glDisable,
    glMatrixMode, glLoadIdentity, glViewport,
    glTranslatef, glRotatef,
    glPushMatrix, glPopMatrix,
    glLightfv, glColorMaterial, glColor3f,
    glMaterialfv, glShadeModel,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST, GL_LIGHTING, GL_LIGHT0,
    GL_AMBIENT, GL_DIFFUSE, GL_SPECULAR, GL_POSITION,
    GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE,
    GL_COLOR_MATERIAL, GL_SMOOTH,
    GL_PROJECTION, GL_MODELVIEW,
)
from OpenGL.GLU import gluPerspective

from shapes import draw_box
from camera import Camera
from house import draw_house, build_house
from doors import build_doors, update_doors, draw_doors, toggle_nearest_door, hint_text
from lights import setup_all_lights, apply_lights, toggle_room_light, draw_bulbs
from OpenGL.GL import glBegin, glEnd, glNormal3f, glVertex3f, GL_QUADS

camera = Camera(-3.0, 12.0)
# ───────────────────────────────────────────────
# HẰNG SỐ CỬA SỔ
# ───────────────────────────────────────────────
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE  = "Nhà 3D — Đồ án Đồ họa Máy tính"

# Góc xoay hiện tại của hộp thử nghiệm (độ)
rotation_angle: float = 0.0

# ───────────────────────────────────────────────
# THIẾT LẬP CAMERA (PROJECTION)
# ───────────────────────────────────────────────

def setup_projection(width: int, height: int) -> None:
    """
    Thiết lập ma trận phối cảnh (perspective projection).
    FOV = 60°, tỉ lệ khung = width/height, near = 0.1m, far = 500m.
    """
    glMatrixMode(GL_PROJECTION)  # Chuyển sang ma trận chiếu
    glLoadIdentity()             # Reset về đơn vị
    aspect = width / height if height > 0 else 1.0
    # gluPerspective: fovy (độ), aspect, zNear, zFar
    gluPerspective(60.0, aspect, 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)   # Trở lại ma trận mô hình — mặc định vẽ ở đây


# ───────────────────────────────────────────────
# CALLBACK: thay đổi kích thước cửa sổ
# ───────────────────────────────────────────────

def on_resize(window, width: int, height: int) -> None:
    """Cập nhật viewport và ma trận chiếu khi người dùng thay đổi cửa sổ."""
    if height == 0:
        height = 1  # Tránh chia cho 0
    glViewport(0, 0, width, height)
    setup_projection(width, height)


# ───────────────────────────────────────────────
# CALLBACK: phím bấm
# ───────────────────────────────────────────────

def on_key(window, key, scancode, action, mods) -> None:
    """Xử lý phím bấm toàn cục. ESC để thoát."""
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_E and action == glfw.PRESS:
        toggle_nearest_door(camera) 
        
    if key == glfw.KEY_F and action == glfw.PRESS: toggle_room_light(camera)   # mở/đóng đèn phòng đang nhìn tới
    # # TẠM THỜI (sẽ xóa ở Bước 3): phím 1 / 2 để nhảy giữa tầng trệt và tầng 2 xem thử
    # if action == glfw.PRESS:
    #     if key == glfw.KEY_1:
    #         camera.y = 1.7      # tầng trệt: mắt cao 1.7 m
    #     elif key == glfw.KEY_2:
    #         camera.y = 4.7      # tầng 2: sàn ở y=3.0 nên mắt ở 3.0 + 1.7
# ───────────────────────────────────────────────
# VẼ KHUNG HÌNH (Frame)
# ───────────────────────────────────────────────

_last_title = ""

def update_hint(window) -> None:
    """Hiện gợi ý '[E] Mở cửa' trên thanh tiêu đề khi đang nhìn vào cửa."""
    global _last_title
    text = hint_text(camera)
    title = WINDOW_TITLE if not text else f"{WINDOW_TITLE}   —   {text}"
    if title != _last_title:          # chỉ đổi khi chữ thay đổi, tránh gọi mỗi khung hình
        glfw.set_window_title(window, title)
        _last_title = title

def render_frame(window, delta_time: float) -> None:
    """
    Vẽ một khung hình. Được gọi mỗi vòng lặp.
    delta_time: thời gian (giây) kể từ khung hình trước.
    """
    # ── Xóa màn hình (màu xanh trời + bộ đệm độ sâu) ──
    glClearColor(0.53, 0.81, 0.92, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # ── Reset ma trận mô hình ──
    glLoadIdentity()

    # ── Cập nhật và đặt camera TRƯỚC khi vẽ mọi thứ ──
    camera.update(window, delta_time)
    camera.apply()

    # Đặt vị trí đèn SAU camera để đèn đứng yên trong thế giới
    apply_lights()

    update_doors(delta_time)   # cập nhật góc xoay các cánh cửa
    update_hint(window)        # gợi ý [E] trên thanh tiêu đề

    draw_floor(40)
    draw_house()
    draw_doors()
    draw_bulbs()

def draw_floor(size: int = 30) -> None:
    """Sàn caro size x size mét, mỗi ô 1m, xen kẽ hai màu."""
    half = size // 2
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    for i in range(-half, half):
        for j in range(-half, half):
            if (i + j) % 2 == 0:
                glColor3f(0.75, 0.75, 0.75)
            else:
                glColor3f(0.35, 0.35, 0.35)
            glVertex3f(i, 0.0, j)
            glVertex3f(i + 1, 0.0, j)
            glVertex3f(i + 1, 0.0, j + 1)
            glVertex3f(i, 0.0, j + 1)
    glEnd()

# ───────────────────────────────────────────────
# HÀM CHÍNH
# ───────────────────────────────────────────────

def main() -> None:
    """Khởi tạo GLFW, tạo cửa sổ, chạy vòng lặp chính."""

    # ── Khởi tạo GLFW ──
    if not glfw.init():
        print("[LỖI] Không thể khởi tạo GLFW!")
        sys.exit(1)

    # Yêu cầu OpenGL cổ điển (compatibility profile)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    # ── Tạo cửa sổ ──
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
    if not window:
        print("[LỖI] Không thể tạo cửa sổ GLFW!")
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)

    # Đồng bộ với VSync (giới hạn 60 FPS)
    glfw.swap_interval(1)

    # ── Đăng ký callbacks ──
    glfw.set_framebuffer_size_callback(window, on_resize)
    glfw.set_key_callback(window, on_key)
    glfw.set_cursor_pos_callback(window, lambda w, x, y: camera.on_mouse(x, y))
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)  # ẩn và khóa chuột
    # ── Khởi tạo OpenGL ──
    glEnable(GL_DEPTH_TEST)  # Bật kiểm tra độ sâu — vật gần che vật xa
    setup_projection(WINDOW_WIDTH, WINDOW_HEIGHT)
    setup_all_lights()
    build_house()
    build_doors()   # tạo 5 cánh cửa + đăng ký va chạm (phải gọi SAU build_house)

    print("=" * 50)
    print(f"  {WINDOW_TITLE}")
    print("  Bước 0: Hình hộp xoay thử nghiệm")
    print("  [ESC] Thoát")
    print("=" * 50)

    # ── Vòng lặp chính ──
    last_time: float = glfw.get_time()

    while not glfw.window_should_close(window):
        # Tính delta time — thời gian giữa 2 khung hình liên tiếp
        current_time: float = glfw.get_time()
        delta_time: float   = current_time - last_time
        last_time           = current_time

        # Giới hạn delta_time để tránh "time jump" khi cửa sổ bị kéo/dừng
        if delta_time > 0.1:
            delta_time = 0.1

        # Xử lý sự kiện (bàn phím, chuột, resize,...)
        glfw.poll_events()

        # Vẽ khung hình
        render_frame(window, delta_time)

        # Hoán đổi buffer (double buffering — tránh nhấp nháy)
        glfw.swap_buffers(window)

    # ── Dọn dẹp ──
    glfw.destroy_window(window)
    glfw.terminate()
    print("Đã thoát. Tạm biệt!")


if __name__ == "__main__":
    main()
