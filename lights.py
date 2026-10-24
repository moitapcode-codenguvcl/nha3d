"""lights.py — Bước 5: đèn trần cho 6 phòng (phím L) + ánh sáng ngoài trời yếu."""
from OpenGL.GL import (
    glEnable, glDisable, glLightfv, glLightf, glLightModelfv, glColorMaterial,
    glShadeModel, glColor3f, glPushMatrix, glPopMatrix, glTranslatef,
    GL_LIGHTING, GL_LIGHT0, GL_LIGHT7, GL_POSITION, GL_AMBIENT, GL_DIFFUSE,
    GL_SPECULAR, GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION,
    GL_QUADRATIC_ATTENUATION, GL_LIGHT_MODEL_AMBIENT, GL_COLOR_MATERIAL,
    GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, GL_SMOOTH,
)
from shapes import draw_sphere

# (tên, x0, x1, z0, z1, tầng)  — tầng 0 = trệt, tầng 1 = lầu
ROOMS = [
    ("Phòng khách", -7, 1, -5, 5, 0),
    ("Phòng ăn",     1, 7, -5, 0, 0),
    ("Bếp",          1, 7,  0, 5, 0),
    ("Sảnh tầng 2", -7, 1, -5, 5, 1),
    ("Phòng ngủ 1",  1, 7, -5, 0, 1),
    ("Phòng ngủ 2",  1, 7,  0, 5, 1),
]
FLOOR_BASE = [0.0, 3.0]   # độ cao mặt sàn từng tầng (m)
BULB_HEIGHT = 2.65        # bóng đèn cao hơn sàn bao nhiêu (trần cao 2.8 m)
FLOOR_SPLIT = 2.9         # chân người chơi thấp hơn mức này => đang ở tầng trệt
START_ON = True           # True: lúc đầu đèn mọi phòng đều bật

lights_on = [START_ON] * len(ROOMS)


def _light_id(i):
    # phòng số i dùng GL_LIGHT1.. (GL_LIGHT0 để dành cho đèn pin)
    return GL_LIGHT0 + 1 + i


def _bulb_position(i):
    # bóng đèn đặt ở chính giữa phòng, sát trần
    _, x0, x1, z0, z1, floor = ROOMS[i]
    return ((x0 + x1) / 2, FLOOR_BASE[floor] + BULB_HEIGHT, (z0 + z1) / 2)


def setup_all_lights():
    """Gọi 1 lần trước vòng lặp: bật hệ thống chiếu sáng và cấu hình các đèn."""
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    # ánh sáng nền toàn cảnh: thấp để phòng tắt đèn trông tối
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.12, 0.12, 0.14, 1.0])

    # ánh sáng ngoài trời (đèn song song, yếu hơn bản cũ)
    glLightfv(GL_LIGHT7, GL_AMBIENT, [0.10, 0.10, 0.10, 1.0])
    glLightfv(GL_LIGHT7, GL_DIFFUSE, [0.45, 0.45, 0.42, 1.0])
    glLightfv(GL_LIGHT7, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    glEnable(GL_LIGHT7)

    # đèn trần: ánh sáng ấm, càng xa càng yếu (suy giảm theo khoảng cách)
    for i in range(len(ROOMS)):
        lid = _light_id(i)
        glLightfv(lid, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
        glLightfv(lid, GL_DIFFUSE, [1.0, 0.92, 0.75, 1.0])
        glLightfv(lid, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glLightf(lid, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(lid, GL_LINEAR_ATTENUATION, 0.08)
        glLightf(lid, GL_QUADRATIC_ATTENUATION, 0.03)


def apply_lights():
    """Gọi MỖI FRAME, SAU camera.apply(): đặt vị trí đèn rồi bật/tắt theo trạng thái.
    Vị trí đèn bị nhân với ma trận ModelView hiện tại, nên phải đặt sau gluLookAt
    thì đèn mới đứng yên trong thế giới (không dính theo camera)."""
    glLightfv(GL_LIGHT7, GL_POSITION, [1.0, 2.0, 1.0, 0.0])   # w=0: đèn song song
    for i in range(len(ROOMS)):
        lid = _light_id(i)
        x, y, z = _bulb_position(i)
        glLightfv(lid, GL_POSITION, [x, y, z, 1.0])           # w=1: đèn điểm
        if lights_on[i]:
            glEnable(lid)
        else:
            glDisable(lid)


def find_room(cam):
    """Trả về chỉ số phòng người chơi đang đứng, hoặc None nếu ở ngoài nhà."""
    floor = 0 if cam.feet_y < FLOOR_SPLIT else 1
    for i, (_, x0, x1, z0, z1, f) in enumerate(ROOMS):
        if f == floor and x0 <= cam.x < x1 and z0 <= cam.z < z1:
            return i
    return None


def toggle_room_light(cam):
    """Phím L: đảo trạng thái đèn của phòng đang đứng."""
    i = find_room(cam)
    if i is None:
        return
    lights_on[i] = not lights_on[i]
    print(f"Den phong #{i + 1}: {'BAT' if lights_on[i] else 'TAT'}")


def draw_bulbs():
    """Vẽ bóng đèn hình cầu. Tắt chiếu sáng khi vẽ để bóng tự 'phát sáng'."""
    glDisable(GL_LIGHTING)
    for i in range(len(ROOMS)):
        x, y, z = _bulb_position(i)
        if lights_on[i]:
            glColor3f(1.0, 0.95, 0.7)    # sáng
        else:
            glColor3f(0.35, 0.35, 0.35)  # xám khi tắt
        glPushMatrix()
        glTranslatef(x, y, z)            # dời hệ tọa độ tới vị trí bóng đèn
        draw_sphere(0.12, 12, 12)
        glPopMatrix()
    glEnable(GL_LIGHTING)