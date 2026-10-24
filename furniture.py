"""
furniture.py — Định nghĩa các mẫu nội thất & đồ đạc đơn giản theo phong cách OpenGL cổ điển.
Không dùng shader, không dùng model ngoài. Tự dựng từ các hình khối cơ bản (box, cylinder).
Hỗ trợ:
- Vẽ bình thường với màu sắc hài hòa.
- Vẽ chế độ xem trước (preview/ghost) khi đang đặt đồ vật.
- Tính toán hộp va chạm AABB theo góc xoay (0, 90, 180, 270 độ).
"""

import math
from OpenGL.GL import (
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef,
    glColor3f, glColor4f, glEnable, glDisable,
    GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
)
from shapes import draw_box, draw_box_at, draw_cylinder


preview_valid = True  # Trạng thái vị trí preview có hợp lệ để đặt hay không

def _apply_color(r, g, b, preview, alpha=0.6):
    """Áp dụng màu sắc. Nếu là preview: Xanh lá nếu hợp lệ, Đỏ nếu vướng vật cản."""
    if preview:
        if preview_valid:
            glColor4f(0.2, 0.9, 0.4, alpha)
        else:
            glColor4f(0.95, 0.2, 0.2, alpha)
    else:
        glColor3f(r, g, b)


# ───────────────────────────────────────────────
# CÁC HÀM VẼ TỪNG LOẠI ĐỒ ĐẠC
# Tâm của mỗi đồ vật đặt tại (0, 0, 0) trên mặt sàn (chân chạm đất y=0)
# ───────────────────────────────────────────────

def draw_table(preview=False):
    """Bàn gỗ đơn giản: Mặt bàn + 4 chân."""
    # Mặt bàn (rộng 1.4m x sâu 0.8m x dày 0.06m, cao 0.75m)
    _apply_color(0.60, 0.40, 0.22, preview)
    draw_box_at(0.0, 0.72, 0.0, 1.4, 0.06, 0.8)

    # 4 chân bàn (hình trụ hoặc hộp vuông 0.06m x 0.06m x cao 0.69m)
    _apply_color(0.45, 0.28, 0.15, preview)
    leg_x, leg_z = 0.60, 0.32
    leg_h = 0.69
    for dx in (-leg_x, leg_x):
        for dz in (-leg_z, leg_z):
            draw_box_at(dx, leg_h / 2.0, dz, 0.08, leg_h, 0.08)


def draw_chair(preview=False):
    """Ghế ăn đơn giản: Mặt ghế, 4 chân, tựa lưng."""
    # Mặt ghế cao 0.45m (0.45m x 0.45m x dày 0.05m)
    _apply_color(0.55, 0.35, 0.18, preview)
    draw_box_at(0.0, 0.42, 0.0, 0.45, 0.05, 0.45)

    # 4 chân ghế
    _apply_color(0.40, 0.25, 0.12, preview)
    leg_d = 0.17
    for dx in (-leg_d, leg_d):
        for dz in (-leg_d, leg_d):
            draw_box_at(dx, 0.20, dz, 0.05, 0.40, 0.05)

    # Tựa lưng ghế (ở phía sau z = -0.18)
    _apply_color(0.50, 0.30, 0.15, preview)
    draw_box_at(0.0, 0.68, -0.19, 0.45, 0.48, 0.04)


def draw_sofa(preview=False):
    """Sofa phòng khách: Đệm ngồi êm ái, lưng tựa và 2 tay vịn."""
    # Phần đế đệm ngồi (rộng 1.8m x sâu 0.85m x cao 0.42m)
    _apply_color(0.32, 0.42, 0.52, preview) # Xám xanh hiện đại
    draw_box_at(0.0, 0.21, 0.05, 1.8, 0.42, 0.75)

    # Đệm ngồi nổi (dày 0.1m)
    _apply_color(0.38, 0.50, 0.62, preview)
    draw_box_at(0.0, 0.44, 0.05, 1.76, 0.08, 0.73)

    # Lưng tựa sofa (cao 0.85m, phía sau z = -0.32)
    _apply_color(0.28, 0.38, 0.48, preview)
    draw_box_at(0.0, 0.55, -0.32, 1.8, 0.70, 0.20)

    # 2 tay vịn bên trái và phải
    _apply_color(0.25, 0.34, 0.44, preview)
    for dx in (-0.85, 0.85):
        draw_box_at(dx, 0.40, 0.0, 0.18, 0.50, 0.85)


