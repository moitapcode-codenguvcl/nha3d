# Nha3D — Mô phỏng và tham quan ngôi nhà 3D

## 1. Giới thiệu

Nha3D là ứng dụng Python sử dụng OpenGL để hiển thị mô hình ngôi nhà 3D và cho phép người dùng tham quan trong môi trường 3D.

## 2. Yêu cầu

- Windows 10/11
- Python đã được cài đặt
- Hỗ trợ OpenGL và GLFW
- Docker Desktop (tùy chọn, dành cho môi trường phát triển)

## 3. Chạy ứng dụng trên Windows

Mở terminal tại thư mục dự án và chạy:

```powershell
py -m pip install -r requirements.txt
py main.py
```

## 4. Sử dụng Docker

Build image:

```powershell
docker build -t nha3d-dev .
```

Khởi chạy container:

```powershell
docker run -it --rm -v "${PWD}:/app" nha3d-dev
```

Kiểm tra thư viện:

```bash
python -c "import glfw; import OpenGL.GL; print('Dependencies OK')"
```

Lưu ý: Cấu hình Docker hiện tại phục vụ môi trường Python và phát triển source code. Để mở cửa sổ OpenGL trên Windows, hãy chạy ứng dụng trực tiếp bằng Python.

## 5. Phát triển dự án

- Chỉnh sửa các file Python để bổ sung tính năng.
- Cập nhật `requirements.txt` khi thêm dependency.
- Giữ lại các file và tài nguyên mà chương trình cần để hoạt động.

## 6. Đóng góp

Bạn có thể tiếp tục phát triển mô hình 3D, hệ thống điều khiển camera, tương tác với vật thể và các tính năng tham quan khác.