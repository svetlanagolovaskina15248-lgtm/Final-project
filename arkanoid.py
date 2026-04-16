import pygame
import sys


# ============================================================
# БЛОК 1. НАСТРОЙКА PYGAME И ОСНОВНЫХ ПАРАМЕТРОВ ИГРЫ
# Здесь мы задаем размеры окна, цвета, скорости и другие
# базовые настройки, которые используются во всей программе.
# ============================================================

pygame.init()

# Размеры игрового окна
WIDTH = 900
HEIGHT = 650

# Заголовок окна
pygame.display.set_caption("Арканоид")

# Создание игрового окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Таймер для ограничения FPS
clock = pygame.time.Clock()
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (70, 130, 255)
RED = (220, 70, 70)
GREEN = (70, 200, 100)
YELLOW = (255, 220, 70)
GRAY = (180, 180, 180)
DARK_BLUE = (30, 40, 90)
PURPLE = (140, 90, 200)
ORANGE = (255, 150, 80)

# Шрифты
font_small = pygame.font.SysFont("arial", 24)
font_medium = pygame.font.SysFont("arial", 34)
font_large = pygame.font.SysFont("arial", 52)


# ============================================================
# БЛОК 2. НАСТРОЙКА ПЛАТФОРМЫ
# Здесь описываются параметры платформы игрока и функции,
# связанные с ее движением и отрисовкой.
# ============================================================

# Размеры платформы
PADDLE_WIDTH = 140
PADDLE_HEIGHT = 18

# Скорость платформы
PADDLE_SPEED = 8

# Начальная позиция платформы
paddle = pygame.Rect(
    WIDTH // 2 - PADDLE_WIDTH // 2,
    HEIGHT - 60,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)


# ============================================================
# БЛОК 3. НАСТРОЙКА МЯЧА
# Здесь создается мяч, задается его размер, скорость и логика
# стартового положения.
# ============================================================

# Радиус мяча
BALL_RADIUS = 10

# Начальная скорость мяча
INITIAL_BALL_SPEED_X = 5
INITIAL_BALL_SPEED_Y = -5
ball_speed_x = INITIAL_BALL_SPEED_X
ball_speed_y = INITIAL_BALL_SPEED_Y

# Позиция мяча
ball_x = WIDTH // 2
ball_y = HEIGHT // 2

# Флаг движения мяча:
# False = мяч стоит на месте до нажатия пробела
# True = мяч летит
ball_moving = False


# ============================================================
# БЛОК 4. НАСТРОЙКА КИРПИЧЕЙ
# Здесь создается набор кирпичей, которые должен разрушить
# игрок. Каждый кирпич будет храниться как прямоугольник.
# ============================================================

BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_WIDTH = 78
BRICK_HEIGHT = 28
BRICK_GAP = 8
BRICK_TOP_OFFSET = 80

# Список кирпичей
bricks = []


def create_bricks():
    """
    Создает новый набор кирпичей.
    Каждый кирпич сохраняется как словарь:
    {
        "rect": прямоугольник кирпича,
        "color": цвет кирпича,
        "points": количество очков за кирпич
    }
    """
    brick_list = []
    colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
    points_by_row = [20, 20, 15, 15, 10, 10]

    total_width = BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP
    start_x = (WIDTH - total_width) // 2

    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
            y = BRICK_TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_GAP)

            brick_rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
            brick_color = colors[row % len(colors)]
            brick_points = points_by_row[row % len(points_by_row)]

            brick_list.append({
                "rect": brick_rect,
                "color": brick_color,
                "points": brick_points
            })

    return brick_list


bricks = create_bricks()


# ============================================================
# БЛОК 5. ИГРОВЫЕ ПЕРЕМЕННЫЕ
# Здесь хранятся очки, жизни, текущее состояние игры и
# вспомогательные флаги.
# ============================================================

score = 0
lives = 3

# Сколько кирпичей уже разрушено
broken_bricks = 0

# Возможные состояния:
# "start"    - стартовый экран
# "play"     - игра идет
# "pause"    - пауза
# "win"      - победа
# "gameover" - поражение
game_state = "start"


# ============================================================
# БЛОК 6. ФУНКЦИЯ СБРОСА ПОЛОЖЕНИЯ МЯЧА И ПЛАТФОРМЫ
# Используется после потери жизни или перезапуска игры.
# ============================================================

