# SPEC.md — Đồ án: Mô phỏng Ngôi nhà 3D Tương tác (OpenGL)

## 1. Tổng quan

Mô phỏng ngôi nhà 3D góc nhìn thứ nhất (first-person) sử dụng OpenGL cổ điển.
Người dùng có thể đi lại trong nhà, mở/đóng cửa, bật/tắt đèn, dùng đèn pin và khám phá đồ vật.

---

## 2. Công nghệ

| Thư viện | Vai trò |
|---|---|
| Python 3 | Ngôn ngữ chính |
| glfw | Tạo cửa sổ, xử lý sự kiện bàn phím/chuột |
| PyOpenGL | Binding OpenGL cho Python |
| numpy | Phép toán vector/ma trận |

> **Quy tắc OpenGL**: Dùng OpenGL cổ điển — `glPushMatrix`, `glTranslatef`, `glRotatef`, `glLight`, `glMaterial`. **KHÔNG** dùng shader (GLSL). **KHÔNG** dùng model 3D có sẵn — mọi vật thể tự dựng từ hình hộp, hình trụ, hình cầu.

---

## 3. Cấu trúc File

```
nha3d/
├── main.py          # Cửa sổ glfw, vòng lặp chính, xử lý input tổng hợp
├── camera.py        # Góc nhìn thứ nhất: vị trí, hướng nhìn, di chuyển
├── shapes.py        # Hàm vẽ hình cơ bản: hộp, trụ, cầu, mặt phẳng
├── house.py         # Tổng hợp ngôi nhà: phòng, tường, sàn, mái, cửa sổ, đồ đạc
├── doors.py         # Cửa mở/đóng với hoạt ảnh quanh bản lề
├── lights.py        # Đèn phòng (glLight) và đèn pin (spotlight)
├── collision.py     # Va chạm AABB (Axis-Aligned Bounding Box)
├── items.py         # Đồ vật có thể nhặt/tương tác
├── requirements.txt
└── README.md
```

---

## 4. Chức năng Chi tiết

### 4.1 Di chuyển góc nhìn thứ nhất
- **WASD**: tiến/lui/trái/phải
- **Chuột**: xoay camera (yaw/pitch)
- **Shift + WASD**: chạy nhanh
- **ESC**: thoát chương trình
- Camera bị giới hạn chiều cao (không bay)

### 4.2 Ngôi nhà 1 tầng — 3 phòng
| Phòng | Đồ đạc |
|---|---|
| Phòng khách | Sofa, bàn cà phê, TV, kệ sách |
| Phòng ngủ | Giường, tủ quần áo, bàn đầu giường |
| Phòng bếp | Bàn bếp, ghế, tủ lạnh, bồn rửa |

Cấu trúc: tường, sàn, mái (hình hộp), cửa sổ (ô kính mỏng).

### 4.3 Va chạm — Không đi xuyên tường
- Mỗi tường/đồ vật là một AABB (hộp bao quanh)
- Trước mỗi bước di chuyển, kiểm tra giao nhau và chặn lại

### 4.4 Cửa mở/đóng
- Phím **E** khi đứng gần cửa (< 2m)
- Hoạt ảnh xoay quanh bản lề (`glRotatef`) từ 0° → 90°
- Trạng thái: CLOSED, OPENING, OPEN, CLOSING

### 4.5 Đèn phòng
- Phím **L**: bật/tắt đèn phòng hiện tại đang đứng
- Dùng `glLight` (GL_LIGHT1, GL_LIGHT2, GL_LIGHT3)
- Khi tắt đèn: ambient rất thấp, chỉ đèn pin chiếu sáng

### 4.6 Đèn pin
- Phím **F**: bật/tắt đèn pin cầm tay
- Spotlight (`GL_SPOT_CUTOFF`, `GL_SPOT_DIRECTION`) theo hướng camera
- Dùng GL_LIGHT0

### 4.7 Nhặt và xem đồ vật *(nếu còn thời gian)*
- Phím **E** khi đứng gần đồ vật (< 1.5m)
- Hiển thị tên và mô tả trên HUD

### 4.8 HUD và README
- Hiển thị gợi ý phím trên màn hình (dùng bitmap font hoặc góc HUD đơn giản)
- README.md hướng dẫn cài đặt và chạy

---

## 5. Quy tắc Code

- **Comment tiếng Việt** giải thích các phép biến đổi 3D (translate, rotate, scale)
- **Mỗi chức năng là một hàm riêng** (không viết logic lẫn lộn vào vòng lặp chính)
- **Đơn vị**: mét (1 đơn vị OpenGL = 1 mét)
- **Mỗi lần chỉ làm đúng việc được yêu cầu** (không thêm ngoài spec)
- Tên biến/hàm: tiếng Anh (snake_case), comment: tiếng Việt

---

## 6. Tiến độ

- [x] Bước 0: Cửa sổ, vòng lặp, shapes cơ bản
- [x] Bước 1: Camera góc nhìn thứ nhất
- [x] Bước 2: Ngôi nhà — tường, sàn, mái, phòng, cửa sổ kính, lan can cầu thang
- [x] Bước 3: Va chạm AABB
- [x] Bước 4: Cửa mở/đóng có hoạt ảnh quanh bản lề
- [x] Bước 5: Hệ thống đèn phòng (phím F)
- [x] Bước 6: Đồ đạc nội thất từng phòng (furniture.py)
- [x] Bước 7: Hệ thống Túi đồ (phím Q, số 1..8) & Đặt đồ vật (Space xoay, Click/E đặt) (inventory.py)
- [x] Bước 8: Cơ chế Cầm đồ vật lên xoay chuột quan sát 3D 360 độ (Inspect mode - phím V) (inspect.py)
- [x] Bước 9: HUD 2D trực tiếp trên màn hình (hud.py) + README hoàn chỉnh
