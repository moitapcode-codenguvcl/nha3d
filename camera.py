"""camera.py — Camera góc nhìn thứ nhất (WASD, chuột), có va chạm và đi cầu thang."""
import math
import glfw
from OpenGL.GLU import gluLookAt

import collision

EYE_HEIGHT = 1.7      # mắt cao hơn chân bao nhiêu (m)
WALK_SPEED = 3.0      # m/s
RUN_SPEED = 6.0       # m/s khi giữ Shift
MOUSE_SENS = 0.1      # độ xoay mỗi pixel chuột


class Camera:
    def __init__(self, x=0.0, z=5.0):
        self.x, self.z = x, z
        self.feet_y = 0.0                 # độ cao CHÂN (logic va chạm)
        self.y = self.feet_y + EYE_HEIGHT # độ cao MẮT (đã làm mượt để vẽ)
        self.yaw = -90.0   # xoay ngang (độ). -90 = nhìn về hướng -Z
        self.pitch = 0.0   # xoay dọc (độ)
        self._last_mx = None
        self._last_my = None

    def on_mouse(self, xpos, ypos):
        """Chuột di chuyển -> đổi yaw/pitch."""
        if self._last_mx is None:
            self._last_mx, self._last_my = xpos, ypos
        dx = xpos - self._last_mx
        dy = self._last_my - ypos          # chuột đi lên -> nhìn lên
        self._last_mx, self._last_my = xpos, ypos
        self.yaw += dx * MOUSE_SENS
        self.pitch += dy * MOUSE_SENS
        self.pitch = max(-89.0, min(89.0, self.pitch))   # không cho lộn ngược

    def front_vector(self):
        """Hướng nhìn từ yaw/pitch (tọa độ cầu -> vector đơn vị)."""
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        return (math.cos(pitch) * math.cos(yaw),
                math.sin(pitch),
                math.cos(pitch) * math.sin(yaw))

    def update(self, window, dt):
        """Đọc WASD, di chuyển có va chạm, rồi cập nhật độ cao chân/mắt."""
        speed = RUN_SPEED if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS else WALK_SPEED
        yaw = math.radians(self.yaw)
        fx, fz = math.cos(yaw), math.sin(yaw)   # hướng tiến (bỏ thành phần Y)
        rx, rz = -fz, fx                         # hướng phải (vuông góc hướng tiến)

        mx = mz = 0.0
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS: mx += fx; mz += fz
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS: mx -= fx; mz -= fz
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS: mx += rx; mz += rz
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS: mx -= rx; mz -= rz

        length = math.hypot(mx, mz)
        if length > 0:                 # chuẩn hóa để đi chéo không nhanh hơn
            dx = mx / length * speed * dt
            dz = mz / length * speed * dt
            self.x, self.z, self.feet_y = collision.move(self.x, self.z, dx, dz, self.feet_y)

        # Chân bám theo mặt sàn/bậc thang (đứng yên cũng cần, vì có thể đang rơi)
        self.feet_y = collision.settle(self.x, self.z, self.feet_y, dt)

        # Mắt đi theo chân, làm mượt để lên/xuống bậc không bị giật
        target_y = self.feet_y + EYE_HEIGHT
        self.y += (target_y - self.y) * min(1.0, 12.0 * dt)

    def apply(self):
        """Đặt camera: gluLookAt(vị trí mắt, điểm nhìn tới, hướng 'lên')."""
        dx, dy, dz = self.front_vector()
        gluLookAt(self.x, self.y, self.z,
                  self.x + dx, self.y + dy, self.z + dz,
                  0.0, 1.0, 0.0)