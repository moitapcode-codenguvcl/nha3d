"""
inventory.py — Quản lý Túi đồ, chọn món đồ (phím Q, số 1..8) và Hệ thống Đặt đồ vật (Building/Placement).
Tính năng:
- Bấm Q: Bật/tắt thanh túi đồ.
- Bấm 1..8: Chọn đồ vật để cầm trên tay.
- Bấm Space: Xoay hướng đồ vật theo chiều kim đồng hồ (+90 độ).
- Xem trước hình chiếu (Ghost/Preview) trên sàn nhà trước mặt:
  + Màu XANH LÁ: Hợp lệ, có thể đặt.
  + Màu ĐỎ: Vướng vật cản (trùng đồ khác, xuyên tường, chắn cửa, chắn cầu thang) -> Không cho đặt.
- Bấm Chuột Trái: Đặt đồ vật cố định vào nhà (chỉ khi hợp lệ).
- Bấm Chuột Phải: Bỏ chọn đồ đang cầm (cất vào túi).
"""

import math
from OpenGL.GL import (
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef,
    glEnable, glDisable, GL_BLEND
)
import furniture
from furniture import FURNITURE_TYPES, SLOT_KEYS, add_placed_item, remove_placed_item, PLACED_ITEMS

# Trạng thái túi đồ
inventory_open = True
active_slot = None
rotation_angle = 0.0


def toggle_inventory():
    """Phím Q: Bật/tắt hiển thị túi đồ."""
    global inventory_open
    inventory_open = not inventory_open


def select_slot(slot_idx: int):
    """Chọn slot bằng phím 1..8. Nếu bấm lại slot đang chọn thì bỏ chọn."""
    global active_slot, rotation_angle
    if 0 <= slot_idx < len(SLOT_KEYS):
        if active_slot == slot_idx:
            active_slot = None
        else:
            active_slot = slot_idx
            rotation_angle = 0.0


def rotate_placement():
    """Phím Space: Xoay vật thể 90 độ theo chiều kim đồng hồ quanh trục Y."""
    global rotation_angle
    if active_slot is not None:
        rotation_angle = (rotation_angle + 90.0) % 360.0


def get_active_item_type():
    """Lấy mã loại đồ vật đang cầm trên tay."""
    if active_slot is not None and 0 <= active_slot < len(SLOT_KEYS):
        return SLOT_KEYS[active_slot]
    return None


def calculate_placement_pos(cam):
    """
    Tính vị trí đặt đồ vật trên sàn phía trước người chơi (khoảng 2.0 - 2.5m).
    Xác định sàn tầng trệt (y=0.1) hoặc sàn tầng 2 (y=3.0).
    """
    yaw_rad = math.radians(cam.yaw)
    fx = math.cos(yaw_rad)
    fz = math.sin(yaw_rad)

    dist = 2.2
    place_x = cam.x + fx * dist
    place_z = cam.z + fz * dist

    place_y = 3.0 if cam.feet_y >= 2.0 else 0.1

    # Giới hạn trong khuôn viên nhà
    place_x = max(-6.2, min(6.2, place_x))
    place_z = max(-4.2, min(4.2, place_z))

    return place_x, place_y, place_z


def get_candidate_aabb(item_type: str, px: float, py: float, pz: float, rot: float):
    """Tính toán hộp va chạm AABB của vật thể chuẩn bị đặt."""
    w, h, d = FURNITURE_TYPES[item_type]["size"]
    rad = math.radians(rot)
    cos_a = abs(math.cos(rad))
    sin_a = abs(math.sin(rad))
    box_w = w * cos_a + d * sin_a
    box_d = w * sin_a + d * cos_a

    half_w = box_w / 2.0
    half_d = box_d / 2.0
    return (px - half_w, px + half_w, py, py + h, pz - half_d, pz + half_d)