def draw_bed(preview=False):
    """Giường ngủ: Khung gỗ, đệm trắng, gối đầu và chăn."""
    # Khung giường gỗ (dài 2.0m x rộng 1.6m x cao 0.35m)
    _apply_color(0.50, 0.32, 0.18, preview)
    draw_box_at(0.0, 0.175, 0.0, 1.6, 0.35, 2.0)

    # Thành đầu giường (cao 0.9m ở z = -0.95)
    _apply_color(0.42, 0.26, 0.14, preview)
    draw_box_at(0.0, 0.50, -0.95, 1.6, 0.70, 0.10)

    # Nệm trắng (dày 0.2m)
    _apply_color(0.92, 0.92, 0.94, preview)
    draw_box_at(0.0, 0.42, 0.05, 1.5, 0.18, 1.85)

    # 2 chiếc gối đầu ở sát thành đầu giường
    _apply_color(0.85, 0.85, 0.90, preview)
    draw_box_at(-0.40, 0.54, -0.65, 0.55, 0.10, 0.35)
    draw_box_at(0.40, 0.54, -0.65, 0.55, 0.10, 0.35)

    # Chăn gấp phía đuôi giường (màu xanh than ấm áp)
    _apply_color(0.25, 0.40, 0.55, preview)
    draw_box_at(0.0, 0.45, 0.35, 1.52, 0.16, 1.20)


def draw_wardrobe(preview=False):
    """Tủ quần áo 2 cánh: Hộp đứng cao 2.1m x rộng 1.2m x sâu 0.6m."""
    # Thân tủ chính
    _apply_color(0.45, 0.28, 0.16, preview)
    draw_box_at(0.0, 1.05, 0.0, 1.2, 2.1, 0.6)

    # Đường rãnh chia đôi cánh cửa và 2 tay nắm tủ
    _apply_color(0.75, 0.70, 0.60, preview)
    draw_box_at(-0.04, 1.05, 0.305, 0.03, 0.18, 0.02)
    draw_box_at(0.04, 1.05, 0.305, 0.03, 0.18, 0.02)


def draw_shelf(preview=False):
    """Kệ sách 4 tầng: Gỗ sẫm màu có các cuốn sách nhiều màu."""
    # Khung kệ (cao 1.8m x rộng 1.0m x sâu 0.35m)
    _apply_color(0.38, 0.24, 0.14, preview)
    # Tấm sau
    draw_box_at(0.0, 0.90, -0.16, 1.0, 1.8, 0.03)
    # 2 tấm hông
    draw_box_at(-0.48, 0.90, 0.0, 0.04, 1.8, 0.35)
    draw_box_at(0.48, 0.90, 0.0, 0.04, 1.8, 0.35)
    # 4 tầng ngăn
    for y in (0.05, 0.50, 0.95, 1.40, 1.78):
        draw_box_at(0.0, y, 0.0, 0.96, 0.04, 0.34)

    # Vài cuốn sách trang trí ở các tầng
    if not preview:
        colors = [(0.8, 0.2, 0.2), (0.2, 0.5, 0.8), (0.2, 0.7, 0.3), (0.8, 0.7, 0.2)]
        for i, c in enumerate(colors):
            _apply_color(c[0], c[1], c[2], False)
            draw_box_at(-0.35 + i * 0.18, 0.68, 0.0, 0.12, 0.30, 0.24)
            draw_box_at(0.35 - i * 0.16, 1.13, 0.0, 0.10, 0.28, 0.24)


