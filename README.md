# Nha3D — Mô phỏng Ngôi nhà 3D, Hệ thống Đặt đồ đạc & Quan sát 3D

## 1. Giới thiệu

**Nha3D** là ứng dụng đồ họa 3D tương tác thời gian thực bằng Python, sử dụng OpenGL cổ điển (Compatibility Profile) và GLFW.
Dự án cho phép người dùng tham quan ngôi nhà 2 tầng góc nhìn thứ nhất (FPS), đóng/mở cửa có hoạt ảnh quanh bản lề, bật/tắt đèn từng phòng, và đặc biệt là hệ thống **Túi đồ & Đặt đồ đạc (Building/Placement system)** tương tự game xây dựng, kèm chế độ **Cầm đồ vật lên quan sát 3D 360° (Inspect mode)**.

---

## 2. Các Tính năng Chính

1. **Góc nhìn thứ nhất (FPS) & Va chạm AABB**:
   - Di chuyển bằng `W`, `A`, `S`, `D`, giữ `Shift` để chạy nhanh.
   - Di chuyển chuột xoay góc nhìn mượt mà, hạn chế góc ngẩng/cúi tránh lộn ngược.
   - Hệ thống va chạm tự động ngăn đi xuyên tường, trượt mượt mà dọc tường, tự bước lên các bậc cầu thang và rơi xuống tự nhiên khi bước hụt.
2. **Kiến trúc Ngôi nhà 2 tầng Hoàn chỉnh**:
   - Tầng trệt: Phòng khách, Phòng ăn, Bếp nấu.
   - Tầng 2: Sảnh tầng 2, Phòng ngủ 1, Phòng ngủ 2.
   - Cầu thang 14 bậc kết nối 2 tầng, **lan can bảo vệ quanh lỗ cầu thang** chống ngã.
   - Cửa sổ khung gỗ với **kính bán trong suốt** nhìn ra cảnh quan sân vườn bên ngoài.
   - 5 cánh cửa xoay bản lề mượt mà (cửa chính và các cửa phòng) với cơ chế an toàn chống kẹp người chơi.
3. **Chiếu sáng Phòng**:
   - Phím `F`: Bật / tắt đèn trần của căn phòng người chơi đang đứng. Ánh sáng ấm áp với hiệu ứng suy giảm theo khoảng cách.
4. **Hệ thống Túi đồ & Đặt đồ đạc (Sandbox Building System)**:
   - Phím `Q`: Bật / tắt hiển thị thanh túi đồ (Hotbar).
   - Phím số `1` đến `8`: Chọn đồ vật trong túi (Bàn gỗ, Ghế, Sofa, Giường, Tủ quần áo, Kệ sách, Tủ lạnh, Kệ TV, Đèn bàn).
   - Khi chọn đồ: Hiển thị hình chiếu trước (Ghost Preview) trên sàn nhà phía trước người chơi.
   - Phím `Space`: Xoay chiều đồ vật theo chiều kim đồng hồ (xoay 90° quanh trục Y).
   - Phím `E` hoặc `Chuột Trái`: Đặt đồ vật xuống sàn, đồ vật cố định và tự động có hộp va chạm AABB.
   - Nhắm vào đồ vật đã đặt trên sàn và nhấn `E` hoặc `Chuột Trái`: Thu hồi đồ vật lại vào túi.
5. **Cơ chế Cầm đồ vật lên Quan sát 3D 360° (Inspect Mode)**:
   - Phím `V`: Cầm đồ vật đang chọn (hoặc đồ vật đang nhìn tới) lên giữa màn hình.
   - Di chuyển chuột qua lại: Xoay đồ vật 360 độ tự do quanh mọi trục để ngắm nghía chi tiết (áp dụng cho mọi đồ vật: bàn, ghế, sofa, giường, tủ...).
   - Nhấn `V` hoặc `Chuột Phải` để thoát chế độ quan sát, quay trở lại đi lại bình thường.
6. **Giao diện HUD 2D thuần OpenGL**:
   - Tâm ngắm chữ thập chính giữa màn hình.
   - Thanh Hotbar hiển thị các ô đồ vật kèm số phím tắt `[1]` .. `[8]`.
   - Thông báo gợi ý hành động ngữ cảnh (`[E] Mở cửa`, `[E] Đóng cửa`, `[E] Thu hồi`, `[Space] Xoay`, `[V] Soi 3D`).
   - Tên phòng người chơi đang đứng ở góc trên bên trái.
   - Bảng phím tắt vắn tắt ở góc trên bên phải.
   - Tự dựng bằng font vector nét `GL_LINES`, 100% không phụ thuộc thư viện ngoài.

---

## 3. Bảng Phím Tắt Điều Khiển

| Phím / Chuột | Chức năng |
|---|---|
| **W, A, S, D** | Di chuyển (Tiến / Lùi / Trái / Phải) |
| **Shift + WASD** | Chạy nhanh |
| **Di chuột** | Xoay góc nhìn camera (hoặc xoay 360° vật thể khi Inspect) |
| **F** | Bật / tắt đèn phòng hiện tại |
| **Q** | Bật / tắt thanh hiển thị túi đồ |
| **Phím 1 .. 8** | Chọn món đồ trong túi để cầm trên tay |
| **Space** | Xoay hướng đồ vật chuẩn bị đặt (+90° theo chiều kim đồng hồ) |
| **Chuột Trái / E** | Đặt đồ vật xuống sàn / Thu hồi đồ vật / Đóng mở cửa |
| **V** | Cầm đồ vật lên trước mắt để xoay chuột quan sát 3D |
| **Chuột Phải** | Bỏ chọn đồ đang cầm / Thoát chế độ quan sát 3D |
| **ESC** | Thoát chế độ quan sát 3D / Thoát chương trình |

---

## 4. Hướng dẫn Cài đặt & Chạy

Yêu cầu môi trường:
- Python 3.9+ (đã kiểm tra tương thích hoàn hảo trên Python 3.13)
- Windows 10/11 (hỗ trợ OpenGL và GLFW)

Mở terminal tại thư mục dự án:

```powershell
pip install -r requirements.txt
python main.py
```
