from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

# Player attributes
player_life = 10
player_bullets_left = 20
player_bullet_limit = 20
player_bullets_fired = 0

game_over = False
game_won = False
enemy_won = False

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
weather_state = "day"  # Can be "day", "night", or "rainy"
rain_drops = []
bullets = []
enemies = []
obstacles = []
score = 10
boost_active = False
boost_timer = 0  # Tracks time since boost started
boost_duration = 120  # 2 seconds at 60 FPS (120 frames)
boost_active = False  # Flag to indicate if the boost is active
boost_multiplier = 2  # Boost multiplier (increase speed by 2x)
boost_duration_frames = 120  # ~2 seconds at 60fps

# Global variable initialization
enemy_movement_started = False  # Set to False initially to prevent movement
enemy_movement_timer = 0  # Initialize enemy movement timer
cheat_mode = False
cheat_mode_2 = False  # Cheat Mode 2 (Invisible Player)
passive_cheat_mode = False
cheat_mode_2_start_time = 0  # Initialize start time for cheat mode 2
traps = []
is_playing = True

def zone_check(x1, y1, x2, y2):
    # checks in which zone the current point is at
    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) >= abs(dy): 
        if dx >= 0 and dy >= 0:
            return 0 #zone 0
        elif dx >= 0 and dy <= 0:
            return 7 #zone 7
        elif dx <= 0 and dy >= 0:
            return 3 #zone 3
        elif dx <= 0 and dy <= 0:
            return 4 #zone 4
    else:
        if dx >= 0 and dy >= 0:
            return 1 #zone 1
        elif dx >= 0 and dy <= 0:
            return 6 #zone 6
        elif dx <= 0 and dy >= 0:
            return 2 #zone 2
        elif dx <= 0 and dy <= 0:
            return 5 #zone 5

def zone_m_to_zone_zero(x1, y1, x2, y2, zone):
    #converts any other zone points to zone 0
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
    #coverts the zone 0 to its original zone
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
    zone = zone_check(x1, y1, x2, y2) #finds the zone 
    x1, y1, x2, y2 = zone_m_to_zone_zero(x1, y1, x2, y2, zone)#convert the mth zone coordinates to zone 0
    
    dx = x2 - x1
    dy = y2 - y1
    d = (2 * dy) - dx
    incE = 2 * dy #East
    incNE = 2 * (dy - dx) #North East
    x, y = x1, y1
    glPointSize(3)
    glBegin(GL_POINTS)
    while x <= x2:  #X2 always increases
        conX, conY = zone_zero_to_zone_m(x, y, zone) #converts back the 0th zone to original zone 
        
        glVertex2f(conX, conY)
        if d >= 0: # pixel moves to north east
            d += incNE
            y += 1
        else: # pixel moves to east
            d += incE
        x += 1
    glEnd()

def draw_quit(a, b):
    glColor3f(1, 0, 0)
    midpoint_line(a - 15, b - 15, a + 15, b + 15)
    midpoint_line(a - 15, b + 15, a + 15, b - 15)

def draw_back(a, b):
    glColor3f(0, 0, 1)
    midpoint_line(a + 25, b, a - 15, b)  # horizontal line
    midpoint_line(a + 5, b + 15, a - 15, b)  # upper
    midpoint_line(a + 5, b - 15, a - 15, b)  # lower

def draw_pause_play(a, b):
    if is_playing == True:  # unpause
        glColor3f(0.0, 1.0, 0.0)
        midpoint_line(a - 10, b + 15, a - 10, b - 15)
        midpoint_line(a + 10, b + 15, a + 10, b - 15)
    else:  # pause
        glColor3f(1.0, 0.75, 0.0)
        midpoint_line(a - 10, b + 15, a - 10, b - 15)
        midpoint_line(a - 10, b + 15, a + 10, b)  # up
        midpoint_line(a - 10, b - 15, a + 10, b)  # below

def draw_buttons():
    # Adjust these coordinates to make sure buttons are within the window area
    draw_quit(1000 - 50, 750)  # Position button closer to the center
    draw_back(50, 750)  # Adjust positioning
    draw_pause_play(500, 750)  # Adjust positioning

