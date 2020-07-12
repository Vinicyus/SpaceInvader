import pygame
import os
import time
import random
from pygame import mixer

pygame.font.init()
pygame.init()
mixer.init()

WIDTH, HEIGHT = 750, 680
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (300,40) #screen center
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Space Invader")
programIcon = pygame.image.load(os.path.join("assets", "space_shuttle_icon.png"))
pygame.display.set_icon(programIcon)

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Music & Sound Effects
gameOver = pygame.mixer.Sound("game_over.wav")
shipExplosion = pygame.mixer.Sound("explosion2.wav")
shipShoot = pygame.mixer.Sound("shoot.wav")

# Color & Fonts
white = (255, 255, 255)
black = (0, 0, 0)
grey = (122, 122, 122)
red = (255, 0, 0)
light_red = (255,153,153)
green = (0, 204, 102)
light_green = (204, 255, 153)
blue = (0,0,255)
light_blue = (153, 153, 255)
yellow = (252,237,66)
light_yellow = (255, 255, 178)

extrasmallfont = pygame.font.SysFont("comicsansms", 15)
smallfont = pygame.font.SysFont("comicsansms", 25)
medfont = pygame.font.SysFont("comicsansms", 50)
largefont = pygame.font.SysFont("comicsansms", 65)

# Game Variables
clock = pygame.time.Clock()
FPS = 60

def text_objects(text, color, size):
	if size == "extrasmall":
		textSurface = extrasmallfont.render(text, True, color)
	elif size == "small":
		textSurface = smallfont.render(text, True, color)
	elif size == "medium":
		textSurface = medfont.render(text, True, color)
	elif size == "large":
		textSurface = largefont.render(text, True, color)

	return textSurface, textSurface.get_rect()

def text_to_button(msg, color, buttonx, buttony, buttonwidth, butonheight, size="small"):
	textSurf, textRect = text_objects(msg, color, size)
	textRect.center = ((buttonx+(buttonwidth/2), buttony+(butonheight/2)))
	WIN.blit(textSurf, textRect)

def button(text, x, y, width, height, inactive_color, active_color, action = None):
	cur = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	if x + width > cur[0] > x and y + height > cur[1] > y:
		pygame.draw.rect(WIN, active_color, (x, y, width, height))
		if click[0] == 1 and action != None:
			if action == "quit":
				pygame.quit()
				quit()
			if action == "play":
				main()
			if action == "record":
				records()
	else:
		pygame.draw.rect(WIN, inactive_color, (x, y, width, height))

	text_to_button(text, black, x, y, width, height)

def message_to_screen(msg,color, y_displace=0, size = "small"):
	textSurf, textRect = text_objects(msg, color, size)
	textRect.center = (WIDTH/2), (HEIGHT/2) + y_displace
	WIN.blit(textSurf, textRect)

def records():
	record = True
	file = open('scores.txt')
	lines = sorted(file.readlines(), reverse = True, key = int)
	while record:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r:
					main_menu()
				elif event.key == pygame.K_q:
					pygame.quit()
					quit()

		WIN.blit(BG, (0,0))
		message_to_screen("Records", yellow, -210, "large")
		message_to_screen("Top 10 Records", white, -160, "extrasmall")

		lineHeight = -130
		i = 0
		for line in lines:
			line = line[:-1]
			message_to_screen(str(i + 1) + "°: " + str(line), white, lineHeight, "small")
			lineHeight += 30
			i += 1
			if i == 10:
				break
		file.close()

		message_to_screen("Press R to return to the main menu", white, 210, "small")

		pygame.display.update()
		clock.tick(FPS)

