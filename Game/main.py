import pygame
import sys
import random
import math

pygame.init()

# ==========================
# WINDOW SETUP
# ==========================
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Challenge")
clock = pygame.time.Clock()

# ==========================
# DEFAULT SETTINGS
# ==========================
default_speed = 5
default_corridor = 200
default_wave_angle = 45

terrain_speed = default_speed
corridor_height = default_corridor
wave_angle_max = default_wave_angle

# ==========================
# PLAYER SETUP
# ==========================
wave_img = pygame.image.load("assets/wave_17.png").convert_alpha()
wave_img = pygame.transform.scale(wave_img, (30, 30))

player_x = 150
player_y = HEIGHT // 2
wave_speed_y = 6
space_held = False

trail = []
trail_length = 40

# ==========================
# TERRAIN SETUP
# ==========================
segment_width = 60
floor_points = []
ceiling_points = []

# Initialize terrain points
for i in range(WIDTH // segment_width + 2):
    x_pos = i * segment_width
    y_floor = random.randint(HEIGHT - 150, HEIGHT - 50)
    y_ceiling = random.randint(50, HEIGHT - corridor_height - 150)
    floor_points.append((x_pos, y_floor))
    ceiling_points.append((x_pos, y_ceiling))

def generate_new_point(last_x, is_floor=True):
    if is_floor:
        new_y = random.randint(HEIGHT - 150, HEIGHT - 50)
    else:
        new_y = random.randint(50, HEIGHT - corridor_height - 150)
    return (last_x + segment_width, new_y)

# ==========================
# MAIN GAME LOOP
# ==========================
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_held = True
            elif event.key == pygame.K_UP:
                terrain_speed += 1
            elif event.key == pygame.K_DOWN:
                terrain_speed = max(1, terrain_speed - 1)
            elif event.key == pygame.K_RIGHT:
                corridor_height = min(HEIGHT - 50, corridor_height + 10)
            elif event.key == pygame.K_LEFT:
                corridor_height = max(50, corridor_height - 10)
            elif event.key == pygame.K_w:
                wave_angle_max = min(75, wave_angle_max + 5)
            elif event.key == pygame.K_s:
                wave_angle_max = max(15, wave_angle_max - 5)
            elif event.key == pygame.K_r:
                terrain_speed = default_speed
                corridor_height = default_corridor
                wave_angle_max = default_wave_angle
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_held = False

    # Wave movement
    if space_held:
        player_y -= wave_speed_y
    else:
        player_y += wave_speed_y

    # Keep inside screen
    player_y = max(0, min(HEIGHT - wave_img.get_height(), player_y))

    # Drawing
    screen.fill((0, 0, 0))

    # Move existing trail left along with terrain
    trail = [(tx - terrain_speed, ty) for (tx, ty) in trail]
    if len(trail) > trail_length:
        trail.pop(0)

    # Compute trail offset based on current wave angle
    angle_rad = math.radians(wave_angle_max if space_held else -wave_angle_max)
    offset_x = math.cos(angle_rad) * 5  # distance from center
    offset_y = -math.sin(angle_rad) * 5  # negative because y-axis goes down

    # Add new trail point at the tip of the wave
    trail.append((
        player_x + wave_img.get_width() // 2 + offset_x,
        player_y + wave_img.get_height() // 2 + offset_y
    ))

    # Draw trail
    for i in range(len(trail) - 1):
        pygame.draw.line(screen, (255, 255, 255), trail[i], trail[i + 1], 8)

    # Move floor and ceiling
    floor_points = [(tx - terrain_speed, ty) for (tx, ty) in floor_points]
    ceiling_points = [(tx - terrain_speed, ty) for (tx, ty) in ceiling_points]

    # Remove old points and add new ones
    if floor_points[0][0] < -segment_width:
        floor_points.pop(0)
        floor_points.append(generate_new_point(floor_points[-1][0], is_floor=True))
    if ceiling_points[0][0] < -segment_width:
        ceiling_points.pop(0)
        ceiling_points.append(generate_new_point(ceiling_points[-1][0], is_floor=False))

    # Collision detection (floor)
    for i in range(len(floor_points) - 1):
        x1, y1 = floor_points[i]
        x2, y2 = floor_points[i + 1]
        if x1 <= player_x <= x2:
            t = (player_x - x1) / (x2 - x1)
            terrain_y = y1 + t * (y2 - y1)
            if player_y + wave_img.get_height() > terrain_y:
                player_x = 150
                player_y = HEIGHT // 2
                floor_points.clear()
                ceiling_points.clear()
                for i in range(WIDTH // segment_width + 2):
                    x_pos = i * segment_width
                    floor_points.append((x_pos, random.randint(HEIGHT - 150, HEIGHT - 50)))
                    ceiling_points.append((x_pos, random.randint(50, HEIGHT - corridor_height - 150)))
                break

    # Collision detection (ceiling)
    for i in range(len(ceiling_points) - 1):
        x1, y1 = ceiling_points[i]
        x2, y2 = ceiling_points[i + 1]
        if x1 <= player_x <= x2:
            t = (player_x - x1) / (x2 - x1)
            terrain_y = y1 + t * (y2 - y1)
            if player_y < terrain_y:
                player_x = 150
                player_y = HEIGHT // 2
                floor_points.clear()
                ceiling_points.clear()
                for i in range(WIDTH // segment_width + 2):
                    x_pos = i * segment_width
                    floor_points.append((x_pos, random.randint(HEIGHT - 150, HEIGHT - 50)))
                    ceiling_points.append((x_pos, random.randint(50, HEIGHT - corridor_height - 150)))
                break

    # Draw floor and ceiling
    pygame.draw.lines(screen, (255, 0, 0), False, floor_points, 4)
    pygame.draw.lines(screen, (255, 0, 0), False, ceiling_points, 4)

    # Draw wave
    angle = wave_angle_max if space_held else -wave_angle_max
    rotated_wave = pygame.transform.rotate(wave_img, angle)
    screen.blit(rotated_wave, (player_x, player_y))

    pygame.display.flip()
    clock.tick(60)