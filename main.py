import random
import sys
import pygame
import time
import math

# Define some CGA colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255,85,255)
CYAN = (85,255,255)
CGA = [WHITE,CYAN,PINK]  # CGA palette

# Define some other colors
RED = (255, 0, 0, 0)
BLUE = (102, 153, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (0, 115, 153)
GREYSOFT = (0, 38, 77)
ORANGE = (255, 153, 0)
GREYGREEN = (102, 153, 153)
VIOLET = (255, 51, 204)
BLUESKY = (179, 255, 255)

SCREEN_X = 1366
SCREEN_Y = 768

sprite_size_x = 48
sprite_size_y = 48


Num_ecran = 1   # 0 = In game, 1 = Menu
level = 0
score = 0

player_x = 0    # variable globale qui enregistre la position du joueur sur l'axe X

# --------------------------------------------------
# Fonctions & classes pour charger les sprites
# --------------------------------------------------
class Spritesheet():
    def __init__(self,image):
        self.spritesheet = image

    def getimage(self,frame, row, x,y,scale,color):    # x et y = taille du sprite à récupérer
        image = pygame.Surface((x,y)).convert_alpha()   # On crée une image vierge de la taille du sprite
        image.blit(self.spritesheet, (0,0),(frame * x,row * y,x,y))    # On colle sur l'image vierge la frame voulue
        image = pygame.transform.scale(image,(x*scale,y*scale))         #On zoom si besoin avec le paramètre scale
        image.set_colorkey(color)
        return image    # La fonction renvoie l'image du sprite extrait

#---Charge une liste d'images dans le sprite sheet, en 2 D-------------------------------------------------------------
def Load_sheet(nomspritesheet, animationstep, taille_sprite_x, taille_sprite_y):   # Fichier, découpage des animations, taille du sprite
    list = []
    zoom = 1
    sprite_sheet_image = pygame.image.load(nomspritesheet).convert_alpha()  # Charge spritesheet complet
    sprite_sheet = Spritesheet(sprite_sheet_image)  # appel la classe Spritesheet et charge l'image complète
    for j in range(0,len(animationstep)):
        for i in range(0,animationstep[j]):
            image = sprite_sheet.getimage(i, j, taille_sprite_x, taille_sprite_y, zoom,(0, 0, 0))  # on stocke l'image découpée dans le spritesheet. Zoom = 1
            list.append(image)
    # Retourne la liste des images
    return list

# Fonction qui charge les images des sprites--------------------------------------------------
def load_image(name):
    image = pygame.image.load(name)
    return image


#--------CLASSES-----------------------------------------------------------------------------------
#--------Player-----------------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.posx = int(SCREEN_X/2)
        self.posy = 700
        self.images = []
        self.animationstep = [4]
        self.width = sprite_size_x
        self.height = sprite_size_y
        self.imageslist = Load_sheet("Assets/player.png", self.animationstep, sprite_size_x, sprite_size_y)
        self.rect = pygame.Rect(self.posx, self.posy, sprite_size_x, sprite_size_y)
        self.rect.x = self.posx
        self.rect.y = self.posy
        self.slowframe = 0
        self.frame = 0
        self.frame_max = 2
        self.frame_min = 0
        self.velx = 4
        self.soucoupe_timer_zone = random.randint(500,1000)  # fenetre d'apparition de la soucoupe
        self.soucoupe_timer = 0                              # timer



    # def select_frame(self):
    #     self.frame_min = 0
    #     self.frame_max = 4

    def draw(self):
        self.slowframe += 1
        if self.slowframe > 10:
            self.slowframe = 0
            self.frame += 1
            if self.frame == self.frame_max:
                self.frame = self.frame_min
        ecran.blit(self.imageslist[self.frame], (self.rect.x, self.rect.y))


    def update(self):
        global player_x

        # on enregistre la position du joueur dans une variable globale
        player_x = self.rect.x

        # Captation des touches du clavier
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT]:    # press => : le joueur monte
            self.rect.x -= self.velx
        if pressed_keys[pygame.K_RIGHT]:    # press => : le joueur monte
            self.rect.x += self.velx


