import pygame
import random  # Нужно для случайных координат монетки

pygame.init()

# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('my first game')

# Цвета (RGB)
BG_COLOR = (30, 30, 30)
PLAYER_COLOR = (255, 0, 0)       # Красный игрок
COIN_COLOR = (255, 215, 0)       # Желтая монетка
ENEMY_COLOR = (0, 100, 255)      # Синий враг
TEXT_COLOR = (255, 255, 255)     # Белый текст

# Игрок
x = 375
y = 275
width = 50
height = 50
speed = 5

# Монетка (размером 30x30, случайное появление)
coin_size = 30
coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
coin_y = random.randint(0, SCREEN_HEIGHT - coin_size)

# Враг (размером 40x40)
enemy_x = 100
enemy_y = 100
enemy_size = 40
enemy_speed = 2

# Очки и шрифт
score = 0
font = pygame.font.SysFont(None, 36)

runing = True
while runing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runing = False

    # --- 1. УПРАВЛЕНИЕ ИГРОКОМ ---
    keys = pygame.key.get_pressed()

    if (keys[pygame.K_LEFT] or keys[pygame.KSCAN_A]) and x > 0:
        x = x - speed
    if (keys[pygame.K_RIGHT] or keys[pygame.KSCAN_D]) and x < SCREEN_WIDTH - width:
        x = x + speed
    if (keys[pygame.K_UP] or keys[pygame.KSCAN_W]) and y > 0:
        y = y - speed
    if (keys[pygame.K_DOWN] or keys[pygame.KSCAN_S]) and y < SCREEN_HEIGHT - height:
        y = y + speed

    # --- 2. ЛОГИКА ВРАГА (следует за игроком) ---
    if enemy_x < x:
        enemy_x += enemy_speed
    elif enemy_x > x:
        enemy_x -= enemy_speed

    if enemy_y < y:
        enemy_y += enemy_speed
    elif enemy_y > y:
        enemy_y -= enemy_speed

    # Pygame Rect объекты для легкой проверки столкновений
    player_rect = pygame.Rect(x, y, width, height)
    coin_rect = pygame.Rect(coin_x, coin_y, coin_size, coin_size)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)

    # --- 3. ПРОВЕРКА СТОЛКНОВЕНИЙ ---
    # Взяли монетку
    if player_rect.colliderect(coin_rect):
        score += 1
        coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
        coin_y = random.randint(0, SCREEN_HEIGHT - coin_size)

    # Враг поймал игрока
    if player_rect.colliderect(enemy_rect):
        score = 0  # Сбрасываем счет
        x, y = 375, 275  # Возвращаем игрока в центр
        enemy_x,enemy_y = 100, 100

    # --- 4. ОТРИСОВКА ---
    window.fill(BG_COLOR)

    # Рисуем объекты
    pygame.draw.rect(window, COIN_COLOR, coin_rect)
    pygame.draw.rect(window, ENEMY_COLOR, enemy_rect)
    pygame.draw.rect(window, PLAYER_COLOR, player_rect)

    # Рисуем счет
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    window.blit(score_text, (10, 10))

    pygame.display.update()
    pygame.time.Clock().tick(60)  # Стабильные 60 FPS

pygame.quit()