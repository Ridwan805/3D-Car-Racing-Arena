from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time
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
weather_state = "day"  # Can be "day", "night", or "rainy"
rain_drops = []
bullets = []
enemies = []
obstacles = []
score= 10
boost_active = False
boost_timer = 0
boost_duration_frames = 120  # ~2 seconds at 60fps

cheat_mode_2 = False  # Make sure cheat_mode_2 is defined here
passive_cheat_mode = False  # Make sure passive_cheat_mode is defined here
cheat_mode_2_start_time = 0  # Initialize start time for cheat mode 2
passive_cheat_start_time = 0
traps = []

# Global variable initialization
enemy_movement_started = False  # Set to False initially to prevent movement
enemy_movement_timer = 0  # Initialize enemy movement timer
cheat_mode= False

def draw_traps():
    for trap in traps:
        glPushMatrix()
        glTranslatef(trap['x'], 0.5, trap['z'])  # Position the trap behind the player
        glColor3f(1.0, 0.0, 0.0)  # Red color for traps
        glutSolidSphere(0.2, 20, 20)  # Draw a red sphere representing a trap
        glPopMatrix()
        
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
        
        # Remove bullet if it's out of bounds
        if abs(bullet['x']) > 50 or abs(bullet['z']) > 50:
            bullets.remove(bullet)

def update_enemies():
    global enemies, bullets, enemy_movement_started, enemy_movement_timer, player_x, player_z, weather_state
    global score, cheat_mode_2, passive_cheat_mode  # Include cheat_mode_2 and passive_cheat_mode in the globals

    if not enemy_movement_started:
        return

    enemy_speed = 0.02 if weather_state != "rainy" else 0.035
    enemy_movement_timer += 1

    for i, enemy in enumerate(enemies[:] ):
        if enemy_movement_timer % 8 == 0:
            dx = random.uniform(-enemy_speed, enemy_speed)
            dz = 0.05

            new_x = enemy['x'] + dx
            new_z = enemy['z'] + dz

            # Check obstacle collision
            if not any(abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5 for ox, oy, oz in obstacles):
                if -15 <= new_x <= 15 and -45 <= new_z <= 45:
                    enemies[i]['x'] = new_x
                    enemies[i]['z'] = new_z

        # If Cheat Mode 2 (passive mode) is active, handle collisions and score increment
        if cheat_mode_2:  # Player is invisible, enemies won't shoot or move towards player
            dist_to_enemy = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
            if dist_to_enemy < 1.2:  # Player collides with enemy within a threshold range
                enemies.pop(i)  # Remove the enemy from the list
                score += 1  # Increase score for destroying enemy
                print(f"Enemy destroyed by passive mode! Score: {score}")
                respawn_enemy(enemy)  # Respawn the enemy
                continue  # Move to the next enemy
        
        # Check if enemy collides with traps
        for trap in traps[:]:
            dist_to_trap = math.sqrt((enemy['x'] - trap['x'])**2 + (enemy['z'] - trap['z'])**2)
            if dist_to_trap < 1.0:  # If the enemy is near the trap (within a certain distance)
                print(f"Enemy fell into the trap! Score: {score}")
                enemies.pop(i)  # Remove the enemy
                traps.remove(trap)  # Remove the trap
                score += 1  # Increase the score
                respawn_enemy(enemy)  # Respawn the enemy
                break
                
        # Shooting logic (only if Cheat Mode 2 is NOT active)
        if not cheat_mode_2:
            dist_to_player = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
            current_time = time.time()
            if dist_to_player < 10:  # Shoot at the player if they are within range
                if 'last_shot_time' not in enemy:
                    enemy['last_shot_time'] = current_time
                if current_time - enemy['last_shot_time'] >= 1:
                    dx = player_x - enemy['x']
                    dz = player_z - enemy['z']
                    length = math.sqrt(dx**2 + dz**2)
                    if length != 0:
                        dx /= length
                        dz /= length
                        bullets.append({
                            'x': enemy['x'], 'y': 0.5, 'z': enemy['z'],
                            'dx': dx * 0.1, 'dz': dz * 0.1,
                            'type': 'enemy'
                        })
                    enemy['last_shot_time'] = current_time

        # Collision detection with player bullets (check only player bullets)
        for bullet in bullets[:]:
            if bullet.get('type', 'player') == 'player':  # Check only player bullets
                if abs(bullet['x'] - enemy['x']) < 1 and abs(bullet['z'] - enemy['z']) < 1:
                    print("Enemy destroyed by player bullet.")
                    enemies.pop(i)
                    bullets.remove(bullet)
                    spawn_x = random.uniform(-10, 10)
                    spawn_z = random.uniform(-45, -35)
                    enemies.insert(i, {'x': spawn_x, 'z': spawn_z, 'angle': 0, 'y': 0.5})
                    break



