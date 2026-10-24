"""
collision.py — Va chạm AABB (hộp song song trục) và chiều cao mặt đi được.
Mỗi hộp là (x0, x1, y0, y1, z0, z1). Người chơi là một "cột" bán kính PLAYER_RADIUS.
Hộp có thể bật/tắt (dùng cho cửa: đóng = bật, mở = tắt).
"""
import math

PLAYER_RADIUS = 0.25   # bán kính người chơi (m)
PLAYER_HEIGHT = 1.8    # chiều cao người chơi (m), tính từ chân
STEP_MAX = 0.35        # bước lên được tối đa 0.35 m (bậc thang cao 0.21 m)
FALL_SPEED = 10.0      # tốc độ rơi (m/s) khi bước hụt xuống chỗ thấp hơn
MAX_SUBSTEP = 0.05     # mỗi lần di chuyển tối đa 5 cm, để không xuyên tường khi chạy nhanh

_boxes = []            # danh sách tất cả hộp va chạm
_enabled = []          # _enabled[i] = hộp i đang có hiệu lực hay không


def clear():
    _boxes.clear()
    _enabled.clear()


def add_box(x0, x1, y0, y1, z0, z1):
    """Thêm hộp va chạm, trả về chỉ số của hộp để bật/tắt sau này."""
    _boxes.append((x0, x1, y0, y1, z0, z1))
    _enabled.append(True)
    return len(_boxes) - 1


def set_enabled(index, enabled):
    """Bật/tắt hộp số index (cửa mở thì tắt hộp của cửa)."""
    _enabled[index] = enabled


def is_blocked(x, z, feet_y):
    """
    True nếu đứng ở (x, z) với chân ở độ cao feet_y thì đụng vật cản.
    Chỉ tính hộp CAO HƠN chân + STEP_MAX (bậc thấp thì bước lên được)
    và THẤP HƠN đỉnh đầu (trần/mái ở trên đầu thì không cản).
    """
    low = feet_y + STEP_MAX
    high = feet_y + PLAYER_HEIGHT
    r = PLAYER_RADIUS
    for i, (x0, x1, y0, y1, z0, z1) in enumerate(_boxes):
        if not _enabled[i] or y1 <= low or y0 >= high:
            continue
        # Nở hộp ra r mỗi phía rồi kiểm tra tâm người chơi nằm trong hộp nở
        if x0 - r < x < x1 + r and z0 - r < z < z1 + r:
            return True
    return False


def ground_height(x, z, feet_y):
    """
    Độ cao mặt đi được ngay dưới (x, z): đỉnh cao nhất trong các hộp
    có đỉnh không cao hơn chân + STEP_MAX. Không có hộp nào thì là mặt đất y=0.
    """
    limit = feet_y + STEP_MAX
    best = 0.0
    for i, (x0, x1, y0, y1, z0, z1) in enumerate(_boxes):
        if _enabled[i] and y1 <= limit and y1 > best and x0 <= x <= x1 and z0 <= z <= z1:
            best = y1
    return best


def move(x, z, dx, dz, feet_y):
    """
    Di chuyển (dx, dz). Thử riêng trục X rồi trục Z để TRƯỢT dọc tường.
    Chia nhỏ thành các bước <= MAX_SUBSTEP. Trả về (x, z, feet_y mới).
    """
    dist = math.hypot(dx, dz)
    n = max(1, math.ceil(dist / MAX_SUBSTEP))
    sx, sz = dx / n, dz / n
    for _ in range(n):
        if not is_blocked(x + sx, z, feet_y):
            x += sx
        if not is_blocked(x, z + sz, feet_y):
            z += sz
        g = ground_height(x, z, feet_y)   # bước lên bậc/sàn cao hơn thì chân nâng lên ngay
        if g > feet_y:
            feet_y = g
    return x, z, feet_y


def settle(x, z, feet_y, dt):
    """Cập nhật độ cao chân: lên bậc thì nâng ngay, chỗ thấp hơn thì rơi xuống."""
    g = ground_height(x, z, feet_y)
    if g > feet_y:
        feet_y = g
    elif g < feet_y:
        feet_y = max(g, feet_y - FALL_SPEED * dt)
    return feet_y