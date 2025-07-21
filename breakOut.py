import pygame
import sys

# --- Constantes ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_SPEED = 7
BALL_SPEED = 5
SLOW_BALL_SPEED = 2  # Velocidad reducida para el último ladrillo
SLOW_PADDLE_SPEED = 3  # Velocidad reducida de la paleta cuando suena last_ball.wav
BRICK_ROWS, BRICK_COLS = 5, 10
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 30

# --- Clases ---
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 15))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 30))
        self.speed = PADDLE_SPEED  # velocidad actual de la paleta

    def update(self, keys):
        # Usar velocidad dinámica según atributo
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 100), (7,7), 7)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.vx, self.vy = BALL_SPEED, -BALL_SPEED

    def update(self):
        # Movimiento de la pelota
        self.rect.x += self.vx
        self.rect.y += self.vy

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((BRICK_WIDTH-2, BRICK_HEIGHT-2))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Función principal ---
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Cargar sonidos de colisión en orden
    sonido_archivos = ['colision1.wav', 'colision2.wav', 'colision3.wav']
    sonidos_col = [pygame.mixer.Sound(archivo) for archivo in sonido_archivos]
    indice_sonido = 0
    # Sonido especial para último ladrillo
    last_ball_sound = pygame.mixer.Sound('last_ball.wav')
    last_slowed = False
    # Cargar jumpscare
    scream_sound = pygame.mixer.Sound('scream.wav')
    jumpscare_img = pygame.image.load('canye_jumpscare.png').convert()
    jumpscare_img = pygame.transform.scale(jumpscare_img, (WIDTH, HEIGHT))

    all_sprites = pygame.sprite.Group()
    bricks = pygame.sprite.Group()

    paddle = Paddle()
    ball = Ball()
    all_sprites.add(paddle, ball)

    # Crear ladrillos
    colors = [(255,0,0),(255,165,0),(255,255,0),(0,128,0),(0,0,255)]
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = col * BRICK_WIDTH + 1
            y = row * BRICK_HEIGHT + 1 + 50
            brick = Brick(x, y, colors[row % len(colors)])
            all_sprites.add(brick)
            bricks.add(brick)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        paddle.update(pygame.key.get_pressed())
        ball.update()

        # Colisión pelota ↔ paredes de la ventana
        if ball.rect.left <= 0:
            ball.rect.left = 0
            ball.vx *= -1
            sonidos_col[indice_sonido].play()
            indice_sonido = (indice_sonido + 1) % len(sonidos_col)
        elif ball.rect.right >= WIDTH:
            ball.rect.right = WIDTH
            ball.vx *= -1
            sonidos_col[indice_sonido].play()
            indice_sonido = (indice_sonido + 1) % len(sonidos_col)
        if ball.rect.top <= 0:
            ball.rect.top = 0
            ball.vy *= -1
            sonidos_col[indice_sonido].play()
            indice_sonido = (indice_sonido + 1) % len(sonidos_col)

        # Colisión pelota ↔ paleta
        if pygame.sprite.collide_rect(ball, paddle) and ball.vy > 0:
            ball.rect.bottom = paddle.rect.top
            ball.vy *= -1
            sonidos_col[indice_sonido].play()
            indice_sonido = (indice_sonido + 1) % len(sonidos_col)

        # Colisión pelota ↔ ladrillo
        hit_brick = pygame.sprite.spritecollideany(ball, bricks)
        if hit_brick:
            if ball.vy > 0:
                ball.rect.bottom = hit_brick.rect.top
            else:
                ball.rect.top = hit_brick.rect.bottom
            ball.vy *= -1
            hit_brick.kill()
            # Sonido normal de colisión
            sonidos_col[indice_sonido].play()
            indice_sonido = (indice_sonido + 1) % len(sonidos_col)
            # Si queda un solo ladrillo y aún no ralentizado
            if len(bricks) == 1 and not last_slowed:
                last_slowed = True
                last_ball_sound.play(loops=-1)
                ball.vx = SLOW_BALL_SPEED if ball.vx > 0 else -SLOW_BALL_SPEED
                ball.vy = SLOW_BALL_SPEED if ball.vy > 0 else -SLOW_BALL_SPEED
                paddle.speed = SLOW_PADDLE_SPEED

        # Si ya no quedan ladrillos, detener loop del sonido especial
        if last_slowed and len(bricks) == 0:
            last_ball_sound.stop()

        # Verificar si la pelota cae por debajo: fin del juego
        if ball.rect.top > HEIGHT:
            # Detener sonido en caso de game over
            if last_slowed:
                last_ball_sound.stop()
            # Jumpscare y sonido único
            scream_sound.play()
            screen.blit(jumpscare_img, (0, 0))
            pygame.display.flip()
            pygame.time.delay(int(scream_sound.get_length() * 1000))
            print("¡Game Over!")
            running = False

        # Dibujar todo
        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