def reset_ball_and_paddle():
    """
    Возвращает платформу и мяч в начальное положение.
    Мяч снова будет ждать нажатия пробела.
    """
    global ball_x, ball_y, ball_speed_x, ball_speed_y, ball_moving

    paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
    paddle.y = HEIGHT - 60

    # Мяч ставится на платформу, чтобы старт выглядел естественно
    ball_x = paddle.centerx
    ball_y = paddle.top - BALL_RADIUS

    ball_speed_x = INITIAL_BALL_SPEED_X
    ball_speed_y = INITIAL_BALL_SPEED_Y

    ball_moving = False


# Выставляем стартовое положение мяча сразу на платформу
reset_ball_and_paddle()


# ============================================================
# БЛОК 7. ФУНКЦИЯ ПОЛНОГО ПЕРЕЗАПУСКА ИГРЫ
# Используется при старте новой игры после победы или поражения.
# ============================================================

def reset_game():
    """
    Полностью перезапускает игру:
    - сбрасывает счет
    - восстанавливает жизни
    - создает новые кирпичи
    - возвращает мяч и платформу в начало
    - переводит игру в режим start
    """
    global score, lives, bricks, game_state, broken_bricks

    score = 0
    lives = 3
    broken_bricks = 0
    bricks = create_bricks()
    reset_ball_and_paddle()
    game_state = "start"


# ============================================================
# БЛОК 8. ОТРИСОВКА ТЕКСТА
# Вспомогательная функция для удобного вывода надписей.
# ============================================================

def draw_text(text, font, color, x, y, center=False):
    """
    Рисует текст на экране.
    Если center=True, то координаты считаются центром текста.
    """
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


# ============================================================
# БЛОК 9. ОТРИСОВКА ИГРОВЫХ ОБЪЕКТОВ
# Здесь рисуются фон, платформа, мяч, кирпичи, очки и жизни.
# ============================================================

def draw_game():
    """
    Отрисовывает все основные объекты игры.
    """
    # Фон
    screen.fill(BLACK)

    # Верхняя декоративная полоса
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, WIDTH, 55))

    # Платформа
    pygame.draw.rect(screen, WHITE, paddle, border_radius=8)

    # Мяч
    pygame.draw.circle(screen, YELLOW, (ball_x, ball_y), BALL_RADIUS)

    # Кирпичи
    for brick in bricks:
        pygame.draw.rect(screen, brick["color"], brick["rect"], border_radius=6)
        pygame.draw.rect(screen, WHITE, brick["rect"], 2, border_radius=6)

    # Очки и жизни
    draw_text(f"Очки: {score}", font_small, WHITE, 20, 15)
    draw_text(f"Жизни: {lives}", font_small, WHITE, WIDTH - 120, 15)


# ============================================================
# БЛОК 10. ЭКРАНЫ СОСТОЯНИЙ ИГРЫ
# Здесь выводятся стартовый экран, экран победы и поражения.
# ============================================================

