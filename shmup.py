# Shmup game
# Shoot 'em up

import pygame
import random
from os import path

# Diretórios utilizados no jogo
img_dir = path.join(path.dirname(__file__), "img")
snd_dir = path.join(path.dirname(__file__), "snd")

# Constantes
WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000
FONT_NAME = pygame.font.match_font("arial")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)

# Inicializa o pygame e cria a janela
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup")
# Objeto para ajudar a controlar o tempo - FPS
clock = pygame.time.Clock()

# Função para desenhar texto
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Cria novos asteroides
def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs_group.add(m)

# Desenha a barra de 'vida' que a nave tem
def draw_shield_bar(surf, x, y, player_shield):
    if player_shield < 0:
        player_shield = 0
    BAR_LENGHT = 100
    BAR_HEIGHT = 10
    fill = (player_shield / 100) * BAR_LENGHT
    outline_rect = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# Desenha a quantidade de vidas restantes 
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# Classe Player - Nave
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Imagem
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        # Posição
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

        # Para testar a colisão
        self.radius = 20
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        self.speedx = 1 # Velocidade
        self.shield = 100 # Escudo total
        self.shoot_delay = 300 # Tempo de delay para o tiro
        self.last_shoot = pygame.time.get_ticks() # Tempo do ultimo tiro
        self.lives = 3 # Vidas

        # Quando a nave 'morre' fica um tempo oculta
        self.hidden = False 
        self.hide_timer = pygame.time.get_ticks()

        # Powerups
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        key = pygame.key.get_pressed()

        if key[pygame.K_d]:
            self.rect.x += 5
        if key[pygame.K_a]:
            self.rect.x -= 5

        if key[pygame.K_SPACE]:
            self.shoot()

        # Collision
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0

        # Mostra a nave se ela estiver oculta
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        # Timeout para os powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    # Tiro 
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            # Tiro nível 1
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets_group.add(bullet)
                shoot_sound.play()
            # Tiro nível 2
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets_group.add(bullet1)
                bullets_group.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # Esconde o Player temporariamente
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    # Quando o jogador pega o powerup a função é ativada
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()


# Classe Mob - Asteroid
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Imagem
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()

        # Para testar a colisão
        self.radius = int(self.rect.width * .85 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        # Posição
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)

        # Velocidade e rotação
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)

        self.last_update = pygame.time.get_ticks()

    # Função de rotação
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()

        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Se o asteroide estiver fora do limite da tela o asteroid recebe novos parametros
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


# Classe Bullet - Tiro
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Imagem
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        # Posição
        self.rect.bottom = y
        self.rect.centerx = x

        # Velocidade
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

        # Se for para fora do limite o tiro é 'morto'
        if self.rect.bottom < 0:
            self.kill()


# Classe Pow - Powerups
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)

        # Imagem
        self.type = random.choice(["shield", "gun"]) # Escolhe aleatoriamente o tipo
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        # Posição
        self.rect.center = center

        # Velocidade
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy

        # Se fora para fora do limite o powerup é 'morto'
        if self.rect.top > HEIGHT:
            self.kill()


# Classe Explosion - Explosão
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)

        # Tamanho
        self.size = size

        # Imagem        
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()

        # Posição
        self.rect.center = center

        # Variáveis para controlar os frames
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect.center = center


# Carrega todos os game graphics
background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background_rect = background.get_rect()

# Imagem do player
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert()
# Mini imagem do player serve para utilizar na contagem de vidas
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)

# Imagem do tiro
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()

