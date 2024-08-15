import pygame
import math
import random

pygame.init()

# Define colors
white = (255, 255, 255)
grey = (125, 125, 125)
blue = (0, 0, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
pink = (255, 200, 200)
black = (0, 0, 0)

# Define dimensions and frame rate
fps = 60
X = 1000
Y = 1000

# Create display surface
display_surface = pygame.display.set_mode((X, Y))

# Set window title
pygame.display.set_caption('Game')

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Create the player triangle
player_size = 50
player_surface = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
# Define the points of the triangle with the point facing upward
player_points = [(player_size // 2, 0), (0, player_size), (player_size, player_size)]
pygame.draw.polygon(player_surface, yellow, player_points)

# Score variable
score = 0

# Font for rendering the score, health, and game over message
font = pygame.font.SysFont('Arial', 30)

# Player health
player_health = 3

# Flag to check if the game is over
game_over = False

# Wave variables
wave_number = 1
wave_duration = 10000  # x/1000 seconds per wave
wave_timer = 0
enemy_spawn_timer = 0
enemy_spawn_interval = 1000  # x/1000 seconds between each enemy spawn
min_enemy_spawn_interval = 100

def get_angle_to_mouse(player_center, mouse_pos):
    # Calculate the angle between the player center and mouse position
    dx = mouse_pos[0] - player_center[0]
    dy = mouse_pos[1] - player_center[1]
    angle = math.degrees(math.atan2(dy, dx))  # Adjust to correct for the inverted y-axis
    return angle

class Bullet:
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle
        self.speed = 10  # Speed of the bullet

    def move(self):
        # Move the bullet in the direction of its angle
        self.pos[0] += self.speed * math.cos(math.radians(self.angle))
        self.pos[1] += self.speed * math.sin(math.radians(self.angle))

    def draw(self, surface):
        pygame.draw.circle(surface, pink, (int(self.pos[0]), int(self.pos[1])), 5)

    def collides_with(self, enemy):
        # Check if the bullet collides with the enemy
        bullet_rect = pygame.Rect(self.pos[0] - 5, self.pos[1] - 5, 10, 10)
        enemy_rect = pygame.Rect(enemy.pos[0], enemy.pos[1], enemy.size, enemy.size)
        return bullet_rect.colliderect(enemy_rect)

class Enemy:
    def __init__(self, pos, player_center, size=50, speed=2, color=green, health=1):
        self.pos = pos
        self.size = size
        self.color = color
        self.speed = speed
        self.health = health
        self.angle = get_angle_to_mouse(pos, player_center)

    def move(self):
        # Move the enemy towards the player
        self.pos[0] += self.speed * math.cos(math.radians(self.angle))
        self.pos[1] += self.speed * math.sin(math.radians(self.angle))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (int(self.pos[0]), int(self.pos[1]), self.size, self.size))

# List to hold all bullets
bullets = []

# List to hold all enemies
enemies = []

# Function to spawn an enemy at a random position on the edge of the screen
def spawn_enemy(player_center):
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    if edge == 'top':
        pos = [random.randint(0, X), 0]
    elif edge == 'bottom':
        pos = [random.randint(0, X), Y]
    elif edge == 'left':
        pos = [0, random.randint(0, Y)]
    elif edge == 'right':
        pos = [X, random.randint(0, Y)]
    
    # Randomly choose an enemy type with wave difficulty scaling
    enemy_type = random.choice(['regular', 'small_fast', 'large_tanky'])
    if enemy_type == 'regular':
        enemies.append(Enemy(pos, player_center, speed=2 + wave_number * 0.2, health=1 + wave_number // 5))
    elif enemy_type == 'small_fast':
        enemies.append(Enemy(pos, player_center, size=25, speed=4 + wave_number * 0.3, color=blue, health=1))
    elif enemy_type == 'large_tanky':
        enemies.append(Enemy(pos, player_center, size=75, speed=1 + wave_number * 0.1, color=red, health=3 + wave_number // 3))

# Function to render the score on the screen
def draw_score(surface, score):
    score_surface = font.render(f'Score: {score}', True, black)
    surface.blit(score_surface, (10, 10))

# Function to render the wave timer on the screen
def draw_wave_timer(surface, time_left):
    timer_surface = font.render(f'Time Left: {time_left:.1f}', True, black)
    surface.blit(timer_surface, (X - timer_surface.get_width() - 10, 10))

# Function to render the player health on the screen
def draw_health(surface, health):
    health_surface = font.render(f'Health: {health}', True, black)
    surface.blit(health_surface, (X - health_surface.get_width() - 10, 40))

# Function to display game over screen
def display_game_over(surface):
    game_over_surface = font.render('Game Over! Press R to Restart', True, red)
    surface.blit(game_over_surface, (X // 2 - game_over_surface.get_width() // 2, Y // 2))

# Function to reset the game
def reset_game():
    global score, player_health, bullets, enemies, wave_number, wave_timer, enemy_spawn_timer, enemy_spawn_interval, game_over
    score = 0
    player_health = 3  # Reset player health to initial value
    bullets = []
    enemies = []
    wave_number = 1
    wave_timer = 0
    enemy_spawn_timer = 0
    enemy_spawn_interval = 1000  # Reset to initial spawn interval
    game_over = False

# Function to shoot bullets
def shoot_bullets(player_center, mouse_pos, number_of_bullets):
    angle = get_angle_to_mouse(player_center, mouse_pos)
    spread_angle = 10  # Angle between multiple bullets

    if number_of_bullets == 1:
        angles = [angle]
    elif number_of_bullets == 2:
        angles = [angle - spread_angle / 2, angle + spread_angle / 2]
    elif number_of_bullets == 3:
        angles = [angle - spread_angle, angle, angle + spread_angle]

    for angle in angles:
        bullet_start_pos = [
            player_center[0] + (player_size // 2) * math.cos(math.radians(angle)),
            player_center[1] + (player_size // 2) * math.sin(math.radians(angle))
        ]
        bullets.append(Bullet(bullet_start_pos, angle))

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:  # Left-click
            player_center = (X // 2, Y // 2)
            mouse_pos = pygame.mouse.get_pos()

            if score >= 50:
                shoot_bullets(player_center, mouse_pos, 3)
            elif score >= 20:
                shoot_bullets(player_center, mouse_pos, 2)
            else:
                shoot_bullets(player_center, mouse_pos, 1)
                
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    # Check if the game is over
    if game_over:
        display_surface.fill(grey)
        display_game_over(display_surface)
        pygame.display.update()
        continue

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Calculate the angle to rotate the player
    player_center = (X // 2, Y // 2)
    angle = get_angle_to_mouse(player_center, mouse_pos)

    # Rotate the player image
    rotated_player_surface = pygame.transform.rotate(player_surface, -angle - 90)  # Negative angle to rotate correctly, minus 90 degrees

    # Get the new rect for the rotated image and set its center
    rotated_rect = rotated_player_surface.get_rect(center=player_center)

    # Fill the display surface with grey
    display_surface.fill(grey)

    # Draw the rotated player image
    display_surface.blit(rotated_player_surface, rotated_rect.topleft)

    # Move and draw bullets
    for bullet in bullets:
        bullet.move()
        bullet.draw(display_surface)

    # Move and draw enemies
    enemies_to_remove = []
    for enemy in enemies:
        enemy.move()
        enemy.draw(display_surface)

        # Check if the enemy collides with the player
        player_rect = pygame.Rect(player_center[0] - player_size // 2, player_center[1] - player_size // 2, player_size, player_size)
        enemy_rect = pygame.Rect(enemy.pos[0], enemy.pos[1], enemy.size, enemy.size)
        if player_rect.colliderect(enemy_rect):
            player_health -= 1
            enemies_to_remove.append(enemy)
            if player_health <= 0:
                game_over = True

    # Remove enemies that collided with the player
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)

    # Check for bullet-enemy collisions
    bullets_to_remove = []
    for bullet in bullets:
        for enemy in enemies:
            if bullet.collides_with(enemy):
                bullets_to_remove.append(bullet)
                enemy.health -= 1  # Decrease enemy health
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 1  # Increase score when an enemy is destroyed
                    if score % 10 == 0:
                        player_health += 1  # Increase player health by x every multiple of y score

    # Remove bullets that collided with enemies
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)

    # Remove bullets that are out of the screen
    bullets = [bullet for bullet in bullets if 0 <= bullet.pos[0] <= X and 0 <= bullet.pos[1] <= Y]

    # Wave and enemy spawn management
    wave_timer += clock.get_time()
    enemy_spawn_timer += clock.get_time()

    if enemy_spawn_timer >= enemy_spawn_interval:
        spawn_enemy(player_center)
        enemy_spawn_timer = 0

    if wave_timer >= wave_duration:
        wave_number += 1
        wave_timer = 0
        enemy_spawn_interval = max(min_enemy_spawn_interval, enemy_spawn_interval - 100)  # Decrease spawn interval to increase difficulty

    # Draw the score
    draw_score(display_surface, score)

    # Draw the wave timer
    time_left = (wave_duration - wave_timer) / 1000  # Convert milliseconds to seconds
    draw_wave_timer(display_surface, time_left)

    # Draw the player's health
    draw_health(display_surface, player_health)

    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(fps)
