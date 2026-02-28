import pygame
import sys
import os
import json
import random

WIDTH, HEIGHT = 800, 400
GROUND_Y = 300

# sky and cloud colors
SKY_TOP = (135, 206, 235)
CLOUD_COLOR = (250, 250, 250)
GROUND_COLOR = (210, 180, 120)

BASE_SPEED = 280
BASE_SPAWN = 1.3

DIFFICULTIES = {
    'easy': {'speed_mul': 0.8, 'spawn_mul': 1.25},
    'normal': {'speed_mul': 1.0, 'spawn_mul': 1.0},
    'hard': {'speed_mul': 1.35, 'spawn_mul': 0.75}
}

# hitbox tuning (smaller = more forgiving)
PLAYER_HITBOX_SHRINK = (12, 8)  # (horizontal, vertical) pixels to remove from player rect
OBSTACLE_HITBOX_SHRINK = (6, 4)  # (horizontal, vertical) pixels to remove from obstacle rect

HIGHFILE = 'dino_high.json'

# global cactus sprite (filled in main)
CACTUS_RAW = None

# simple parallax cloud data (filled in main)
clouds = []


def load_highscore():
    if os.path.exists(HIGHFILE):
        try:
            with open(HIGHFILE, 'r', encoding='utf-8') as f:
                return int(json.load(f).get('high', 0))
        except Exception:
            return 0
    return 0


def save_highscore(n):
    try:
        with open(HIGHFILE, 'w', encoding='utf-8') as f:
            json.dump({'high': int(n)}, f)
    except Exception:
        pass


def create_dino_sprite():
    # small 16x16 pixel sprite
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    G = (147, 196, 125)
    O = (56, 118, 29)
    B = (0, 0, 0)
    pixels = []
    outline = [(3,6),(4,5),(5,4),(6,4),(7,4),(8,5),(9,6),(10,6),(11,7),(11,8),(10,9),(9,10),(8,10),(7,10),(6,10),(5,10),(4,9),(3,8)]
    for x,y in outline:
        s.set_at((x,y), O)
    for yy in range(6,10):
        for xx in range(5,10):
            s.set_at((xx,yy), G)
    s.set_at((6,11), G); s.set_at((8,11), G)
    s.set_at((9,6), B)
    return s


def create_cactus_sprite():
    # small 8x12 cactus pixel art
    s = pygame.Surface((8, 12), pygame.SRCALPHA)
    s.fill((0,0,0,0))
    G = (83, 141, 78)
    D = (48, 93, 52)
    # trunk/body pixels
    pixels = [
        (3,0),(4,0),
        (2,1),(3,1),(4,1),(5,1),
        (2,2),(3,2),(4,2),(5,2),
        (1,3),(2,3),(3,3),(4,3),(5,3),(6,3),
        (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),
        (2,5),(3,5),(4,5),(5,5),
        (2,6),(3,6),(4,6),(5,6),
        (3,7),(4,7),
    ]
    for x,y in pixels:
        s.set_at((x,y), G)
    # darker outline/spot
    s.set_at((1,5), D); s.set_at((6,5), D)
    s.set_at((3,3), D)
    return s