# Respawn enemy at the bottom of the track
def respawn_enemy(enemy):
    spawn_x = random.uniform(-10, 10)
    spawn_z = random.uniform(-45, -35)  # Start at the bottom horizontal line
    enemy.update({'x': spawn_x, 'y': 0.5, 'z': spawn_z, 'angle': 0})  # Reset enemy position
    print(f"Enemy respawned at x: {spawn_x}, z: {spawn_z}")

                
def generate_rain():
    rain_drops = []
    for _ in range(100):  # Generate 100 raindrops
        x = random.uniform(-15, 15)
        z = random.uniform(-45, 45)
        y = random.uniform(5, 10)  # Start the rain from the top of the screen
        rain_drops.append({'x': x, 'y': y, 'z': z})
    return rain_drops

def draw_rain():
    global rain_drops
    if weather_state == "rainy":
        glColor3f(0.7, 0.7, 1.0)  # Light blue color for rain
        glBegin(GL_LINES)
        for raindrop in rain_drops:
            glVertex3f(raindrop['x'], raindrop['y'], raindrop['z'])
            glVertex3f(raindrop['x'], raindrop['y'] - 1, raindrop['z'])  # Rain drops fall down
        glEnd()

        # Update rain drops to fall
        for raindrop in rain_drops:
            raindrop['y'] -= 0.1  # Move raindrop downward
            if raindrop['y'] < -45:  # If raindrop goes below the track, reset it
                raindrop['y'] = random.uniform(5, 10)


# Function to update car and enemy speeds when it's rainy
def update_car_speed():
    global player_speed, enemy_movement_timer, weather_state, boost_active
    if weather_state == "rainy":
        player_speed = 0.8  # Increase player speed in rainy weather
        enemy_movement_timer = max(0.4, enemy_movement_timer)  # Speed up enemy movement
    else:
        player_speed = 0.3  # Normal speed
        enemy_movement_timer = 0.8  # Normal enemy speed
            
