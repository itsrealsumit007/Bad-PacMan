import pygame
import random
import math

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 40
PAC_SPEED = 4
ENEMY_SPEED = 3
POWERUP_TIME = 300

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pac-Man Game")
game_clock = pygame.time.Clock()

class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 15
        self.movement = [0, 0]
        self.score = 0
        self.lives = 3
        self.is_powered = False
        self.power_timer = 0
        self.is_chomping = True
        self.chomp_angle = 45
        self.anim_tick = 0

    def update_position(self, maze_walls):
        next_x = self.x + (self.movement[0] * PAC_SPEED)
        next_y = self.y + (self.movement[1] * PAC_SPEED)
        
        can_move = True
        for wall in maze_walls:
            if wall.check_collision(next_x, next_y):
                can_move = False
                break
        
        if can_move:
            if 0 <= next_x <= WINDOW_WIDTH:
                self.x = next_x
            if 0 <= next_y <= WINDOW_HEIGHT:
                self.y = next_y

        self.anim_tick += 1
        if self.anim_tick % 10 == 0:
            self.is_chomping = not self.is_chomping

    def draw_pacman(self):
        if self.is_chomping:
            start_angle = 0
            end_angle = 360
        else:
            if self.movement == [-1, 0]:
                start_angle = 135
                end_angle = 405
            elif self.movement == [1, 0]:
                start_angle = -45
                end_angle = 225
            elif self.movement == [0, -1]:
                start_angle = 45
                end_angle = 315
            else:
                start_angle = 225
                end_angle = 495

        pygame.draw.arc(game_window, YELLOW, 
                       (self.x - self.size, self.y - self.size, 
                        self.size * 2, self.size * 2),
                       math.radians(start_angle), math.radians(end_angle))

class Enemy:
    def __init__(self, x, y, color, chase_style):
        self.x = x
        self.y = y
        self.size = 15
        self.color = color
        self.chase_style = chase_style
        self.movement = [1, 0]
        self.is_scared = False
        self.speed = ENEMY_SPEED
        self.spawn_point = (x, y)
        self.is_scatter = False
        self.scatter_tick = 0
        self.in_house = True
        self.exit_timer = random.randint(30, 180) 

    def chase_player(self, player, maze_walls):
        self.exit_timer -= 1
        
        if self.in_house and self.exit_timer <= 0:
            if self.y > 250:  
                self.y -= self.speed
            else:
                self.in_house = False
            return

        if not self.in_house:
            if self.is_scatter:
                self.scatter_tick += 1
                if self.scatter_tick > 180:
                    self.is_scatter = False
                    self.scatter_tick = 0
                target_x = random.randint(0, WINDOW_WIDTH)
                target_y = random.randint(0, WINDOW_HEIGHT)
            else:
                if self.chase_style == "chase":
                    target_x, target_y = player.x, player.y
                elif self.chase_style == "ambush":
                    target_x = player.x + player.movement[0] * 100
                    target_y = player.y + player.movement[1] * 100
                elif self.chase_style == "patrol":
                    target_x = (player.x + WINDOW_WIDTH/2) % WINDOW_WIDTH
                    target_y = (player.y + WINDOW_HEIGHT/2) % WINDOW_HEIGHT

            current_speed = self.speed / 2 if self.is_scared else self.speed
            
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance != 0:
                dx = dx/distance * current_speed
                dy = dy/distance * current_speed

            next_x = self.x + dx
            next_y = self.y + dy

            can_move = True
            for wall in maze_walls:
                if wall.check_collision(next_x, next_y):
                    can_move = False
                    break

            if can_move:
                if 0 <= next_x <= WINDOW_WIDTH:
                    self.x = next_x
                if 0 <= next_y <= WINDOW_HEIGHT:
                    self.y = next_y

    def respawn(self):
        self.x, self.y = self.spawn_point
        self.is_scared = False
        self.in_house = True
        self.exit_timer = random.randint(30, 180)
        self.scatter_tick = 0
        self.is_scatter = False

    def draw_enemy(self):
        color = BLUE if self.is_scared else self.color
        pygame.draw.circle(game_window, color, (int(self.x), int(self.y)), self.size)

class Dot:
    def __init__(self, x, y, is_powerup=False):
        self.x = x
        self.y = y
        self.size = 8 if is_powerup else 4
        self.exists = True
        self.is_powerup = is_powerup

    def draw_dot(self):
        if self.exists:
            color = BLUE if self.is_powerup else WHITE
            pygame.draw.circle(game_window, color, (int(self.x), int(self.y)), self.size)

class MazeWall:
    def __init__(self, x, y, width, height):
        self.wall = pygame.Rect(x, y, width, height)

    def draw_wall(self):
        pygame.draw.rect(game_window, BLUE, self.wall)

    def check_collision(self, x, y):
        return self.wall.collidepoint(x, y)

