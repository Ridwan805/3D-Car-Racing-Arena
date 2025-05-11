from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

player_life = 10
player_bullets_left = 20
player_bullet_limit = 20
player_bullets_fired = 0

game_over = False
game_won = False

player_wins = False
font = GLUT_BITMAP_HELVETICA_18

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
weather_state = "day"
rain_drops = []
bullets = []
enemies = []
obstacles = []
score = 10
boost_active = False
boost_timer = 0
boost_duration = 120
boost_active = False
boost_multiplier = 2
boost_duration_frames = 120


enemy_movement_started = False  
enemy_movement_timer = 0  
cheat_mode = False
cheat_mode_2 = False  
passive_cheat_mode = False
cheat_mode_2_start_time = 0  
traps = []
is_playing = True

def zone_check(x1, y1, x2, y2):
    
    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) >= abs(dy): 
        if dx >= 0 and dy >= 0:
            return 0 
        elif dx >= 0 and dy <= 0:
            return 7 
        elif dx <= 0 and dy >= 0:
            return 3 
        elif dx <= 0 and dy <= 0:
            return 4 
    else:
        if dx >= 0 and dy >= 0:
            return 1 
        elif dx >= 0 and dy <= 0:
            return 6 
        elif dx <= 0 and dy >= 0:
            return 2 
        elif dx <= 0 and dy <= 0:
            return 5 

def zone_m_to_zone_zero(x1, y1, x2, y2, zone):
    
    if zone == 0:
        return x1, y1, x2, y2
    elif zone == 1:
        return y1, x1, y2, x2
    elif zone == 2:
        return y1, -x1, y2, -x2
    elif zone == 3:
        return -x1, y1, -x2, y2
    elif zone == 4:
        return -x1, -y1, -x2, -y2
    elif zone == 5:
        return -y1, -x1, -y2, -x2
    elif zone == 6:
        return -y1, x1, -y2, x2
    elif zone == 7:
        return x1, -y1, x2, -y2
    
def zone_zero_to_zone_m(x,y,zone): 
    
    if zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y
    elif zone == 0:
        return x, y

def midpoint_line(x1, y1, x2, y2):   
    zone = zone_check(x1, y1, x2, y2) 
    x1, y1, x2, y2 = zone_m_to_zone_zero(x1, y1, x2, y2, zone)
    
    dx = x2 - x1
    dy = y2 - y1
    d = (2 * dy) - dx
    incE = 2 * dy 
    incNE = 2 * (dy - dx) 
    x, y = x1, y1
    glPointSize(3)
    glBegin(GL_POINTS)
    while x <= x2: 
        conX, conY = zone_zero_to_zone_m(x, y, zone) 
        
        glVertex2f(conX, conY)
        if d >= 0: 
            d += incNE
            y += 1
        else:
            d += incE
        x += 1
    glEnd()

def draw_quit(a, b):
    glColor3f(1, 0, 0)
    midpoint_line(a - 15, b - 15, a + 15, b + 15)
    midpoint_line(a - 15, b + 15, a + 15, b - 15)

def draw_back(a, b):
    glColor3f(0, 0, 1)
    midpoint_line(a + 25, b, a - 15, b) 
    midpoint_line(a + 5, b + 15, a - 15, b) 
    midpoint_line(a + 5, b - 15, a - 15, b)  

def draw_pause_play(a, b):
    if is_playing == True:  
        glColor3f(0.0, 1.0, 0.0)
        midpoint_line(a - 10, b + 15, a - 10, b - 15)
        midpoint_line(a + 10, b + 15, a + 10, b - 15)
    else:  
        glColor3f(1.0, 0.75, 0.0)
        midpoint_line(a - 10, b + 15, a - 10, b - 15)
        midpoint_line(a - 10, b + 15, a + 10, b) 
        midpoint_line(a - 10, b - 15, a + 10, b)  

def draw_buttons():
    
    draw_quit(1000 - 50, 750)  
    draw_back(50, 750) 
    draw_pause_play(500, 750)  

def restart_game():
    global player_x, player_z, player_life, player_bullets_fired, score, game_over, is_playing
    global bullets, enemies, traps, cheat_mode, weather_state, rain_drops
    global player_angle, camera_angle_h, camera_height, camera_view, player_y, weather_state,enemy_movement_started,enemy_movement_timer
   
    player_x = 0.0
    player_z = -45.0
    player_y = 0.0 
    player_life = 10
    player_bullets_fired = 0
    score = 0
    game_over = False
    is_playing = True 
    camera_view = "third_person"
    camera_angle_h = 0
    camera_height = 10
    player_angle = 0.0
    weather_state = "day" 
    enemy_movement_started = False  
    enemy_movement_timer = 0 
    
    bullets = []
    enemies = []  
    traps = []

    
    cheat_mode = False
    weather_state = "day"  
    rain_drops = []

    
    respawn_enemy()  

       