def draw_fridge(preview=False):
    """Tủ lạnh 2 cánh gia đình: Màu xám bạc kim loại hiện đại."""
    # Thân tủ lạnh (cao 1.85m x rộng 0.8m x sâu 0.75m)
    _apply_color(0.78, 0.80, 0.82, preview)
    draw_box_at(0.0, 0.925, 0.0, 0.80, 1.85, 0.75)

    # Rãnh phân cách ngăn đông (trên) và ngăn mát (dưới)
    _apply_color(0.20, 0.20, 0.20, preview)
    draw_box_at(0.0, 1.25, 0.378, 0.80, 0.02, 0.01)

    # Tay nắm cửa tủ lạnh
    _apply_color(0.35, 0.35, 0.35, preview)
    draw_box_at(-0.30, 1.40, 0.39, 0.04, 0.20, 0.03) # Ngăn trên
    draw_box_at(-0.30, 0.95, 0.39, 0.04, 0.40, 0.03) # Ngăn dưới


def draw_lamp(preview=False):
    """Đèn bàn / Đèn ngủ: Đế tròn, thân kim loại, chụp đèn ấm cúng."""
    # Đế đèn (đường kính 0.2m x cao 0.03m)
    _apply_color(0.30, 0.30, 0.30, preview)
    draw_box_at(0.0, 0.02, 0.0, 0.20, 0.04, 0.20)

    # Thân đèn (cao 0.35m)
    _apply_color(0.70, 0.65, 0.40, preview)
    draw_box_at(0.0, 0.20, 0.0, 0.04, 0.36, 0.04)

    # Chụp đèn nón/hộp (màu kem sáng)
    _apply_color(0.95, 0.90, 0.70, preview)
    draw_box_at(0.0, 0.42, 0.0, 0.28, 0.20, 0.28)


def draw_tv_unit(preview=False):
    """Kệ Tivi + Tivi màn hình phẳng siêu mỏng."""
    # Kệ tủ tivi bằng gỗ nằm ngang (dài 1.6m x cao 0.45m x sâu 0.45m)
    _apply_color(0.35, 0.22, 0.12, preview)
    draw_box_at(0.0, 0.225, 0.0, 1.6, 0.45, 0.45)

    # Chân đế TV kim loại
    _apply_color(0.2, 0.2, 0.2, preview)
    draw_box_at(0.0, 0.48, 0.0, 0.40, 0.04, 0.25)
    draw_box_at(0.0, 0.56, 0.0, 0.08, 0.14, 0.06)

    # Khung TV màn hình mỏng (rộng 1.2m x cao 0.7m x dày 0.04m)
    _apply_color(0.12, 0.12, 0.12, preview)
    draw_box_at(0.0, 0.98, 0.0, 1.24, 0.72, 0.04)

    # Màn hình TV (màu đen bóng)
    _apply_color(0.05, 0.08, 0.12, preview)
    draw_box_at(0.0, 0.98, 0.022, 1.18, 0.66, 0.01)


# ───────────────────────────────────────────────
# DANH MỤC CÁC LOẠI ĐỒ ĐẠC
# ───────────────────────────────────────────────
FURNITURE_TYPES = {
    "table": {
        "name": "Bàn gỗ",
        "size": (1.4, 0.75, 0.8),
        "draw": draw_table,
    },
    "chair": {
        "name": "Ghế tựa",
        "size": (0.5, 0.92, 0.5),
        "draw": draw_chair,
    },
    "sofa": {
        "name": "Sofa đệm",
        "size": (1.8, 0.90, 0.85),
        "draw": draw_sofa,
    },
    "bed": {
        "name": "Giường ngủ",
        "size": (1.6, 0.90, 2.0),
        "draw": draw_bed,
    },
    "wardrobe": {
        "name": "Tủ quần áo",
        "size": (1.2, 2.10, 0.6),
        "draw": draw_wardrobe,
    },
    "shelf": {
        "name": "Kệ sách",
        "size": (1.0, 1.80, 0.35),
        "draw": draw_shelf,
    },
    "fridge": {
        "name": "Tủ lạnh",
        "size": (0.8, 1.85, 0.75),
        "draw": draw_fridge,
    },
    "tv": {
        "name": "Kệ & Tivi",
        "size": (1.6, 1.35, 0.45),
        "draw": draw_tv_unit,
    },
    "lamp": {
        "name": "Đèn bàn",
        "size": (0.3, 0.55, 0.3),
        "draw": draw_lamp,
    },
}

# Danh sách thứ tự phím tắt 1..8
SLOT_KEYS = ["table", "chair", "sofa", "bed", "wardrobe", "shelf", "fridge", "tv", "lamp"]