def restart_game():
    global player_x, player_z, player_life, player_bullets_fired, score, game_over, is_playing, enemy_won
    global bullets, enemies, traps, cheat_mode, weather_state, rain_drops
    global player_angle, camera_angle_h, camera_height, camera_view, player_y, weather_state,enemy_movement_started,enemy_movement_timer
    # Reset the game variables
    player_x = 0.0
    player_z = -45.0
    player_y = 0.0 
    player_life = 10
    player_bullets_fired = 0
    score = 0
    game_over = False
    is_playing = True  # Start the game again
    camera_view = "third_person"
    camera_angle_h = 0
    camera_height = 10
    player_angle = 0.0
    weather_state = "day" 
    enemy_movement_started = False  # Set to False initially to prevent movement
    enemy_movement_timer = 0 
    # Reset game objects (e.g., bullets, enemies, traps)
    bullets = []
    enemies = []  # You may want to re-initialize enemies here, depending on your logic
    traps = []

    # Reset cheat mode and weather state
    cheat_mode = False
    weather_state = "day"  # Default to "day"
    rain_drops = []
    enemy_won = False
    # Respawn enemies
    respawn_enemy()  # Call to respawn all enemies
     
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
        glTranslatef(trap['x'], 0.5, trap['z'])  # Position the trap behind the player
        glColor3f(1.0, 0.0, 0.0)  # Red color for traps
        glutSolidSphere(0.2, 20, 20)  # Draw a red sphere representing a trap
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
        safe_dist = 2.0
        used_x = [player_x]   # start by reserving the player’s x
        for _ in range(2):
            # pick a random x that's at least safe_dist from everyone else
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
    global bullets, obstacles
    for bullet in bullets[:]:
        bullet['x'] += bullet['dx']
        bullet['z'] += bullet['dz']
        
        # Check for collision with obstacles
        for obstacle in obstacles[:]:
            if (abs(bullet['x'] - obstacle[0]) < 1.5 and
                abs(bullet['z'] - obstacle[2]) < 1.5):
                # Remove the bullet
                bullets.remove(bullet)
                # Remove the obstacle
                obstacles.remove(obstacle)
                print(f"Obstacle hit! New obstacle will appear.")
                # Add a new obstacle
                spawn_new_obstacle()
                break  # Stop checking for collisions once the bullet is removed
        
        # Remove bullet if it's out of bounds
        if abs(bullet['x']) > 50 or abs(bullet['z']) > 50:
            bullets.remove(bullet)

def spawn_new_obstacle():
    # Randomly place a new obstacle within a specific range
    new_obstacle = (random.uniform(-15, 15), 0.0, random.uniform(45, -45))
    obstacles.append(new_obstacle)
    print(f"New obstacle spawned at {new_obstacle}")
    
def update_enemies():
    global enemies, bullets, enemy_movement_started, enemy_movement_timer, enemy_won, game_won
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

            # Check obstacle collision
            if not any(abs(new_x - ox) < 1.5 and abs(new_z - oz) < 1.5 for ox, oy, oz in obstacles):
                if -15 <= new_x <= 15 and -45 <= new_z <= 45:
                    enemies[i]['x'] = new_x
                    enemies[i]['z'] = new_z

        # --- ENEMY SHOOTING ---
        if cheat_mode_2:  # Player is invisible, enemies won't shoot or move towards player
            dist_to_enemy = math.sqrt((player_x - enemy['x'])**2 + (player_z - enemy['z'])**2)
            if dist_to_enemy < 1.2:  # Player collides with enemy within a threshold range
                enemies.pop(i)  # Remove the enemy from the list
                score += 1  # Increase score for destroying enemy
                print(f"Enemy destroyed by passive mode! Score: {score}")
                respawn_enemy()  # Respawn the enemy
                continue  # Move to the next enemy
        for trap in traps[:]:
            dist_to_trap = math.sqrt((enemy['x'] - trap['x'])**2 + (enemy['z'] - trap['z'])**2)
            if dist_to_trap < 1.0:  # If the enemy is near the trap (within a certain distance)
                print(f"Enemy fell into the trap! Score: {score}")
                enemies.pop(i)  # Remove the enemy
                traps.remove(trap)  # Remove the trap
                score += 1  # Increase the score
                respawn_enemy()  # Respawn the enemy
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

        # --- CHECK ENEMY BULLET HITS PLAYER ---
        for bullet in bullets[:]:
            if bullet.get('type') == 'enemy':
                if abs(bullet['x'] - player_x) < 1 and abs(bullet['z'] - player_z) < 1:
                    bullets.remove(bullet)
                    player_life -= 1
                    print(f"Player hit! Life left: {player_life}")
                    if player_life <= 0:
                        game_over = True
                        print("Game Over: Player lost all lives.")

        # --- CHECK PLAYER BULLET HITS ENEMY ---
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

        # --- CHECK ENEMY REACHES TOP LINE ---
        for enemy in enemies:
            if enemy['z'] >= 44 and not game_won:
                enemy_won = True
                game_over = True
                print("Game Over: Enemy reached finish line!")
                return

def respawn_enemy():
    global enemies  # Ensure the global enemies list is used

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