def draw_text(x, y, text):
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

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

def draw_traps():
    for trap in traps:
        glPushMatrix()
        glTranslatef(trap['x'], 0.5, trap['z'])  
        glColor3f(1.0, 0.0, 0.0)  
        glutSolidSphere(0.2, 20, 20) 
        glPopMatrix()

def draw_obstacle():
    global obstacles
    if not obstacles:
        
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
        safe_dist = 2.0
        used_x = [player_x]   
        for _ in range(2):
            
            while True:
                ex = random.uniform(-10, 10)
                if all(abs(ex - ox) > safe_dist for ox in used_x):
                    break
            used_x.append(ex)
            enemies.append({'x': ex, 'z': -45.0, 'angle': 0, 'y': 0.5})
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy['x'], enemy['y'], enemy['z'])
        glRotatef(enemy['angle'], 0, 1, 0)

        
        glColor3f(0.4, 0.0, 1.0)
        glutSolidCube(1.0)

        
        glTranslatef(0.0, 0.4, 0.6)
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
    global bullets, obstacles
    for bullet in bullets[:]:
        bullet['x'] += bullet['dx']
        bullet['z'] += bullet['dz']
        
       
        for obstacle in obstacles[:]:
            if (abs(bullet['x'] - obstacle[0]) < 1.5 and
                abs(bullet['z'] - obstacle[2]) < 1.5):
                
                bullets.remove(bullet)
                
                obstacles.remove(obstacle)
                print(f"Obstacle hit! New obstacle will appear.")
                
                spawn_new_obstacle()
                break  
        
       
        if abs(bullet['x']) > 50 or abs(bullet['z']) > 50:
            bullets.remove(bullet)

def spawn_new_obstacle():
    
    new_obstacle = (random.uniform(-15, 15), 0.0, random.uniform(-45, -35))
    obstacles.append(new_obstacle)
    print(f"New obstacle spawned at {new_obstacle}")


def update_enemies():
    global enemies, bullets, enemy_movement_started, enemy_movement_timer
    global player_x, player_z, weather_state, player_life, game_over, score

    if not enemy_movement_started or game_over:
        return

    enemy_speed = 0.02 if weather_state != "rainy" else 0.035
    enemy_movement_timer += 1

    for i, enemy in enumerate(enemies[:]):
        if enemy_movement_timer % 8 == 0:
            dx = random.uniform(-enemy_speed, enemy_speed)
            dz = 0.05

            new_x = enemy['x'] + dx
            new_z = enemy['z'] + dz

            
            if not any(abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5 for ox, oy, oz in obstacles):
                if -15 <= new_x <= 15 and -45 <= new_z <= 45:
                    enemies[i]['x'] = new_x
                    enemies[i]['z'] = new_z

        
        if cheat_mode_2: 
            dist_to_enemy = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
            if dist_to_enemy < 1.2:  
                enemies.pop(i)  
                score += 1  
                print(f"Enemy destroyed by passive mode! Score: {score}")
                respawn_enemy()  
                continue  
        for trap in traps[:]:
            dist_to_trap = math.sqrt((enemy['x'] - trap['x'])**2 + (enemy['z'] - trap['z'])**2)
            if dist_to_trap < 1.0:  
                print(f"Enemy fell into the trap! Score: {score}")
                enemies.pop(i)  
                traps.remove(trap) 
                score += 1  
                respawn_enemy()  
                break
                
        if not cheat_mode_2:       
            dist_to_player = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
            current_time = time.time()
            if dist_to_player < 10:
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

        
        for bullet in bullets[:]:
            if bullet.get('type') == 'enemy':
                if abs(bullet['x'] - player_x) < 1 and abs(bullet['z'] - player_z) < 1:
                    bullets.remove(bullet)
                    player_life -= 1
                    print(f"Player hit! Life left: {player_life}")
                    if player_life <= 0:
                        game_over = True
                        print("Game Over: Player lost all lives.")

        
        for bullet in bullets[:]:
            if bullet.get('type') == 'player':
                if abs(bullet['x'] - enemy['x']) < 1 and abs(bullet['z'] - enemy['z']) < 1:
                    print("Enemy destroyed by player bullet.")
                    bullets.remove(bullet)
                    enemies.pop(i)
                    score += 1
                    spawn_x = random.uniform(-10, 10)
                    spawn_z = random.uniform(-45, -35)
                    enemies.insert(i, {'x': spawn_x, 'z': spawn_z, 'angle': 0, 'y': 0.5})
                    break

        
        if enemy['z'] >= 45 and not game_won:
            game_over = True
            print("Game Over: Enemy reached finish line!")
            return

