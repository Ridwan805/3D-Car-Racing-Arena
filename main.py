from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

# Player attributes
player_x = 0.0
player_y = 0.0
player_z = -45.0
player_speed = 0.3
player_angle = 0.0
camera_view = "third_person"
camera_angle_h = 0
camera_height = 10
enemy_movement_started = False
enemy_movement_timer = 0

bullets = []
enemies = []
obstacles = []

def draw_track():
    glPushMatrix()
    column_colors = [(0.3, 0.3, 0.3), (0.0, 0.0, 0.0)]
    track_width = 30
    column_width = 5
    num_columns = track_width // column_width

    for i in range(-num_columns // 2, num_columns // 2 + 1):
        if i == -num_columns // 2 or i == num_columns // 2:
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_LINES)
            glVertex3f(i * column_width, 0, 50)
            glVertex3f(i * column_width, 0, -50)
            glEnd()
        else:
            glColor3f(*column_colors[i % 2])
            glBegin(GL_QUADS)
            glVertex3f(i * column_width, 0, 50)
            glVertex3f((i + 1) * column_width, 0, 50)
            glVertex3f((i + 1) * column_width, 0, -50)
            glVertex3f(i * column_width, 0, -50)
            glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(-track_width / 2, 0.01, 45)
    glVertex3f(track_width / 2, 0.01, 45)
    glVertex3f(-track_width / 2, 0.01, -45)
    glVertex3f(track_width / 2, 0.01, -45)
    glEnd()
    glPopMatrix()

def draw_obstacle():
    global obstacles
    if not obstacles:
        # Removed 2 obstacles for better enemy/player navigation
        obstacles = [
            (-10, 0.0, -30), (-10, 0.0, 10), 
            (10, 0.0, -20), (0, 0.0, 0),
            (13, 0.0, -15), (13, 0.0, -5)
        ]

    for x, y, z in obstacles:
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.5, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(-1.0, 0, -1.0)
        glVertex3f(1.0, 0, -1.0)
        glVertex3f(0, 2.0, 0)
        glVertex3f(1.0, 0, -1.0)
        glVertex3f(1.0, 0, 1.0)
        glVertex3f(0, 2.0, 0)
        glVertex3f(1.0, 0, 1.0)
        glVertex3f(-1.0, 0, 1.0)
        glVertex3f(0, 2.0, 0)
        glVertex3f(-1.0, 0, 1.0)
        glVertex3f(-1.0, 0, -1.0)
        glVertex3f(0, 2.0, 0)
        glEnd()
        glPopMatrix()

def draw_player_car():
    glPushMatrix()
    glTranslatef(player_x, 0.5, player_z)
    glRotatef(player_angle, 0, 1, 0)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCube(1.0)
    glTranslatef(0.0, 0.0, 0.6)
    glColor3f(0.0, 1.0, 0.0)
    glutSolidCube(0.5)
    glPopMatrix()

def draw_enemy_car():
    global enemies
    if not enemies:
        for _ in range(2):
            ex = random.uniform(-10, 10)
            ez = random.uniform(-45, -35)  # Start below the horizontal line
            enemies.append({'x': ex, 'z': ez, 'angle': 0, 'y': 0.5})

    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy['x'], enemy['y'], enemy['z'])
        glRotatef(enemy['angle'], 0, 1, 0)

        # Back side - blue
        glColor3f(0.0, 0.0, 1.0)
        glutSolidCube(1.0)

        # Front side - purple (slightly forward)
        glTranslatef(0.0, 0.0, 0.6)
        glColor3f(0.5, 0.0, 1.0)
        glutSolidCube(0.5)

        glPopMatrix()


def draw_bullets():
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet['x'], bullet['y'], bullet['z'])
        glColor3f(1.0, 1.0, 0.0)
        glutSolidSphere(0.2, 20, 20)
        glPopMatrix()

def update_bullets():
    global bullets
    for bullet in bullets[:]:
        bullet['x'] += bullet['dx']
        bullet['z'] += bullet['dz']
        if abs(bullet['x']) > 50 or abs(bullet['z']) > 50:
            bullets.remove(bullet)