def build_maze():
    maze_walls = []
    wall_layout = [
        (100, 100, 600, 20),  
        (100, 100, 20, 400),  
        (100, 500, 600, 20),  
        (700, 100, 20, 400),  
        (150, 200, 200, 20),  
        (450, 200, 200, 20),  
        (150, 400, 200, 20),  
        (450, 400, 200, 20), 
        (530, 250, 20, 120),   
        (350, 250, 20, 100),  
        (430, 250, 20, 100),  
        (350, 350, 100, 20), 
    ]
    
    for wall in wall_layout:
        maze_walls.append(MazeWall(*wall))
    return maze_walls

def create_dots(maze_walls):
    dots = []
    power_dots = []
    
    for x in range(150, 650, 30):
        for y in range(150, 450, 30):
            valid_spot = True
            test_dot = Dot(x, y)
            
            for wall in maze_walls:
                if wall.check_collision(x, y):
                    valid_spot = False
                    break
                    
            if valid_spot:
                dots.append(test_dot)
    
    
    power_dot_positions = [
        (130, 130),  
        (670, 130),   
        (130, 470),   
        (670, 470)  
    ]
    
    for pos in power_dot_positions:
        power_dots.append(Dot(pos[0], pos[1], True))
    
    return dots, power_dots

def init_game():
    pacman = PacMan(120, 120)
    maze_walls = build_maze()
    enemies = [
        Enemy(385, 280, RED, "chase"),     
        Enemy(385, 280, PINK, "ambush"),   
        Enemy(385, 310, ORANGE, "patrol"), 
        Enemy(385, 310, PURPLE, "chase")   
    ]
    dots, power_dots = create_dots(maze_walls)
    for enemy in enemies:
        enemy.respawn()
    return pacman, maze_walls, enemies, dots, power_dots

pacman, maze_walls, enemies, dots, power_dots = init_game()

game_over = False
victory = False
game_active = True

while game_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_active = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                pacman.movement = [-1, 0]
            elif event.key == pygame.K_RIGHT:
                pacman.movement = [1, 0]
            elif event.key == pygame.K_UP:
                pacman.movement = [0, -1]
            elif event.key == pygame.K_DOWN:
                pacman.movement = [0, 1]
            elif event.key == pygame.K_SPACE and (game_over or victory):
                pacman, maze_walls, enemies, dots, power_dots = init_game()
                game_over = False
                victory = False

    if not game_over and not victory:
        pacman.update_position(maze_walls)
        
        if pacman.is_powered:
            pacman.power_timer += 1
            if pacman.power_timer >= POWERUP_TIME:
                pacman.is_powered = False
                pacman.power_timer = 0
                for enemy in enemies:
                    enemy.is_scared = False

        for enemy in enemies:
            enemy.chase_player(pacman, maze_walls)
            distance = math.sqrt((enemy.x - pacman.x)**2 + (enemy.y - pacman.y)**2)
            if distance < (enemy.size + pacman.size):
                if pacman.is_powered:
                    enemy.respawn()
                    pacman.score += 200
                else:
                    pacman.lives -= 1
                    if pacman.lives <= 0:
                        game_over = True
                    else:
                        pacman.x = WINDOW_WIDTH // 2
                        pacman.y = WINDOW_HEIGHT // 2
                        pacman.movement = [0, 0]
                        for ghost in enemies:
                            ghost.respawn()

        for dot in dots:
            if dot.exists:
                distance = math.sqrt((dot.x - pacman.x)**2 + (dot.y - pacman.y)**2)
                if distance < (dot.size + pacman.size):
                    dot.exists = False
                    pacman.score += 10

        for power_dot in power_dots:
            if power_dot.exists:
                distance = math.sqrt((power_dot.x - pacman.x)**2 + (power_dot.y - pacman.y)**2)
                if distance < (power_dot.size + pacman.size):
                    power_dot.exists = False
                    pacman.is_powered = True
                    pacman.power_timer = 0
                    pacman.score += 50
                    for enemy in enemies:
                        enemy.is_scared = True

        if all(not dot.exists for dot in dots) and all(not pd.exists for pd in power_dots):
            victory = True

    game_window.fill(BLACK)
    
    for wall in maze_walls:
        wall.draw_wall()
    
    for dot in dots:
        dot.draw_dot()
    
    for power_dot in power_dots:
        power_dot.draw_dot()
    
    pacman.draw_pacman()
    
    for enemy in enemies:
        enemy.draw_enemy()

    game_font = pygame.font.Font(None, 36)
    score_display = game_font.render(f'Score: {pacman.score}  Lives: {pacman.lives}', True, WHITE)
    game_window.blit(score_display, (10, 10))

    if game_over:
        game_over_msg = game_font.render('Game Over! Press SPACE to restart', True, RED)
        game_window.blit(game_over_msg, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2))
    
    if victory:
        victory_msg = game_font.render('You Won! Press SPACE to restart', True, YELLOW)
        game_window.blit(victory_msg, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2))

    pygame.display.flip()
    game_clock.tick(60)

pygame.quit()