# ───────────────────────────────────────────────
# QUẢN LÝ CÁC ĐỒ ĐẠC ĐÃ ĐẶT TRONG THẾ GIỚI
# ───────────────────────────────────────────────
class PlacedItem:
    def __init__(self, item_type: str, x: float, y: float, z: float, rot: float = 0.0):
        self.item_type = item_type
        self.x = x
        self.y = y
        self.z = z
        self.rot = rot # Góc xoay (độ): 0, 90, 180, 270
        self.collision_id = None
        self.info = FURNITURE_TYPES[item_type]

    def get_aabb(self):
        """Tính toán hộp va chạm AABB tính theo góc xoay quanh trục Y."""
        w, h, d = self.info["size"]
        rad = math.radians(self.rot)
        # Khi xoay quanh Y, độ rộng theo X và Z sẽ biến đổi
        cos_a = abs(math.cos(rad))
        sin_a = abs(math.sin(rad))
        box_w = w * cos_a + d * sin_a
        box_d = w * sin_a + d * cos_a

        half_w = box_w / 2.0
        half_d = box_d / 2.0
        return (self.x - half_w, self.x + half_w,
                self.y, self.y + h,
                self.z - half_d, self.z + half_d)

    def draw(self, preview=False):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rot, 0.0, 1.0, 0.0)
        self.info["draw"](preview=preview)
        glPopMatrix()


# Danh sách các đồ đạc hiện có trong nhà
PLACED_ITEMS = []


def add_placed_item(item_type: str, x: float, y: float, z: float, rot: float = 0.0, register_collision=True):
    """Tạo đồ vật đặt trong nhà và đăng ký va chạm nếu cần."""
    import collision
    item = PlacedItem(item_type, x, y, z, rot)
    if register_collision:
        x0, x1, y0, y1, z0, z1 = item.get_aabb()
        item.collision_id = collision.add_box(x0, x1, y0, y1, z0, z1)
    PLACED_ITEMS.append(item)
    return item


def remove_placed_item(item):
    """Xóa đồ vật và tắt hộp va chạm."""
    import collision
    if item in PLACED_ITEMS:
        if item.collision_id is not None:
            collision.set_enabled(item.collision_id, False)
        PLACED_ITEMS.remove(item)


def draw_all_placed_items():
    """Vẽ toàn bộ đồ đạc đã đặt trong nhà."""
    for item in PLACED_ITEMS:
        item.draw(preview=False)


def setup_default_house_furniture():
    """Bố trí sẵn một số nội thất cơ bản ban đầu cho các phòng."""
    PLACED_ITEMS.clear()

    # 1. Phòng khách (Tầng trệt: x: -7..1, z: -5..5)
    add_placed_item("sofa", -3.5, 0.1, -1.0, rot=0.0)
    add_placed_item("table", -3.5, 0.1, 0.5, rot=0.0)
    add_placed_item("tv", -3.5, 0.1, 3.5, rot=180.0)
    add_placed_item("shelf", -6.5, 0.1, 1.0, rot=90.0)

    # 2. Phòng ăn & Bếp (Tầng trệt: x: 1..7, z: -5..5)
    # Phòng ăn (z: -5..0)
    add_placed_item("table", 4.0, 0.1, -2.5, rot=0.0)
    add_placed_item("chair", 4.0, 0.1, -1.7, rot=180.0)
    add_placed_item("chair", 4.0, 0.1, -3.3, rot=0.0)
    # Bếp (z: 0..5)
    add_placed_item("fridge", 6.2, 0.1, 0.8, rot=-90.0)

    # 3. Tầng 2: Phòng ngủ 1 (z: -5..0) & Phòng ngủ 2 (z: 0..5)
    # Phòng ngủ 1 (y = 3.0)
    add_placed_item("bed", 4.0, 3.0, -3.2, rot=0.0)
    add_placed_item("wardrobe", 6.2, 3.0, -1.5, rot=-90.0)
    add_placed_item("lamp", 2.2, 3.0, -4.2, rot=0.0)

    # Phòng ngủ 2 (y = 3.0)
    add_placed_item("bed", 4.0, 3.0, 3.2, rot=180.0)
    add_placed_item("shelf", 6.2, 3.0, 1.5, rot=-90.0)