#--------Tirs-----------------------------------------------------------------------------------
class Tir(pygame.sprite.Sprite):
    def __init__(self, posx, posy):
        super().__init__()
        self.image = pygame.Surface([10, 10])                       # sprite de 10*10 pixels
        pygame.draw.rect(self.image, CYAN, pygame.Rect(0, 0,10,10)) # sprite de 10*10 pixels
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy

    def update(self):
        global score
        self.rect.y -= 5
        # dépassement des limites de l'écran ?
        if self.rect.y < 0:
            self.kill()
        #collision avec un alien ?
        collision = pygame.sprite.spritecollide(self, all_enemy, False)
        if collision:
            self.kill()                     # on supprime la bullet
            for enemy in collision:       # on parcourt les ennemis pour savoir lequel est en collision
                if enemy.explode:
                    pass
                else:
                    score += 100
                    enemy.explode = True
                    enemy.frame_min = 10    # frame contenant l'explosion
                    enemy.frame_max = 21
                    enemy.frame = enemy.frame_min
                    # pygame.mixer.Sound.play(tir_son)


#--------gates-----------------------------------------------------------------------------------
class Gate(pygame.sprite.Sprite):
    def __init__(self, col, posx, posy):
        super().__init__()
        self.image = pygame.Surface([70, 10])                       # sprite de 10*10 pixels
        pygame.draw.rect(self.image, col, pygame.Rect(0, 0,70,10)) # sprite de 10*10 pixels
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy
#--------Soucoupe bonus-----------------------------------------------------------------------------------
class Soucoupe(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.posx = 30
        self.posy = 30
        self.images = []
        self.animationstep = [2]
        self.width = sprite_size_x
        self.height = sprite_size_y
        self.imageslist = Load_sheet("Assets/soucoupe.png", self.animationstep, sprite_size_x, sprite_size_y)
        self.rect = pygame.Rect(self.posx, self.posy, sprite_size_x, sprite_size_y)
        self.rect.x = self.posx
        self.rect.y = self.posy
        self.slowframe = 0
        self.frame = 0
        self.frame_max = 2
        self.frame_min = 0
        self.velx = 4

    def select_frame(self):
        self.frame_min = 0
        self.frame_max = 2

    def draw(self):
        self.slowframe += 1
        if self.slowframe > 10:
            self.slowframe = 0
            self.frame += 1
            if self.frame == self.frame_max:
                self.frame = self.frame_min
        ecran.blit(self.imageslist[self.frame], (self.rect.x, self.rect.y))

    def update(self):
        self.rect.x += self.velx
        if self.rect.x > SCREEN_X:
            self.kill()


#--------bullet-----------------------------------------------------------------------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, posx, posy):
        super().__init__()
        self.images = []
        self.animationstep = [4]
        self.width = sprite_size_x
        self.height = sprite_size_y
        self.imageslist = Load_sheet("Assets/bullet.png", self.animationstep, 7,23)
        self.rect = pygame.Rect(0, 0, 7,23)
        self.rect.x = posx
        self.rect.y = posy
        self.slowframe = 0
        self.frame = 0
        self.frame_max = 4
        self.frame_min = 0
        self.vely = 2

    # def select_frame(self):
    #     self.frame_min = 0
    #     self.frame_max = 4

    def draw(self):
        self.slowframe += 1
        if self.slowframe > 10:
            self.slowframe = 0
            self.frame += 1
            if self.frame == self.frame_max:
                self.frame = self.frame_min
        ecran.blit(self.imageslist[self.frame], (self.rect.x, self.rect.y))


    def update(self):
        self.rect.y += self.vely
        # dépassement des limites de l'écran ?
        if self.rect.y > SCREEN_Y:
            self.kill()




#--------Enemies-----------------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, posx, posy, numero):
        super().__init__()
        self.posx = posx
        self.posy = posy
        self.images = []
        self.animationstep = [2,2,2,2,2,12]
        self.width = sprite_size_x
        self.height = sprite_size_y
        self.imageslist = Load_sheet("Assets/enemis_spritesheet_CGA.png", self.animationstep, sprite_size_x, sprite_size_y)
        self.rect = pygame.Rect(self.posx, self.posy, sprite_size_x, sprite_size_y)
        self.rect.x = self.posx
        self.rect.y = self.posy
        self.slowframe = 0
        if numero == 1:
            self.frame_min = 0
            self.frame_max = 1
            self.frame = self.frame_min
        if numero == 2:
            self.frame_min = 2
            self.frame_max = 3
            self.frame = self.frame_min
        if numero == 3:
            self.frame_min = 4
            self.frame_max = 5
            self.frame = self.frame_min
        if numero == 4:
            self.frame_min = 6
            self.frame_max = 7
            self.frame = self.frame_min
        if numero == 5:
            self.frame_min = 8
            self.frame_max = 9
            self.frame = self.frame_min
        self.velx = 1
        self.descente = False
        self.descente_compteur = 0
        self.timer = 0
        self.timer_zone = random.randint(1000,2000)
        if numero > 3 :             # Seuls certains types d'enemis tirent
            self.tir = True
        else:
            self.tir = False
        self.explode = False        # pour gérer les explosions



    # def select_frame(self):
    #     self.frame_min = 3
    #     self.frame_max = 5

    def draw(self):
        self.slowframe += 1
        if self.slowframe > 10:
            self.slowframe = 0
            self.frame += 1
            if self.frame > self.frame_max:
                if self.explode:        # on arrive au bout de la boucle de Frames, si on est dans une explosion on kill l'objet
                    self.frame = self.frame_min # sinon ça bug au moment de l'affichage...
                    self.kill()
                else:                   # pas d'explosion, on reprend au début de la boucle de frames
                    self.frame = self.frame_min
        ecran.blit(self.imageslist[self.frame], (self.rect.x, self.rect.y)) # affichage


    def update(self):
        # on vérifie si l'alien est en descente ou en déplacement horizontal
        if self.descente:                                       # Descente façon machine à écrire sur l'axe Y
            if self.descente_compteur < sprite_size_y:                     # on est descendu jusqu'au bout ?
                self.rect.y += 1
                self.descente_compteur += 1
            else:                                               # on est descendu jusqu'au bout !
                self.descente_compteur = 0
                self.descente = False
        else:                                                   # Déplacement classique sur l'axe X
            self.rect.x += self.velx
            if self.rect.x > SCREEN_X-sprite_size_x:
                self.velx = self.velx*(-1)
                self.descente = True
            if self.rect.x < 0:
                self.velx = self.velx*(-1)
                self.descente = True

            # Tir ?
            if self.tir :           # Tir uniquement si tir = TRUE
                self.timer += 1
                if self.timer == self.timer_zone:                   # Tir déclenché
                    bullet = Bullet(self.rect.x, self.rect.y)       # on crée un objet aux coordonnées de l'alien
                    all_bullet.add(bullet)
                    all_sprites_list.add(bullet)
                    self.timer = 0                                  # on remet à 0 le timer pour déclencher un nouveau tir
                    self.timer_zone = random.randint(100, 1000)     # délai d'apparition du prochain tir


#-------Etoiles--------------------------------------------------------------------------
class Etoiles(pygame.sprite.Sprite):
    def __init__(self, width, height, posx, posy, velx):
        super().__init__()
        # self.color = [WHITE,CYAN,PINK]  # CGA palette
        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, CGA[random.randint(0,2)], pygame.Rect(0, 0, width, height))
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy
        self.vely = random.randint(1,3)


    def update(self):       # étoiles vont de droit à gauche pour simuler la vitesse
        self.rect.y += self.vely
        if self.rect.y > SCREEN_Y:     # Etoile sort de l'écran
            self.rect.y = 0                                   # on la replace à l'extreme droite sur l'axe X
            self.rect.x = random.randint(0,SCREEN_X)        # axe x aléatoire
            self.velx = random.randint(1,3)             # vélocité aléatoire