class Obstacle:
    def __init__(self, x, w, h, speed):
        self.rect = pygame.Rect(x, GROUND_Y - h, w, h)
        self.speed = speed

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)

    def draw(self, surf):
        # draw pixel cactus scaled to obstacle rect when available
        global CACTUS_RAW
        if CACTUS_RAW:
            try:
                img = pygame.transform.scale(CACTUS_RAW, (max(1, self.rect.w), max(1, self.rect.h)))
                surf.blit(img, (int(self.rect.x), int(self.rect.y)))
            except Exception:
                pygame.draw.rect(surf, (234,234,234), self.rect)
        else:
            pygame.draw.rect(surf, (234,234,234), self.rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Courier', 20)
    small = pygame.font.SysFont('Courier', 16)

    high = load_highscore()

    dino_raw = create_dino_sprite()
    DINO_W, DINO_H = 44, 44
    dino_img = pygame.transform.scale(dino_raw, (DINO_W, DINO_H))
    # create cactus sprite and clouds
    global CACTUS_RAW, clouds
    CACTUS_RAW = create_cactus_sprite()
    # init clouds: [x,y,speed]
    clouds = [ [random.randint(0, WIDTH), random.randint(30,110), random.uniform(10,40)] for _ in range(4) ]

    player = pygame.Rect(80, GROUND_Y - DINO_H, DINO_W, DINO_H)
    vy = 0
    GRAVITY = 1300
    JUMP_V = -470
    grounded = True

    obstacles = []
    spawn_timer = 0
    score = 0.0

    # start state: choose difficulty first, then start
    started = False

    difficulty = 'normal'
    # ensure variables exist for nonlocal in apply_difficulty
    speed = BASE_SPEED
    spawn_interval = BASE_SPAWN
    def apply_difficulty():
        nonlocal speed, spawn_interval
        d = DIFFICULTIES.get(difficulty, DIFFICULTIES['normal'])
        speed = BASE_SPEED * d['speed_mul']
        spawn_interval = BASE_SPAWN * d['spawn_mul']

    apply_difficulty()

    running = True
    game_over = False

    # UI button rects
    btns = {
        'easy': pygame.Rect(20, 12, 80, 28),
        'normal': pygame.Rect(110, 12, 80, 28),
        'hard': pygame.Rect(200, 12, 80, 28)
    }
    start_btn = pygame.Rect(300, 12, 100, 28)

    def start_game():
        nonlocal started, game_over, spawn_timer, score, obstacles, vy, grounded, player
        # reset run state and begin
        obstacles.clear()
        spawn_timer = 0
        score = 0.0
        player.y = GROUND_Y - DINO_H
        vy = 0
        grounded = True
        game_over = False
        started = True

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if started and not game_over:
                        if grounded:
                            vy = JUMP_V; grounded = False
                    # if not started, space does nothing (require Start)
                if event.key == pygame.K_RETURN:
                    if not started:
                        # press Enter to start after choosing difficulty
                        start_game()
                    elif game_over:
                        # after game over, pressing Enter returns to selection (stop) so user can choose difficulty
                        started = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # difficulty buttons only active before starting
                if not started:
                    # compute centered difficulty buttons (match render())
                    db_w, db_h, db_gap = 120, 44, 14
                    total_w = db_w * 3 + db_gap * 2
                    start_x = WIDTH//2 - total_w//2
                    clicked = False
                    for i, key in enumerate(['easy','normal','hard']):
                        r = pygame.Rect(start_x + i*(db_w + db_gap), 160, db_w, db_h)
                        if r.collidepoint(mx, my):
                            difficulty = key; apply_difficulty(); clicked = True; break
                    # big start button
                    big = pygame.Rect(WIDTH//2 - 120, 240, 240, 64)
                    if big.collidepoint(mx, my):
                        start_game(); clicked = True
                    # also allow clicking the small header buttons (legacy)
                    if not clicked:
                        for k, r in btns.items():
                            if r.collidepoint(mx, my):
                                difficulty = k; apply_difficulty(); break
                else:
                    # during play, clicks cause jump
                    if not game_over:
                        if grounded:
                            vy = JUMP_V; grounded = False
                    else:
                        # after game over, click to stop (go back to selection)
                        started = False

        if started and not game_over:
            # physics
            vy += GRAVITY * dt
            player.y += vy * dt
            if player.y >= GROUND_Y - player.height:
                player.y = GROUND_Y - player.height; vy = 0; grounded = True

            # spawn (some obstacles fast, some slow, sometimes overlapping)
            spawn_timer += dt
            if spawn_timer > spawn_interval:
                spawn_timer = 0
                # choose preset sizes
                presets = [ (14,28), (28,40), (40,44) ]
                choice = random.random()
                min_gap = 56  # minimum horizontal gap between obstacles so player can land
                if choice < 0.6:
                    # single obstacle (easy)
                    w,h = random.choice(presets)
                    spd = speed * random.choice([0.9,1.0,1.05])
                    x = WIDTH + 10
                    obstacles.append(Obstacle(x, w, h, spd))
                elif choice < 0.92:
                    # double: guarantee a gap between obstacles (beat-able)
                    w1,h1 = random.choice(presets)
                    w2,h2 = random.choice(presets)
                    base_x = WIDTH + 10
                    # offset2 placed further right so gap >= min_gap
                    offset1 = 0
                    offset2 = w1 + min_gap + random.randint(0, 40)
                    spd1 = speed * random.choice([0.8,0.9,1.0])  # slower or normal
                    spd2 = speed * random.choice([1.0,1.15,1.3])   # normal or faster
                    obstacles.append(Obstacle(base_x + offset1, w1, h1, spd1))
                    obstacles.append(Obstacle(base_x + offset2, w2, h2, spd2))
                else:
                    # triple cluster: space them so there are gaps between each
                    base_x = WIDTH + 10
                    w1,h1 = random.choice(presets)
                    w2,h2 = random.choice(presets)
                    w3,h3 = random.choice(presets)
                    offset1 = 0
                    offset2 = w1 + min_gap + random.randint(0, 30)
                    offset3 = offset2 + w2 + min_gap + random.randint(0, 30)
                    speeds = [speed * 0.8, speed * 1.0, speed * 1.25]
                    obstacles.append(Obstacle(base_x + offset1, w1, h1, speeds[0]))
                    obstacles.append(Obstacle(base_x + offset2, w2, h2, speeds[1]))
                    obstacles.append(Obstacle(base_x + offset3, w3, h3, speeds[2]))

            # update obstacles
            for ob in list(obstacles):
                ob.update(dt)
                if ob.rect.right < -50:
                    obstacles.remove(ob)

            # collisions (use smaller hitboxes for forgiving collisions)
            for ob in obstacles:
                p_hit = player.inflate(-PLAYER_HITBOX_SHRINK[0], -PLAYER_HITBOX_SHRINK[1])
                o_hit = ob.rect.inflate(-OBSTACLE_HITBOX_SHRINK[0], -OBSTACLE_HITBOX_SHRINK[1])
                if p_hit.colliderect(o_hit):
                    game_over = True
                    if int(score) > high:
                        high = int(score); save_highscore(high)

            # score
            score += dt * 10

        # render

        if not started:
            # Start screen: show title, difficulty selection and large Start button
            # start screen: black background and light title
            screen.fill((0,0,0))
            title = pygame.font.SysFont('Courier', 40).render('DINO PIXEL RUN', True, (230,230,230))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

            # draw description
            desc = small.render('Choose difficulty then press START', True, (170,170,170))
            screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 120))

            # draw ground area behind buttons (black on start screen)
            pygame.draw.rect(screen, (0, 0, 0), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

            # centered difficulty buttons
            db_w, db_h, db_gap = 120, 44, 14
            total_w = db_w * 3 + db_gap * 2
            start_x = WIDTH//2 - total_w//2
            for i, key in enumerate(['easy','normal','hard']):
                r = pygame.Rect(start_x + i*(db_w + db_gap), 160, db_w, db_h)
                color = (110,231,183) if key == difficulty else (34,34,34)
                fg = (2,44,34) if key == difficulty else (220,220,220)
                pygame.draw.rect(screen, color, r)
                txt = font.render(key.upper(), True, fg)
                screen.blit(txt, (r.x + 12, r.y + 8))

            # big start button
            big = pygame.Rect(WIDTH//2 - 120, 240, 240, 64)
            pygame.draw.rect(screen, (100,180,140), big)
            st = pygame.font.SysFont('Courier', 32).render('START', True, (2,44,34))
            screen.blit(st, (big.x + big.width//2 - st.get_width()//2, big.y + big.height//2 - st.get_height()//2))

            # small note
            hint = small.render('Space / Click: Jump  ·  Enter: Start', True, (40,60,80))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
        else:
            # game render: ground, player, obstacles, HUD
            # background: sky + clouds (parallax)
            screen.fill(SKY_TOP)
            for c in clouds:
                # cloud shape: two rectangles for pixel feel
                cx = int(c[0])
                cy = int(c[1])
                pygame.draw.rect(screen, CLOUD_COLOR, (cx, cy, 36, 10))
                pygame.draw.rect(screen, CLOUD_COLOR, (cx+8, cy-6, 20, 12))

            # move clouds
            for c in clouds:
                c[0] -= c[2] * dt
                if c[0] < -80:
                    c[0] = WIDTH + random.randint(20, 200)
                    c[1] = random.randint(30, 110)
                    c[2] = random.uniform(10,40)

            # draw ground area (no dark tile strip)
            pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

            # draw player (pixelated)
            screen.blit(dino_img, (int(player.x), int(player.y)))

            # draw obstacles (cacti)
            for ob in obstacles:
                ob.draw(screen)

            # HUD
            score_s = small.render(f'Score: {int(score)}', True, (154,160,166))
            high_s = small.render(f'High: {high}', True, (154,160,166))
            screen.blit(score_s, (WIDTH - 140, 12))
            screen.blit(high_s, (WIDTH - 240, 12))

            # running indicator
            run_s = small.render('RUNNING', True, (140,220,180))
            screen.blit(run_s, (start_btn.x + 6, start_btn.y + 6))

            if game_over:
                go = font.render('GAME OVER - ENTER to return', True, (255,123,123))
                screen.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