# Imagem dos meteoros
meteor_images = []
meteor_list = ["meteorBrown_big1.png", "meteorBrown_big2.png", "meteorBrown_med1.png",
                "meteorBrown_med3.png", "meteorBrown_small1.png", "meteorBrown_small2.png",
                "meteorBrown_tiny1.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

# Animação da explosão
explosion_anim = {}
explosion_anim["lg"] = []
explosion_anim["sm"] = []
explosion_anim["player"] = []
for i in range(9):
    # Explosão dos asteroides
    filename = f"regularExplosion0{i}.png"
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    # A imagem grande serve para colisão dos tiros com o asteroide
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim["lg"].append(img_lg)
    # A imagem pequena serve para a colisçao dos aseteroides na nave
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim["sm"].append(img_sm)
    
    # Explosão da nave
    filename = f"sonicExplosion0{i}.png"
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim["player"].append(img)

# Imagem dos powerups
powerup_images = {}
powerup_images["shield"] = pygame.image.load(path.join(img_dir, "shield_gold.png")).convert()
powerup_images["gun"] = pygame.image.load(path.join(img_dir, "bolt_gold.png")).convert()

# Sons do jogo
# Som do tiro
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "pew.wav"))

# Sons da explosão
expl_sound = []
for snd in ["expl3.wav", "expl6.wav"]:
    expl_sound.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

# Som de 'morte' da nave
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, "rumble1.ogg"))

# Som dos powerups
shield_sound = pygame.mixer.Sound(path.join(snd_dir, "pow4.wav"))
power_sound = pygame.mixer.Sound(path.join(snd_dir, "pow5.wav"))

# Música
pygame.mixer.music.load(path.join(snd_dir, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.4) # Volume
pygame.mixer.music.play(loops=-1) # Deixa a música infinita

# Sprite groups
all_sprites = pygame.sprite.Group()
mobs_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
powerups_group = pygame.sprite.Group()

# Player
player = Player()
all_sprites.add(player)

# Mob
for i in range(8):
    newmob()

score = 0
running = True
# Laço principal do jogo
while running:
    # Mantem o loop rodando na velocidade certa
    clock.tick(FPS)
    # Processa os inputs - Eventos
    for event in pygame.event.get():
        # Verifica se a janela foi fechada
        if event.type == pygame.QUIT:
            running = False # Interrompe o laço do jogo

    # Update
    all_sprites.update() # Da update em todas as sprites

    # Colisão de tiro com o asteroide
    bullet_hits = pygame.sprite.groupcollide(mobs_group, bullets_group, True, True, pygame.sprite.collide_circle)
    for hit in bullet_hits: # Se houve colisão o laço se ativa
        score += 50 - hit.radius # O score aumenta conforme o tamanho do asteroide
        random.choice(expl_sound).play() # Play no som de explosão
        expl = Explosion(hit.rect.center, "lg")
        all_sprites.add(expl)

        # Chance de dropar algum powerup
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups_group.add(pow)

        # Cria um novo asteroide
        newmob()

    # Colisão do player com o asteroide
    player_collide = pygame.sprite.spritecollide(player, mobs_group, True, pygame.sprite.collide_circle)
    for collide in player_collide: # Se houve colisão o laço se ativa
        player.shield -= collide.radius * 2 # Tira escudo do player conforme o tamanho do asteroide
        expl = Explosion(collide.rect.center, "sm")
        all_sprites.add(expl)
        newmob() # Cria um novo asteroide
        # Se o escudo chegar a 0
        if player.shield <= 0:
            player_die_sound.play() # Play no som de morte
            death_explosion = Explosion(player.rect.center, "player")
            all_sprites.add(death_explosion)
            player.hide() # Esconde o player temporariamente
            player.lives -= 1 # Tira uma vida do player
            player.shield = 100 # O escudo volta ser 100
    
    # Colisão com os powerups
    powerup_collide = pygame.sprite.spritecollide(player, powerups_group, True)
    for hit in powerup_collide: # Se houve colisão o laço se ativa
        # Se for o tipo 'shield'
        if hit.type == "shield":
            player.shield += 20 # Player recebe +20 de escudo
            shield_sound.play() # Ativa o som
            if player.shield >= 100: # Se o player ja estiver com o escudo cheio não acontece nada
                player.shield = 100
        # SE for tipo 'gun'
        if hit.type == "gun":
            player.powerup() # Função pra deixar o tiro melhor
            power_sound.play() # Ativa o som

    # Se o jogador morreu e a explosão terminou
    if player.lives == 0 and not death_explosion.alive():
        running = False # Quebra o laço principal

    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)

    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

    # *Depois* de desenhar tudo, flip a tela
    pygame.display.flip()

pygame.quit()