def keyboardListener(key, x, y):
    global player_x, player_z, player_angle
    global enemy_movement_started, weather_state, rain_drops
    global cheat_mode, boost_active, boost_timer, player_speed
    global cheat_mode_2, cheat_mode_2_start_time

    rot_step = 2
    base_speed = player_speed  # Use player_speed as the base speed

    # Apply weather-based speed adjustments
    if weather_state == "rainy":
        base_speed *= 1.5
    if cheat_mode:
        base_speed *= 0.5
    

    dx = base_speed * math.sin(math.radians(player_angle))
    dz = base_speed * math.cos(math.radians(player_angle))

    def is_colliding(new_x, new_z):
        for ox, oy, oz in obstacles:
            if abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5:
                return True
        return False

    if key == b'w':  # Move forward
        enemy_movement_started = True
        new_x = player_x + dx
        new_z = player_z + dz
        if -15 < new_x < 15 and -45 < new_z < 45 and not is_colliding(new_x, new_z):
            player_x = new_x
            player_z = new_z

    elif key == b's':  # Move backward
        new_x = player_x - dx
        new_z = player_z - dz
        if -15 < new_x < 15 and -45 < new_z < 45 and not is_colliding(new_x, new_z):
            player_x = new_x
            player_z = new_z

    elif key == b'a':  # Rotate left
        player_angle += rot_step
    elif key == b'd':  # Rotate right
        player_angle -= rot_step
    elif key == b'1':  # Set weather to day
        weather_state = "day"
    elif key == b'2':  # Set weather to night
        weather_state = "night"
    elif key == b'3':  # Set weather to rainy
        weather_state = "rainy"
        rain_drops = generate_rain()
    elif key == b'c' or key == b'C':  # Toggle cheat mode
        cheat_mode = not cheat_mode
        print(f"Cheat mode {'ON' if cheat_mode else 'OFF'}")
        
    if score >= 10 and key == b'b' and not cheat_mode_2:
        cheat_mode_2 = True
        cheat_mode_2_start_time = time.time()  # Start timer for cheat mode 2
        print("Cheat mode 2 activated: Player is invisible to enemies!")

    # Deactivate Cheat Mode 2 after 5 seconds
    if cheat_mode_2 and time.time() - cheat_mode_2_start_time > 5:
        cheat_mode_2 = False
        print("Cheat mode 2 deactivated.")
    if key == b't':  # Player places a trap
        trap_x = player_x - 1.0  # Positioning behind the player (adjust distance as needed)
        trap_z = player_z + 1.0  # Slightly behind in the Z direction
        traps.append({'x': trap_x, 'z': trap_z})  # Store 
        
    glutPostRedisplay()


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
        # Fire a bullet from the player car
        dx = 0.5 * math.sin(math.radians(player_angle))
        dz = 0.5 * math.cos(math.radians(player_angle))
        bullet = {'x': player_x + dx, 'y': 0.5, 'z': player_z + dz, 'dx': dx, 'dz': dz}
        bullets.append(bullet)
        print("Player Bullet Fired!")

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Toggle between first-person and third-person views
        camera_view = "first_person" if camera_view == "third_person" else "third_person"
        print(f"Camera view switched to {camera_view}")


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
    global enemies, bullets, missed_bullets, life, game_over, score, cheat_mode
    global player_x, player_z, player_angle  # Ensure these are referenced globally

    

    if cheat_mode:
        # Auto-drive towards the closest enemy
        closest_enemy = min(enemies, key=lambda enemy: math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2), default=None)
        if closest_enemy:
            # Move player towards the closest enemy
            dx = closest_enemy['x'] - player_x
            dz = closest_enemy['z'] - player_z
            angle_to_enemy = math.atan2(dz, dx)
            player_angle = math.degrees(angle_to_enemy)
            
            move_step = 0.2  # Regular speed
            player_x += move_step * math.cos(angle_to_enemy)
            player_z += move_step * math.sin(angle_to_enemy)
            
            # Auto-fire at the closest enemy
            dist_to_enemy = math.sqrt((player_x - closest_enemy['x'])**2 + (player_z - closest_enemy['z'])**2)
            if dist_to_enemy < 10:
                dx = closest_enemy['x'] - player_x
                dz = closest_enemy['z'] - player_z
                length = math.sqrt(dx**2 + dz**2)
                if length != 0:
                    dx /= length  # Normalize direction
                    dz /= length
                    bullets.append({
                        'x': player_x, 'y': 0.5, 'z': player_z,
                        'dx': dx * 0.2, 'dz': dz * 0.2
                    })

    update_bullets()
    update_enemies()  # Update enemy movement and shooting
    glutPostRedisplay()  # Request a redraw
   
    glutPostRedisplay()




def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Set background color based on weather state
    if weather_state == "day":
        glClearColor(1.0, 1.0, 0.0, 1.0)  # Yellow for day
    elif weather_state == "night":
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black for night
    elif weather_state == "rainy":
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black for rainy (night time effect)

    # Camera setup
    setupCamera()

    # Draw the track, obstacles, player car, and enemy cars
    draw_track()
    draw_obstacle()
    draw_player_car()
    draw_enemy_car()

    # Draw rain if the weather is rainy
    draw_rain()
    draw_traps()
    # Draw bullets and other objects
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