# ---------------------------------------------------------------------------------------
#----Fonction pour écrire à l'écran-------------------------------------------------------------
def ecrit(texte,col,size, x, y,police):

    if police == "":
        font = pygame.freetype.Font(None, size)
    else:
        font = pygame.freetype.Font("Assets/retro.ttf", size)

    text_surf2, text_rect2 = font.render(texte,col)     # font.render permet d'avoir une transparence
    ecran.blit(text_surf2, (x, y))


#---------------------------------------------------------------------------------
# -Update affichage graphique during the game-------------------------------------
def Updateaffichage():

    # appel de la fonction update de l'ensemble des objets (quand ils en ont une)
    all_sprites_list.update()  # Appelle la fonction update de chaque groupe de sprite

    # efface l'écran
    ecran.fill(BLACK)

    # Affichage des différents groupes de sprites

    # ici on anime les sprites en image fixe
    all_etoiles.draw(ecran)
    all_tirs.draw(ecran)
    all_gates.draw(ecran)

    # ici on anime les sprites qui comportent plusieurs images
    for enemy in all_enemy:
        enemy.draw()    # appel de la fonction draw dans la classe enemy

    for soucoupe in all_soucoupe:
        soucoupe.draw()    # appel de la fonction draw dans la classe soucoupe

    for bullet in all_bullet:
        bullet.draw()    # appel de la fonction draw dans la classe soucoupe

    # Affichage Level
    ecrit("Level : ", PINK, 15, 20, 20, "retro")
    ecrit(str(level), PINK, 15, 120, 20, "retro")

    # Affichage Score
    ecrit("Score : ", CYAN, 15, SCREEN_X-200, 20, "retro")
    ecrit(str(score), CYAN, 15, SCREEN_X-100, 20, "retro")


    # Affichage player
    for player in all_player:
        player.draw()


    pygame.display.flip()

    clock.tick(100)