def check_can_place(cam):
    """
    Kiểm tra toàn diện xem vị trí hiện tại có hợp lệ để đặt đồ vật không:
    - Không đè lên đồ vật khác.
    - Không đè lên người chơi.
    - Không xuyên qua tường ngoài hoặc tường ngăn.
    - Không chắn cửa ra vào.
    - Không rơi vào lỗ cầu thang hoặc chắn lối lên cầu thang tầng 2.
    """
    item_type = get_active_item_type()
    if item_type is None:
        return False, "Chưa chọn đồ"

    px, py, pz = calculate_placement_pos(cam)
    bx0, bx1, by0, by1, bz0, bz1 = get_candidate_aabb(item_type, px, py, pz, rotation_angle)

    # 1. Kiểm tra đè lên đồ vật khác (cùng tầng)
    for placed in PLACED_ITEMS:
        if abs(placed.y - py) > 0.5:
            continue
        ox0, ox1, oy0, oy1, oz0, oz1 = placed.get_aabb()
        # Nếu giao cắt theo cả trục X và Z -> Trùng đè!
        if not (bx1 <= ox0 or bx0 >= ox1 or bz1 <= oz0 or bz0 >= oz1):
            return False, "Trùng đè đồ vật khác"

    # 2. Kiểm tra trùng người chơi
    pr = 0.40
    if (bx0 - pr < cam.x < bx1 + pr and bz0 - pr < cam.z < bz1 + pr and abs(cam.feet_y - py) < 1.0):
        return False, "Trùng vị trí người chơi"

    # 3. Kiểm tra tường ngoài
    if bx0 < -6.8 or bx1 > 6.8 or bz0 < -4.8 or bz1 > 4.8:
        return False, "Xuyên tường ngoài"

    # 4. Kiểm tra tường ngăn trung tâm (x = 1.0)
    if bx0 < 1.08 and bx1 > 0.92:
        return False, "Xuyên tường ngăn giữa"

    # 5. Kiểm tra tường ngăn phòng bên phải (z = 0.0 từ x = 1.0 đến 6.8)
    if bx1 > 0.92 and bz0 < 0.08 and bz1 > -0.08:
        return False, "Xuyên tường ngăn phòng"

    # 6. Kiểm tra chắn cửa ra vào
    door_positions = [
        (-3.0, 5.0),   # Cửa chính
        (1.0, -2.5),   # Cửa phòng 1
        (1.0, 2.5),    # Cửa phòng 2
    ]
    for dx, dz in door_positions:
        dist_to_door = math.hypot(px - dx, pz - dz)
        if dist_to_door < 1.25:
            return False, "Chắn cửa ra vào"

    # 7. Kiểm tra lỗ cầu thang và lối lên cầu thang ở tầng 2
    if py >= 2.0:
        # Lỗ cầu thang: x từ -6.9 đến -2.0, z từ -4.9 đến -3.7
        if not (bx1 <= -6.9 or bx0 >= -1.95 or bz1 <= -4.9 or bz0 >= -3.65):
            return False, "Rơi vào lỗ cầu thang"
        # Lối bước từ cầu thang ra sàn tầng 2: x từ -6.9 đến -5.2, z từ -3.7 đến -2.6
        if not (bx1 <= -6.9 or bx0 >= -5.2 or bz1 <= -3.7 or bz0 >= -2.6):
            return False, "Chắn lối lên cầu thang"

    return True, "Hợp lệ"


def try_place_item(cam):
    """Đặt đồ vật đang cầm xuống sàn tại vị trí ngắm (nếu vị trí hợp lệ)."""
    item_type = get_active_item_type()
    if item_type is None:
        return False

    can_place, reason = check_can_place(cam)
    if not can_place:
        print(f"[CẢNH BÁO] Không thể đặt: {reason}")
        return False

    px, py, pz = calculate_placement_pos(cam)
    add_placed_item(item_type, px, py, pz, rot=rotation_angle, register_collision=True)
    return True


def draw_placement_preview(cam):
    """Vẽ bóng mờ (preview) của đồ vật: Xanh lá nếu đặt được, Đỏ nếu vướng."""
    item_type = get_active_item_type()
    if item_type is None:
        return

    can_place, _ = check_can_place(cam)
    furniture.preview_valid = can_place

    px, py, pz = calculate_placement_pos(cam)
    draw_fn = FURNITURE_TYPES[item_type]["draw"]

    glEnable(GL_BLEND)
    glPushMatrix()
    glTranslatef(px, py, pz)
    glRotatef(rotation_angle, 0.0, 1.0, 0.0)
    draw_fn(preview=True)
    glPopMatrix()
    glDisable(GL_BLEND)


def find_looked_at_item(cam, max_dist=2.5):
    """Tìm đồ vật đã đặt mà người chơi đang nhìn vào ở cự ly gần (< max_dist)."""
    fx, fy, fz = cam.front_vector()
    best_item = None
    best_dist = max_dist

    for item in PLACED_ITEMS:
        dx = item.x - cam.x
        dy = (item.y + item.info["size"][1] / 2.0) - cam.y
        dz = item.z - cam.z
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist < best_dist:
            dot = (dx * fx + dy * fy + dz * fz) / dist
            if dot > 0.85:
                best_item = item
                best_dist = dist

    return best_item


def pickup_item(cam):
    """Thu hồi đồ vật đang nhìn vào trên sàn."""
    item = find_looked_at_item(cam)
    if item:
        remove_placed_item(item)
        return item
    return None