def respawn_enemy():
    global enemies  

    safe_dist = 2.0
    used_x = [player_x]
    for enemy in enemies:
        while True:
            spawn_x = random.uniform(-10, 10)
            if all(abs(spawn_x - ox) > safe_dist for ox in used_x):
                break
        used_x.append(spawn_x)
        enemy.update({'x': spawn_x, 'y': 0.5, 'z': -45.0, 'angle': 0})

def generate_rain():
    rain_drops = []
    for _ in range(100):  
        x = random.uniform(-15, 15)
        z = random.uniform(-45, 45)
        y = random.uniform(5, 10) 
        rain_drops.append({'x': x, 'y': y, 'z': z})
    return rain_drops

def draw_rain():
    global rain_drops
    if weather_state == "rainy":
        glColor3f(0.7, 0.7, 1.0) 
        glBegin(GL_LINES)
        for raindrop in rain_drops:
            glVertex3f(raindrop['x'], raindrop['y'], raindrop['z'])
            glVertex3f(raindrop['x'], raindrop['y'] - 1, raindrop['z']) 
        glEnd()

        
        for raindrop in rain_drops:
            raindrop['y'] -= 0.1 
            if raindrop['y'] < -45:  
                raindrop['y'] = random.uniform(5, 10)

def keyboardListener(key, x, y):
    global player_x, player_z, player_angle
    global enemy_movement_started, weather_state, rain_drops,cheat_mode_2_start_time, cheat_mode_2
    global cheat_mode, boost_active, boost_timer, player_speed
    global player_bullet_limit, player_bullets_fired, game_over, game_won

    if game_over or game_won:
        return  

    rot_step = 2
    base_speed = 0.3

   
    if weather_state == "rainy":
        base_speed *= 1.5
    if cheat_mode:
        base_speed *= 0.5
    if boost_active:
        base_speed *= 5

    dx = base_speed * math.sin(math.radians(player_angle))
    dz = base_speed * math.cos(math.radians(player_angle))

    def is_colliding(new_x, new_z):
        for ox, oy, oz in obstacles:
            if abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5:
                return True
        return False
    
    if is_playing:
        if key == b' ' and not boost_active: 
            boost_active = True
            boost_timer = 0 
            print("Boost activated!")
        if key == b'w':
            enemy_movement_started = True
            new_x = player_x + dx
            new_z = player_z + dz
            if -15 < new_x < 15 and -45 < new_z < 45 and not is_colliding(new_x, new_z):
                player_x = new_x
                player_z = new_z
            if new_z >= 45 and not game_over:
                game_won = True
                

        elif key == b's':
            new_x = player_x - dx
            new_z = player_z - dz
            if -15 < new_x < 15 and -45 < new_z < 45 and not is_colliding(new_x, new_z):
                player_x = new_x
                player_z = new_z
        elif key == b'a':
            player_angle += rot_step
        elif key == b'd':
            player_angle -= rot_step
        elif key == b'1':
            weather_state = "day"
        elif key == b'2':
            weather_state = "night"
        elif key == b'3':
            weather_state = "rainy"
            rain_drops = generate_rain()
        elif key == b'c' or key == b'C':
            cheat_mode = not cheat_mode
        elif key == b' ':
            if player_bullets_fired < player_bullet_limit:
                boost_active = True
                boost_timer = 120 
        if score >= 10 and key == b'b' and not cheat_mode_2:
            cheat_mode_2 = True
            cheat_mode_2_start_time = time.time()  
            print("Cheat mode 2 activated: Player is invisible to enemies!")

    
        if cheat_mode_2 and time.time() - cheat_mode_2_start_time > 5:
            cheat_mode_2 = False
            print("Cheat mode 2 deactivated.")
        if key == b't':  
            trap_x = player_x - 1.0  
            trap_z = player_z + 1.0  
            traps.append({'x': trap_x, 'z': trap_z})  
        
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
    global camera_view, bullets, player_bullets_fired, player_bullet_limit, game_over, is_playing
    y = 800 - y 
    

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if (500-10)<= x <=(500+10) and (750  -15) <= y <= (750 +15): 
            is_playing = not is_playing
            
        print(x,y)
        if (950-15)<= x <=(950+15) and (750 -15) <= y <= (750 +15): 
            print('Goodbye! Score:', score)
            glutLeaveMainLoop()
        if (30) <= x <= (80) and (750 -15) <= y <= (750 + 15):  
            print('Restarting the game...')
            restart_game()
        if is_playing == False or game_over: 
            return
        else:
          if 0 <= x <= 1000 and  0 <= y <= 720:
            if player_bullets_fired < player_bullet_limit:
                dx = 0.5 * math.sin(math.radians(player_angle))
                dz = 0.5 * math.cos(math.radians(player_angle))
                bullet = {
                    'x': player_x + dx, 'y': 0.5, 'z': player_z + dz,
                    'dx': dx, 'dz': dz, 'type': 'player'
                }
                bullets.append(bullet)
                player_bullets_fired += 1
            else:
                game_over = True  



    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        
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
    global player_x, player_z, player_angle
    global boost_active, boost_timer, game_won
    global player_bullets_fired, player_bullet_limit
    global enemy_movement_started
    global boost_active, boost_timer, boost_duration, player_speed

    if boost_active:
        boost_timer += 1
        if boost_timer >= boost_duration:
            boost_active = False  
            print("Boost ended.")
    
    
    if boost_active:
        player_speed = 0.3 * boost_multiplier  
    else:
        player_speed = 0.3  
    

    if game_over or game_won:
        return  
    if is_playing == False: 
        return  

    if cheat_mode:
        
        closest_enemy = min(enemies, key=lambda e: math.sqrt((player_x - e['x'])**2 + (player_z - e['z'])**2), default=None)
        if closest_enemy:
            dx = closest_enemy['x'] - player_x
            dz = closest_enemy['z'] - player_z
            angle_to_enemy = math.atan2(dz, dx)
            player_angle = math.degrees(angle_to_enemy)

            move_step = 0.2  # Slow auto-move
            player_x += move_step * math.cos(angle_to_enemy)
            player_z += move_step * math.sin(angle_to_enemy)

            dist_to_enemy = math.sqrt((player_x - closest_enemy['x'])**2 + (player_z - closest_enemy['z'])**2)
            if dist_to_enemy < 10:
                dx = closest_enemy['x'] - player_x
                dz = closest_enemy['z'] - player_z
                length = math.sqrt(dx**2 + dz**2)
                if length != 0:
                    dx /= length
                    dz /= length
                    bullets.append({
                        'x': player_x, 'y': 0.5, 'z': player_z,
                        'dx': dx * 0.2, 'dz': dz * 0.2,
                        'type': 'player'
                    })
                    player_bullets_fired += 1

    
    if boost_active:
        boost_timer += 1
        if boost_timer >= boost_duration_frames:
            boost_active = False
            boost_timer = 0
            print("Boost ended.")

    
    if player_z >= 45:
        game_won = True
        print("Player reached top line. YOU WIN!")

    
    for enemy in enemies:
        if enemy['z'] >= 45:
            game_over = True
            print("Enemy reached top line before player. GAME OVER!")

    update_bullets()
    update_enemies()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    
    if weather_state == "day":
        glClearColor(1.0, 1.0, 0.0, 1.0)  
    elif weather_state == "night":
        glClearColor(0.0, 0.0, 0.0, 1.0)  
    elif weather_state == "rainy":
        glClearColor(0.0, 0.0, 0.2, 1.0)  

    setupCamera()
    draw_track()
    draw_obstacle()
    draw_player_car()
    draw_enemy_car()
    draw_rain()
    draw_traps()
    draw_bullets()
    
    iterate()

    
    draw_buttons()

    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 150)  
    for ch in f"Bullets Left: {max(0, player_bullet_limit - player_bullets_fired)}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glRasterPos2f(10, 100)  
    for ch in f"Lives Left: {player_life}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glRasterPos2f(10, 50)  
    for ch in f"Score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    
    if game_over:
        glColor3f(1, 0, 0)
        glRasterPos2f(800, 50)
        for ch in "🚨 GAME OVER":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    elif game_won:
        glColor3f(0, 1, 0)
        glRasterPos2f(780, 50)
        for ch in "🏁 PLAYER WINS!":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    # Restore matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glutSwapBuffers()

def iterate():
    glViewport(0, 0, 1000, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1000, 0.0, 800, -1.0, 1.0)  
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
   
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