def pause():
	paused = True
	WIN.blit(BG, (0,0))
	message_to_screen("Paused", yellow, -100, "large")
	message_to_screen("Press R to return to the main menu", white, 0)
	message_to_screen("Press C to continue", white, 30)
	message_to_screen("Press Q to quit", white, 60)

	while paused:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_c:
					paused = False
				elif event.key == pygame.K_r:
					main_menu()
				elif event.key == pygame.K_q:
					pygame.quit()
					quit()
		pygame.display.update()
		clock.tick(FPS)

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not(self.y <= height and self.y >= 0)

	def collision(self, obj):
		return collide(self, obj)

class Ship:
	COOLDOWN = 30

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()

class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)

	def draw(self, window):
		super().draw(window)
		self.healthbar(window)

	def healthbar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):		
	COLOR_MAP = {
				"red": (RED_SPACE_SHIP, RED_LASER),
				"green": (GREEN_SPACE_SHIP, GREEN_LASER),
				"blue": (BLUE_SPACE_SHIP, BLUE_LASER)
	}

	def __init__(self, x, y, color, health =100):
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x-20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 

def main_menu():
	WIN.blit(BG, (0,0))
	intro = True
	pygame.mixer.music.load("menu_screen.mp3")
	pygame.mixer.music.play(-1)
	while intro:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					pygame.quit()
					quit()

		message_to_screen("Space Invader", yellow, -100, "large")
		message_to_screen("Protect the galaxy from foreign invaders!", white, -40, "small")

		button("Play", 250,350,100,50, red, light_red, action="play" )
		button("Records", 400,350,100,50, green, light_green, action="record")

		pygame.display.update()
		clock.tick(FPS)

def main():
	run = True
	pygame.mixer.music.load("game_screen.mp3")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.3)
	level = -10 #to start with 0
	lives = 3
	main_font = pygame.font.SysFont("comicsans", 50)

	enemies = []
	wave_length = 5
	enemy_vel =  1

	player_vel = 6
	laser_vel = 7

	player = Player(300, 560)

	lost = False
	lost_count = 0

	def redraw_window(lost):
		WIN.blit(BG, (0,0))
        # draw text
		lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
		level_label = main_font.render(f"Score: {level}", 1, (255,255,255))

		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

		for enemy in enemies:
 			enemy.draw(WIN)

		player.draw(WIN)

		# if lost:
		# 	lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
		# 	WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

		# pygame.display.update()

		if lost == True:
			f = open('scores.txt', 'a')
			f.writelines(str(level) + "\n")
			f.close()
			pygame.mixer.Sound.play(gameOver)

		while lost == True:
			WIN.blit(BG, (0,0))
			message_to_screen("Game over", red, -120, size="large")
			message_to_screen("Press R to return to the main menu", white, -50, size="small")
			message_to_screen("Press C to play again", white, -20, size="small")
			message_to_screen("Press Q to quit", white, 10, size="small")
			pygame.display.update()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					lost = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						lost = False
					elif event.key == pygame.K_r:
						main_menu()
					if event.key == pygame.K_c:
						main()

		pygame.display.update()

	while run:
		clock.tick(FPS)	
		redraw_window(lost)

		#if lives < 0 or player.health <= 0:
		#if lives < 1:
		#	lost = True
		#	lost_count += 1

		if player.health <= 0:
			pygame.mixer.Sound.play(shipExplosion)
			lives -= 1
			lost_count += 1
			if lives < 1:
				lost = True
				lost_count += 1
			else:
				player = Player(300, 560)


		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		if len(enemies) == 0:
			level += 10
			wave_length += 5
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH -100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()

		keys = pygame.key.get_pressed()
		if keys[pygame.K_a] and player.x + player_vel > 0: #left
			player.x -= player_vel
		if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
			player.x += player_vel
		if keys[pygame.K_w] and player.y + player_vel > 0: #up
			player.y -= player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()
			pygame.mixer.Sound.play(shipShoot)
		if keys[pygame.K_p]:
			pause()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2*FPS) == 1:
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)	
			elif enemy.y  + enemy.get_height() > HEIGHT:
				player.health -= 10
				enemies.remove(enemy)

		player.move_lasers(-laser_vel, enemies)


main_menu()