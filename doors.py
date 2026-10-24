"""
doors.py — Cửa mở/đóng quanh bản lề (phím E).
Trạng thái: CLOSED -> OPENING -> OPEN -> CLOSING -> CLOSED.
"""
import math
from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslatef, glRotatef, glColor3f

from shapes import draw_box_at
import collision
from house import HALF_D, UPPER_TOP, DOOR_W, DOOR_H, WALL_T

LEAF_T = 0.06          # độ dày cánh cửa (m)
OPEN_TIME = 0.5        # thời gian mở/đóng (giây)
INTERACT_DIST = 1.5    # đứng cách cửa tối đa bao xa thì bấm E được (m)

CLOSED, OPENING, OPEN, CLOSING = "CLOSED", "OPENING", "OPEN", "CLOSING"


class Door:
    def __init__(self, axis, fixed, center, base, hinge, swing):
        """
        axis='x': tường chạy dọc X, cửa nằm ở z=fixed, tâm cửa tại x=center.
        axis='z': tường chạy dọc Z, cửa nằm ở x=fixed, tâm cửa tại z=center.
        base : cao độ chân cửa (0 tầng trệt, 3.0 tầng 2).
        hinge: -1 hoặc +1 — bản lề ở đầu nhỏ hơn/lớn hơn của lỗ cửa (dọc theo tường).
        swing: -1 hoặc +1 — cánh cửa mở ra phía nào theo trục vuông góc với tường.
        """
        self.axis, self.fixed, self.center = axis, fixed, center
        self.base, self.hinge, self.swing = base, hinge, swing
        self.state = CLOSED
        self.t = 0.0                    # 0 = đóng hẳn, 1 = mở hết (90 độ)

        half, ht = DOOR_W / 2.0, WALL_T / 2.0
        if axis == 'x':
            self.cx, self.cz = center, fixed
            self.box = (center - half, center + half, base, base + DOOR_H, fixed - ht, fixed + ht)
        else:
            self.cx, self.cz = fixed, center
            self.box = (fixed - ht, fixed + ht, base, base + DOOR_H, center - half, center + half)
        # Cửa đóng thì chặn đường: đăng ký 1 hộp va chạm, bật/tắt theo trạng thái
        self.index = collision.add_box(*self.box)

    def player_in_zone(self, px, pz, feet_y):
        """Người chơi có đang đứng trong vùng cánh cửa quét qua (sát lỗ cửa) không?"""
        if abs(feet_y - self.base) > 1.0:
            return False
        x0, x1, _, _, z0, z1 = self.box
        r = collision.PLAYER_RADIUS + 0.05
        return x0 - r < px < x1 + r and z0 - r < pz < z1 + r

    def toggle(self, px, pz, feet_y):
        """Bấm E: đang đóng thì mở, đang mở thì đóng (trừ khi đang đứng trong lối cửa)."""
        if self.state in (CLOSED, CLOSING):
            self.state = OPENING
            collision.set_enabled(self.index, False)   # mở: cho đi qua
        else:
            if self.player_in_zone(px, pz, feet_y):
                return                                  # đang đứng trong cửa, không đóng
            self.state = CLOSING
            collision.set_enabled(self.index, True)     # đóng: chặn lại ngay

    def update(self, dt):
        speed = 1.0 / OPEN_TIME
        if self.state == OPENING:
            self.t += speed * dt
            if self.t >= 1.0:
                self.t, self.state = 1.0, OPEN
        elif self.state == CLOSING:
            self.t -= speed * dt
            if self.t <= 0.0:
                self.t, self.state = 0.0, CLOSED

    def draw(self):
        """
        Vẽ cánh cửa: tịnh tiến tới bản lề -> xoay quanh trục Y -> vẽ tấm cửa lệch khỏi bản lề.
        Góc xoay = t * 90 độ, dấu phụ thuộc phía bản lề và hướng mở.
        """
        half = DOOR_W / 2.0
        d = -self.hinge                       # cánh cửa nằm ở phía ngược với bản lề
        leaf_len = DOOR_W - 0.02              # hơi ngắn hơn lỗ để không dính khung
        glColor3f(0.45, 0.28, 0.15)           # nâu gỗ
        glPushMatrix()
        if self.axis == 'x':
            glTranslatef(self.center + self.hinge * half, self.base, self.fixed)   # tới bản lề
            glRotatef(self.t * 90.0 * self.swing * self.hinge, 0.0, 1.0, 0.0)      # xoay quanh trục Y
            draw_box_at(d * leaf_len / 2.0, DOOR_H / 2.0, 0.0, leaf_len, DOOR_H, LEAF_T)
        else:
            glTranslatef(self.fixed, self.base, self.center + self.hinge * half)
            glRotatef(-self.t * 90.0 * self.swing * self.hinge, 0.0, 1.0, 0.0)
            draw_box_at(0.0, DOOR_H / 2.0, d * leaf_len / 2.0, LEAF_T, DOOR_H, leaf_len)
        glPopMatrix()


DOORS = []


def build_doors():
    """Tạo các cửa của nhà. Gọi SAU build_house() (vì build_house xóa va chạm cũ)."""
    DOORS.clear()
    # Cửa chính (tường trước z=+5, tâm x=-3): bản lề bên trái, mở vào trong nhà (về phía -Z)
    DOORS.append(Door('x', HALF_D, -3.0, 0.0, -1, -1))
    # Hai cửa thông phòng trên tường x=1, ở cả tầng trệt lẫn tầng 2
    for base in (0.0, UPPER_TOP):
        DOORS.append(Door('z', 1.0, -2.5, base, -1, +1))   # mở sang phòng bên phải phía sau
        DOORS.append(Door('z', 1.0, 2.5, base, +1, +1))    # mở sang phòng bên phải phía trước


def update_doors(dt):
    for door in DOORS:
        door.update(dt)


def draw_doors():
    for door in DOORS:
        door.draw()


def find_target(cam):
    """Cửa gần nhất mà người chơi đang nhìn tới, cùng tầng, trong tầm INTERACT_DIST."""
    fx, _, fz = cam.front_vector()
    fl = math.hypot(fx, fz)
    if fl < 1e-6:
        return None
    best, best_dist = None, INTERACT_DIST
    for door in DOORS:
        if abs(cam.feet_y - door.base) > 1.0:          # khác tầng
            continue
        dx, dz = door.cx - cam.x, door.cz - cam.z
        dist = math.hypot(dx, dz)
        if dist > best_dist:
            continue
        # cos góc giữa hướng nhìn (nằm ngang) và hướng tới cửa phải > 0.5 (lệch dưới 60 độ)
        if dist > 0.4 and (dx * fx + dz * fz) / (dist * fl) < 0.5:
            continue
        best, best_dist = door, dist
    return best


def toggle_nearest_door(cam):
    door = find_target(cam)
    if door:
        door.toggle(cam.x, cam.z, cam.feet_y)


def hint_text(cam):
    """Chữ gợi ý khi nhìn vào cửa; None nếu không có cửa nào trong tầm."""
    door = find_target(cam)
    if door is None:
        return None
    return "[E] Đóng cửa" if door.state in (OPEN, OPENING) else "[E] Mở cửa"