def keyboardListener(key, x, y):
    global player_x, player_z, player_angle, enemy_won
    global enemy_movement_started, weather_state, rain_drops,cheat_mode_2_start_time, cheat_mode_2
    global cheat_mode, boost_active, boost_timer, player_speed
    global player_bullet_limit, player_bullets_fired, game_over, game_won, enemies

    if game_over or game_won  or enemy_won:
        return  # prevent movement if game ended

    rot_step = 2
    base_speed = 0.3

    # Adjust speed based on weather
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
        if key == b' ' and not boost_active:  # Activate boost when spacebar is pressed
            boost_active = True
            boost_timer = 0  # Reset the boost timer
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
            
            for enemy in enemies: 
                if enemy['z'] >= 44:
                    enemy_won = True
                    game_over = True
                    return
                

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
                boost_timer = 120  # ~2 seconds
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
            traps.append({'x': trap_x, 'z': trap_z})  # Store : trap_z})  # Store trap 
        
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
    global camera_view, bullets, player_bullets_fired, player_bullet_limit, game_over, is_playing, enemy_won
    y = 800 - y 
    

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if (500-10)<= x <=(500+10) and (750  -15) <= y <= (750 +15): #when pause/resume is pressed
            is_playing = not is_playing
            
        print(x,y)
        if (950-15)<= x <=(950+15) and (750 -15) <= y <= (750 +15): #when quit is pressed 
            print('Goodbye! Score:', score)
            glutLeaveMainLoop()
        if (30) <= x <= (80) and (750 -15) <= y <= (750 + 15):  # Restart
            print('Restarting the game...')
            restart_game()
        if enemy_won:
            return
        if is_playing == False or game_over : 
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
                game_over = True  # too many bullets fired



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
    global enemies, bullets, game_over, score, cheat_mode
    global player_x, player_z, player_angle
    global boost_active, boost_timer, game_won, enemy_won
    global player_bullets_fired, player_bullet_limit
    global enemy_movement_started
    global boost_active, boost_timer, boost_duration, player_speed

    if boost_active:
        boost_timer += 1
        if boost_timer >= boost_duration:
            boost_active = False  # End the boost after the specified duration
            print("Boost ended.")
    
    # Update player speed if boost is active
    if boost_active:
        player_speed = 0.3 * boost_multiplier  # Increase speed by the multiplier (2x)
    else:
        player_speed = 0.3  # Default speed
    

    if game_over == True or game_won == True or enemy_won == True:
        return  # Stop updates
    if is_playing == False: # Codition happens then pause
        return  
    if cheat_mode and enemies:
            # 1) pick the closest enemy
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
                


        # BOOST TIMER CHECK
        if boost_active:
            boost_timer += 1
            if boost_timer >= boost_duration_frames:
                boost_active = False
                boost_timer = 0
                print("Boost ended.")

    # Check win condition
    if player_z >= 45:
        game_won = True
        print("Player reached top line. YOU WIN!")
        return
    # Check if enemy reached top first
    for enemy in enemies:
        if enemy['z'] >= 44:
            game_over = True
            print("Enemy reached top line before player. GAME OVER!")
            return 
        
    update_bullets()
    update_enemies()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Set background color based on weather
    if weather_state == "day":
        glClearColor(1.0, 1.0, 0.0, 1.0)  # Yellow
    elif weather_state == "night":
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black
    elif weather_state == "rainy":
        glClearColor(0.0, 0.0, 0.2, 1.0)  # Deep Blue

    setupCamera()
    draw_track()
    draw_obstacle()
    draw_player_car()
    draw_enemy_car()
    draw_rain()
    draw_traps()
    draw_bullets()
    
    iterate()

    # Draw buttons in 2D after 3D scene
    draw_buttons()

    # ----------------- On-screen Text -----------------
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # Match the window size
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Top-left info (white text)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 150)  # Current position is at the top
    for ch in f"Bullets Left: {max(0, player_bullet_limit - player_bullets_fired)}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glRasterPos2f(10, 100)  # Current position is at the top
    for ch in f"Lives Left: {player_life}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glRasterPos2f(10, 50)  # Current position is at the top
    for ch in f"Score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    # Top-right message (game over or win)
    if enemy_won:
        glColor3f(1, 0, 0)
        glRasterPos2f(760, 50)
        for ch in "PLAYER LOSES!":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    elif game_over:
        glColor3f(1, 0, 0)
        glRasterPos2f(800, 50)
        for ch in "GAME OVER":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    elif game_won:
        glColor3f(0, 1, 0)
        glRasterPos2f(780, 50)
        for ch in "PLAYER WINS!":
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
    glOrtho(0.0, 1000, 0.0, 800, -1.0, 1.0)  # Fix this line, make the Z range -1 to 1 for 2D drawing
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