#---------------------------------------------------------------------------------
def gagne():
    global level
    level += 1
    new_level(level)
# -----------------------------------------------------
def new_level(level):
    # Nettoyage des groupes de sprites
    all_sprites_list.empty()
    all_enemy.empty()
    all_etoiles.empty()
    all_player.empty()
    all_tirs.empty()
    all_gates.empty()
    all_soucoupe.empty()
    all_bullet.empty()

    # Création des ennemies
    k = 0   # espace Y entre les enemis
    for j in range(0,3):
        z = 0   # espace X entre les ennemis
        k += sprite_size_y
        for i in range (0,13):
            enemy_type = random.randint(1, 5)                                             # Type d'ennemis : aléatoire
            # enemy_type = 2                                                                  # Type d'ennemis : 1
            enemy = Enemy(70 + (i*sprite_size_x)+z,50 + (j*sprite_size_y)+k, enemy_type)    # Création objet ennemi
            all_enemy.add(enemy)
            all_sprites_list.add(enemy)
            z += sprite_size_x     # espace X entre les ennemis

    # Création des étoiles
    for i in range(40):
        etoiles = Etoiles( 3,3,random.randint(0,SCREEN_X), random.randint(0,SCREEN_Y),3)     # Fenetre d'apparition des étoiles
        all_etoiles.add(etoiles)
        all_sprites_list.add(etoiles)

    # Création des gates
    for i in range(0,4):
        gate = Gate(CYAN,300 + (i * (sprite_size_x * 5)), 680)      # première ligne de défense
        all_gates.add(gate)
        all_sprites_list.add(gate)
        gate = Gate(WHITE, 300 + (i * (sprite_size_x * 5)), 670)    # seconde ligne de défense
        all_gates.add(gate)
        all_sprites_list.add(gate)

    # Crée player
    player = Player()
    all_player.add(player)
    all_sprites_list.add(player)