def draw_start_screen():
    """
    Рисует стартовый экран перед началом игры.
    """
    screen.fill(BLACK)
    draw_text("АРКАНОИД", font_large, WHITE, WIDTH // 2, 170, center=True)
    draw_text("Управление: стрелки влево / вправо", font_medium, GRAY, WIDTH // 2, 250, center=True)
    draw_text("Пробел — запуск мяча", font_medium, GRAY, WIDTH // 2, 300, center=True)
    draw_text("P — пауза", font_medium, GRAY, WIDTH // 2, 350, center=True)
    draw_text("Разбей все кирпичи и не дай мячу упасть вниз", font_small, WHITE, WIDTH // 2, 410, center=True)
    draw_text("Нажми ENTER, чтобы начать", font_medium, YELLOW, WIDTH // 2, 490, center=True)


def draw_pause_screen():
    """
    Рисует экран паузы поверх игрового поля.
    """
    draw_game()
    draw_text("ПАУЗА", font_large, YELLOW, WIDTH // 2, HEIGHT // 2 - 20, center=True)
    draw_text("Нажми P, чтобы продолжить", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 40, center=True)


def draw_win_screen():
    """
    Рисует экран победы.
    """
    screen.fill(BLACK)
    draw_text("ПОБЕДА!", font_large, GREEN, WIDTH // 2, 220, center=True)
    draw_text(f"Ваш счет: {score}", font_medium, WHITE, WIDTH // 2, 300, center=True)
    draw_text("Нажми R, чтобы сыграть снова", font_medium, YELLOW, WIDTH // 2, 400, center=True)


def draw_gameover_screen():
    """
    Рисует экран поражения.
    """
    screen.fill(BLACK)
    draw_text("ИГРА ОКОНЧЕНА", font_large, RED, WIDTH // 2, 220, center=True)
    draw_text(f"Ваш счет: {score}", font_medium, WHITE, WIDTH // 2, 300, center=True)
    draw_text("Нажми R, чтобы начать заново", font_medium, YELLOW, WIDTH // 2, 400, center=True)


# ============================================================
# БЛОК 11. УПРАВЛЕНИЕ ПЛАТФОРМОЙ
# Функция считывает нажатия клавиш и двигает платформу по
# экрану, не давая ей выходить за границы окна.
# ============================================================

def move_paddle():
    """
    Двигает платформу влево или вправо по нажатию клавиш.
    """
    global ball_x, ball_y

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        paddle.x -= PADDLE_SPEED

    if keys[pygame.K_RIGHT]:
        paddle.x += PADDLE_SPEED

    # Ограничение по границам окна
    if paddle.left < 0:
        paddle.left = 0

    if paddle.right > WIDTH:
        paddle.right = WIDTH

    # Пока мяч не запущен, он движется вместе с платформой
    if not ball_moving:
        ball_x = paddle.centerx
        ball_y = paddle.top - BALL_RADIUS


# ============================================================
# БЛОК 12. ДВИЖЕНИЕ МЯЧА
# Здесь мяч перемещается по экрану согласно своей скорости.
# ============================================================

def move_ball():
    """
    Перемещает мяч, если он запущен.
    """
    global ball_x, ball_y

    if ball_moving:
        ball_x += ball_speed_x
        ball_y += ball_speed_y


# ============================================================
# БЛОК 13. СТОЛКНОВЕНИЕ МЯЧА СО СТЕНАМИ
# Здесь обрабатывается отражение мяча от левой, правой и
# верхней стен. Нижняя граница означает потерю жизни.
# ============================================================

def handle_wall_collisions():
    """
    Обрабатывает столкновения мяча со стенами.
    Если мяч падает вниз, игрок теряет жизнь.
    """
    global ball_speed_x, ball_speed_y, lives, game_state

    # Отскок от левой стены
    if ball_x - BALL_RADIUS <= 0:
        ball_speed_x = -ball_speed_x

    # Отскок от правой стены
    if ball_x + BALL_RADIUS >= WIDTH:
        ball_speed_x = -ball_speed_x

    # Отскок от верхней стены
    if ball_y - BALL_RADIUS <= 55:
        ball_speed_y = -ball_speed_y

    # Падение мяча вниз
    if ball_y + BALL_RADIUS >= HEIGHT:
        lives -= 1

        if lives > 0:
            reset_ball_and_paddle()
            game_state = "play"
        else:
            game_state = "gameover"


# ============================================================
# БЛОК 14. СТОЛКНОВЕНИЕ МЯЧА С ПЛАТФОРМОЙ
# Мяч отскакивает вверх, а направление по X слегка меняется
# в зависимости от того, в какую часть платформы он попал.
# ============================================================

def handle_paddle_collision():
    """
    Проверяет столкновение мяча с платформой.
    """
    global ball_y, ball_speed_y, ball_speed_x

    ball_rect = pygame.Rect(
        ball_x - BALL_RADIUS,
        ball_y - BALL_RADIUS,
        BALL_RADIUS * 2,
        BALL_RADIUS * 2
    )

    if ball_rect.colliderect(paddle) and ball_speed_y > 0:
        # Ставим мяч прямо над платформой, чтобы он не застревал в ней
        ball_y = paddle.top - BALL_RADIUS

        # Отражаем мяч вверх
        ball_speed_y = -abs(ball_speed_y)

        # Вычисляем отклонение от центра платформы
        paddle_center = paddle.centerx
        difference = ball_x - paddle_center

        # Меняем горизонтальную скорость в зависимости от места удара
        ball_speed_x = int(difference / 18)

        # Чтобы мяч не летел строго вертикально слишком часто
        if ball_speed_x == 0:
            ball_speed_x = 1


# ============================================================
# БЛОК 15. СТОЛКНОВЕНИЕ МЯЧА С КИРПИЧАМИ
# При попадании в кирпич мяч отражается, кирпич удаляется,
# а игрок получает очки.
# ============================================================

def handle_brick_collision():
    """
    Проверяет столкновение мяча с кирпичами.
    Если столкновение найдено:
    - удаляет кирпич
    - прибавляет очки
    - меняет направление мяча
    """
    global ball_speed_x, ball_speed_y, score, game_state, broken_bricks

    ball_rect = pygame.Rect(
        ball_x - BALL_RADIUS,
        ball_y - BALL_RADIUS,
        BALL_RADIUS * 2,
        BALL_RADIUS * 2
    )

    for brick in bricks[:]:
        brick_rect = brick["rect"]

        if ball_rect.colliderect(brick_rect):
            overlap_left = ball_rect.right - brick_rect.left
            overlap_right = brick_rect.right - ball_rect.left
            overlap_top = ball_rect.bottom - brick_rect.top
            overlap_bottom = brick_rect.bottom - ball_rect.top

            min_overlap_x = min(overlap_left, overlap_right)
            min_overlap_y = min(overlap_top, overlap_bottom)

            # Определяем, был удар скорее сбоку или сверху/снизу
            if min_overlap_x < min_overlap_y:
                ball_speed_x = -ball_speed_x
            else:
                ball_speed_y = -ball_speed_y

            bricks.remove(brick)
            score += brick["points"]
            broken_bricks += 1

            # Каждые 5 разбитых кирпичей немного ускоряем мяч
            if broken_bricks % 5 == 0:
                if ball_speed_x > 0:
                    ball_speed_x += 1
                else:
                    ball_speed_x -= 1

                if ball_speed_y > 0:
                    ball_speed_y += 1
                else:
                    ball_speed_y -= 1

            break

    # Если все кирпичи уничтожены — победа
    if len(bricks) == 0:
        game_state = "win"


# ============================================================
# БЛОК 16. ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
# Это главная часть программы. Здесь постоянно:
# - обрабатываются события
# - обновляется положение объектов
# - перерисовывается экран
# ============================================================

running = True

while running:
    clock.tick(FPS)

    # --------------------------------------------------------
    # ОБРАБОТКА СОБЫТИЙ
    # Здесь программа реагирует на закрытие окна и нажатия клавиш.
    # --------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Запуск игры со стартового экрана
            if game_state == "start" and event.key == pygame.K_RETURN:
                game_state = "play"

            # Запуск мяча пробелом
            if game_state == "play" and event.key == pygame.K_SPACE:
                ball_moving = True

            # Пауза и снятие с паузы
            if event.key == pygame.K_p:
                if game_state == "play":
                    game_state = "pause"
                elif game_state == "pause":
                    game_state = "play"

            # Перезапуск после победы или поражения
            if game_state in ("win", "gameover") and event.key == pygame.K_r:
                reset_game()

    # --------------------------------------------------------
    # ЛОГИКА ИГРЫ В СОСТОЯНИИ "play"
    # Выполняется только тогда, когда игра активна.
    # --------------------------------------------------------
    if game_state == "play":
        move_paddle()
        move_ball()
        handle_wall_collisions()
        handle_paddle_collision()
        handle_brick_collision()
        draw_game()

        # Подсказка, пока мяч не запущен
        if not ball_moving:
            draw_text("Нажми ПРОБЕЛ, чтобы запустить мяч", font_small, WHITE, WIDTH // 2, HEIGHT // 2 + 40, center=True)

    # --------------------------------------------------------
    # ОТРИСОВКА СТАРТОВОГО ЭКРАНА
    # --------------------------------------------------------
    elif game_state == "start":
        draw_start_screen()

    # --------------------------------------------------------
    # ОТРИСОВКА ПАУЗЫ
    # --------------------------------------------------------
    elif game_state == "pause":
        draw_pause_screen()

    # --------------------------------------------------------
    # ОТРИСОВКА ЭКРАНА ПОБЕДЫ
    # --------------------------------------------------------
    elif game_state == "win":
        draw_win_screen()

    # --------------------------------------------------------
    # ОТРИСОВКА ЭКРАНА ПОРАЖЕНИЯ
    # --------------------------------------------------------
    elif game_state == "gameover":
        draw_gameover_screen()

    # Обновление изображения на экране
    pygame.display.flip()

# Корректное завершение программы
pygame.quit()
sys.exit()
