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