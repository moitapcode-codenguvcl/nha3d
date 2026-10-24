"""
shapes.py — Các hàm vẽ hình học cơ bản bằng OpenGL cổ điển.
Không dùng shader. Mọi hình tự dựng từ quads và triangles.
Đơn vị: mét.
"""

from OpenGL.GL import (
    glBegin, glEnd, glVertex3f, glNormal3f,
    glPushMatrix, glPopMatrix,
    glScalef, glTranslatef,
    GL_QUADS, GL_TRIANGLES,
)
from OpenGL.GLU import gluNewQuadric, gluCylinder, gluSphere, gluQuadricNormals, GLU_SMOOTH


# ─────────────────────────────────────────────
# HÌNH HỘP (Box)
# ─────────────────────────────────────────────

def draw_box(width: float, height: float, depth: float) -> None:
    """
    Vẽ hình hộp chữ nhật có kích thước width x height x depth.
    Tâm hộp đặt tại gốc tọa độ hiện tại.
    
    Quy ước trục:
        X: chiều ngang (width)
        Y: chiều cao  (height)
        Z: chiều sâu  (depth)
    """
    # Nửa kích thước mỗi chiều — để hộp cân đối quanh gốc tọa độ
    w = width  / 2.0
    h = height / 2.0
    d = depth  / 2.0

    glBegin(GL_QUADS)

    # ── Mặt TRƯỚC (normal hướng ra +Z) ──
    glNormal3f(0.0,  0.0,  1.0)
    glVertex3f(-w, -h,  d)
    glVertex3f( w, -h,  d)
    glVertex3f( w,  h,  d)
    glVertex3f(-w,  h,  d)

    # ── Mặt SAU (normal hướng ra -Z) ──
    glNormal3f(0.0,  0.0, -1.0)
    glVertex3f( w, -h, -d)
    glVertex3f(-w, -h, -d)
    glVertex3f(-w,  h, -d)
    glVertex3f( w,  h, -d)

    # ── Mặt TRÊN (normal hướng ra +Y) ──
    glNormal3f(0.0,  1.0,  0.0)
    glVertex3f(-w,  h, -d)
    glVertex3f( w,  h, -d)
    glVertex3f( w,  h,  d)
    glVertex3f(-w,  h,  d)

    # ── Mặt DƯỚI (normal hướng ra -Y) ──
    glNormal3f(0.0, -1.0,  0.0)
    glVertex3f(-w, -h,  d)
    glVertex3f( w, -h,  d)
    glVertex3f( w, -h, -d)
    glVertex3f(-w, -h, -d)

    # ── Mặt PHẢI (normal hướng ra +X) ──
    glNormal3f(1.0,  0.0,  0.0)
    glVertex3f( w, -h,  d)
    glVertex3f( w, -h, -d)
    glVertex3f( w,  h, -d)
    glVertex3f( w,  h,  d)

    # ── Mặt TRÁI (normal hướng ra -X) ──
    glNormal3f(-1.0, 0.0,  0.0)
    glVertex3f(-w, -h, -d)
    glVertex3f(-w, -h,  d)
    glVertex3f(-w,  h,  d)
    glVertex3f(-w,  h, -d)

    glEnd()


def draw_box_at(x: float, y: float, z: float,
                width: float, height: float, depth: float) -> None:
    """
    Vẽ hình hộp có tâm tại (x, y, z) với kích thước tùy chỉnh.
    Dùng glPushMatrix / glPopMatrix để không làm ảnh hưởng các phép biến đổi bên ngoài.
    """
    glPushMatrix()
    # Dịch chuyển tới vị trí (x, y, z) trong không gian thế giới
    glTranslatef(x, y, z)
    draw_box(width, height, depth)
    glPopMatrix()


# ─────────────────────────────────────────────
# HÌNH TRỤ (Cylinder)
# ─────────────────────────────────────────────

def draw_cylinder(radius: float, height: float, slices: int = 16) -> None:
    """
    Vẽ hình trụ đứng (trục Y) với bán kính và chiều cao tùy chỉnh.
    Đáy trụ tại y=0, đỉnh trụ tại y=height.
    """
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)

    glPushMatrix()
    # GLU cylinder mặc định theo trục Z — xoay -90° quanh X để đứng theo Y
    from OpenGL.GL import glRotatef
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    gluCylinder(quad, radius, radius, height, slices, 1)
    glPopMatrix()


# ─────────────────────────────────────────────
# HÌNH CẦU (Sphere)
# ─────────────────────────────────────────────

def draw_sphere(radius: float, slices: int = 16, stacks: int = 16) -> None:
    """
    Vẽ hình cầu tại gốc tọa độ hiện tại với bán kính tùy chỉnh.
    """
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)


# ─────────────────────────────────────────────
# MẶT PHẲNG nằm ngang (Flat Plane)
# ─────────────────────────────────────────────

def draw_plane(width: float, depth: float) -> None:
    """
    Vẽ mặt phẳng nằm ngang tại y=0.
    Normal hướng lên +Y.
    Dùng để vẽ sàn nhà hoặc trần nhà.
    """
    w = width / 2.0
    d = depth / 2.0

    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)   # Normal hướng lên
    glVertex3f(-w, 0.0, -d)
    glVertex3f( w, 0.0, -d)
    glVertex3f( w, 0.0,  d)
    glVertex3f(-w, 0.0,  d)
    glEnd()