def update_enemies():
    global enemies, bullets, enemy_movement_started, enemy_movement_timer, player_x, player_z

    if not enemy_movement_started:
        return

    enemy_movement_timer += 1  # Slow down enemy movement

    for enemy in enemies[:]:
        if enemy_movement_timer % 8 == 0:  # Move every 8 frames
            # Try small random side movement (zigzag)
            possible_steps = [(-0.05, 0.1), (0.0, 0.1), (0.05, 0.1)]
            random.shuffle(possible_steps)

            for dx, dz in possible_steps:
                new_x = enemy['x'] + dx
                new_z = enemy['z'] + dz

                # Check collision with obstacles
                blocked = False
                for ox, oy, oz in obstacles:
                    if abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5:
                        blocked = True
                        break

                if not blocked and -15 <= new_x <= 15 and -45 <= new_z <= 45:
                    enemy['x'] = new_x
                    enemy['z'] = new_z
                    break

        # Shoot bullet at player if close
        dist_to_player = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
        if dist_to_player < 10:
            dx = player_x - enemy['x']
            dz = player_z - enemy['z']
            length = math.sqrt(dx**2 + dz**2)
            if length != 0:
                dx /= length
                dz /= length
                bullets.append({
                    'x': enemy['x'], 'y': 0.5, 'z': enemy['z'],
                    'dx': dx * 0.2, 'dz': dz * 0.2
                })

        # Collision with player car
        if dist_to_player < 1.2:
            enemies.remove(enemy)
            # Respawn a new enemy at the bottom of the track
            spawn_x = random.uniform(-10, 10)
            spawn_z = random.uniform(-45, -35)
            enemies.append({'x': spawn_x, 'y': 0.5, 'z': spawn_z, 'angle': 0})


        # Check if player is near
        dist = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
        if dist < 10:
            dx = player_x - enemy['x']
            dz = player_z - enemy['z']
            length = math.sqrt(dx**2 + dz**2)
            if length != 0:
                dx /= length
                dz /= length
                bullets.append({
                    'x': enemy['x'], 'y': 0.5, 'z': enemy['z'],
                    'dx': dx * 0.2, 'dz': dz * 0.2
                })


            
def keyboardListener(key, x, y):
    global player_x, player_z, player_angle, enemy_movement_started
    move_step = 0.4
    rot_step = 5
    dx = move_step * math.sin(math.radians(player_angle))
    dz = move_step * math.cos(math.radians(player_angle))

    min_x, max_x = -15, 15
    min_z, max_z = -45, 45

    def is_colliding(new_x, new_z):
        for ox, oy, oz in obstacles:
            if abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5:
                return True
        return False

    if key == b'w':
        enemy_movement_started = True
        new_x = player_x + dx
        new_z = player_z + dz
        if min_x < new_x < max_x and min_z < new_z < max_z and not is_colliding(new_x, new_z):
            player_x = new_x
            player_z = new_z
    elif key == b's':
        new_x = player_x - dx
        new_z = player_z - dz
        if min_x < new_x < max_x and min_z < new_z < max_z and not is_colliding(new_x, new_z):
            player_x = new_x
            player_z = new_z
    elif key == b'a':
        player_angle += rot_step
    elif key == b'd':
        player_angle -= rot_step



def specialKeyListener(key, x, y):
    global camera_angle_h, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle_h -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle_h += 5
    elif key == GLUT_KEY_UP:
        camera_height += 1
    elif key == GLUT_KEY_DOWN:
        camera_height = max(2, camera_height - 1)

def mouseListener(button, state, x, y):
    global camera_view, bullets
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        dx = 0.5 * math.sin(math.radians(player_angle))
        dz = 0.5 * math.cos(math.radians(player_angle))
        bullet = {'x': player_x + dx, 'y': 0.5, 'z': player_z + dz, 'dx': dx, 'dz': dz}
        bullets.append(bullet)
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_view = "first_person" if camera_view == "third_person" else "third_person"

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.1, 200)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_view == "third_person":
        cx = player_x - 30 * math.sin(math.radians(camera_angle_h))
        cy = player_y + camera_height
        cz = player_z - 30 * math.cos(math.radians(camera_angle_h))
        gluLookAt(cx, cy, cz, player_x, player_y, player_z, 0, 1, 0)
    else:
        lx = player_x + math.sin(math.radians(player_angle))
        lz = player_z + math.cos(math.radians(player_angle))
        gluLookAt(player_x, player_y + 2, player_z, lx, player_y + 2, lz, 0, 1, 0)

def animate():
    update_bullets()
    update_enemies()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setupCamera()
    draw_track()
    draw_obstacle()
    draw_player_car()
    draw_enemy_car()
    draw_bullets()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Car Racing Arena Final View")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()

if __name__ == "__main__":
    main()