# ----Game--------------------------------------------------------------------------------------------------------------
def game():

    # apparition soucoupe bonus
    for player in all_player:                                       # on incrémente le timer soucoupe
        player.soucoupe_timer += 1
        if player.soucoupe_timer_zone == player.soucoupe_timer :    # est-ce qu'on est dans la zone d'apparition ?
            soucoupe = Soucoupe()                           # création soucoupe bonus
            all_soucoupe.add(soucoupe)
            all_sprites_list.add(soucoupe)
            soucoupe_timer_zone = random.randint(500, 1000) # délai avant prochaine soucoupe
            soucoupe_timer = 0                              # remise à 0 du timer

    # affichage général du jeu
    Updateaffichage()

# ----Menu-------------------------------------------------
def menu():
    # affichage de l'écran titre
    x = ecran.get_size()  # on récupère la taille de l'écran
    fond = pygame.image.load("Assets/fond.jpg")  # on charge l'image
    fond1 = pygame.transform.scale(fond, (x))  # on adapte l'image à la taille de l'écran
    ecran.blit(fond1, (0, 0))  # on pose l'image sur ecran
    ecrit("Space", PINK, 50, 100, 30, "retro")
    ecrit("Invaders", PINK, 50, 80, 80, "retro")
    ecrit("A game by YML", PINK, 20, 80, 140, "retro")
    img = pygame.image.load("Assets/YmCGA.png")  # on charge l'image
    img1 = pygame.transform.scale(img, (120, 160))  # on adapte la taille de l'image
    ecran.blit(img1, (170, 170))  # on pose l'image sur ecran
    ecrit("Press", WHITE, 40, 50, 350, "retro")
    ecrit("SPACE", CYAN, 40, 100, 390, "retro")
    ecrit("to begin", WHITE, 40, 150, 430, "retro")

    pygame.display.update()  # on affiche le tout

# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------Programme principal-------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# Démarrage écran graphique
pygame.init()
size = [SCREEN_X, SCREEN_Y]
ecran = pygame.display.set_mode(size)
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Création des groupes de sprites
all_sprites_list = pygame.sprite.Group()
all_enemy = pygame.sprite.Group()
all_etoiles = pygame.sprite.Group()
all_player = pygame.sprite.Group()
all_tirs = pygame.sprite.Group()
all_soucoupe = pygame.sprite.Group()
all_bullet = pygame.sprite.Group()
all_gates = pygame.sprite.Group()


continuer = True
# --------------------------------------------------------------------------------------------
# Boucle principale--------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
while continuer:

    # Boucle qui tourne pendant le jeu en dehors de la gestion des évènements-------------------------------------------

    # On rafraichit l'affichage graphique des différents menus

    if Num_ecran == 0:  # Ecran in game
        game()

        # le jeu a démarré (= joueur a appuyé sur espace ou bouton X) ?


    if Num_ecran == 1:  # Ecran de menu
        menu()





# Gestion des évenements dans l'ensemble des Parties du programme : in game, menu, tableau etc...-------------------
    for event in pygame.event.get():


        pressed = pygame.key.get_pressed()  # captation des évèvements claviers sous forme de liste
                                            # permet de capter la répétition des frappes de touches

        # Clic sur la croix fermeture de la fenetre
        if event.type == pygame.QUIT:
            continuer = False
            pygame.quit()

        # KEYDOWN permet de savoir si une touche a été pressée
        # moins rapide que get_pressed, permet de n'avoir qu'une seule touche pressée
        if event.type == pygame.KEYDOWN:  # Utilisateur presse une touche

            # Escape
            if event.key == pygame.K_ESCAPE:
                continuer = False
                pygame.quit()

            # Espace -> on démarre le jeu ou on tir si on est déjà in game
            if event.key == pygame.K_SPACE:
                if Num_ecran == 0:              # on est in game
                    tir = Tir(player_x + int(sprite_size_x/2) - 5,730)
                    all_tirs.add(tir)
                    all_sprites_list.add(tir)
                if Num_ecran == 1:
                    new_level(level)
                    Num_ecran = 0
                    print("Num ecran : ",Num_ecran)
                    Updateaffichage()