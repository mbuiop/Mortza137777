#!/usr/bin/env python3
"""
Galaxy Advanced 3D Game - موتور بازی سه‌بعدی پیشرفته فضایی
Created by: ACTOn Game Studio
"""

import pygame
import numpy as np
import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame.mixer as mixer
from pygame.locals import *
import sys
import os

class Galaxy3DEngine:
    """موتور اصلی بازی سه‌بعدی کهکشانی"""
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # وضعیت بازی
        self.game_state = "MAIN_MENU"  # MAIN_MENU, PLAYING, PAUSED, GAME_OVER
        self.score = 0
        self.level = 1
        self.lives = 3
        self.fuel = 100.0
        self.max_fuel = 100.0
        
        # اشیاء بازی
        self.player = None
        self.enemies = []
        self.asteroids = []
        self.powerups = []
        self.projectiles = []
        self.particles = []
        self.stars = []
        
        # گرافیک سه‌بعدی
        self.camera_pos = [0, 0, 5]
        self.camera_rot = [0, 0, 0]
        self.light_pos = [2, 5, 2]
        
        # صداها
        self.sounds = {}
        self.music = None
        
        # کنترل‌ها
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = (0, 0, 0)
        
        # زمان‌بندی
        self.last_spawn_time = 0
        self.game_time = 0
        
        # تنظیمات پیشرفته
        self.graphics_quality = "HIGH"  # LOW, MEDIUM, HIGH, ULTRA
        self.particle_count = 500
        self.star_count = 1000
        
        self.initialize_game()

    def initialize_game(self):
        """راه‌اندازی اولیه بازی"""
        try:
            # راه‌اندازی Pygame و OpenGL
            pygame.init()
            pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
            pygame.display.set_caption("🚀 Galaxy Advanced 3D Game - ACTOn Studio")
            
            # تنظیمات OpenGL
            self.setup_opengl()
            
            # بارگذاری منابع
            self.load_resources()
            
            # ایجاد دنیای بازی
            self.create_game_world()
            
            # شروع موسیقی
            self.play_background_music()
            
            self.running = True
            print("✅ Galaxy 3D Engine Initialized Successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing game: {e}")
            sys.exit(1)

    def setup_opengl(self):
        """تنظیمات پیشرفته OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # تنظیم نور
        glLightfv(GL_LIGHT0, GL_POSITION, [2, 5, 2, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        
        glClearColor(0.0, 0.0, 0.1, 1.0)  # پس‌زمینه آبی تیره فضایی
        
        # تنظیم پرسپکتیو
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def load_resources(self):
        """بارگذاری منابع بازی"""
        try:
            # بارگذاری صداها
            self.load_sounds()
            
            # بارگذاری مدل‌های سه‌بعدی (ساده)
            self.create_3d_models()
            
            print("✅ Resources loaded successfully!")
            
        except Exception as e:
            print(f"⚠️ Could not load some resources: {e}")

    def load_sounds(self):
        """بارگذاری صداهای بازی"""
        try:
            # صدای موتور
            engine_sound = mixer.Sound(self.generate_sine_wave(440, 0.1))
            self.sounds['engine'] = engine_sound
            
            # صدای انفجار
            explosion_sound = mixer.Sound(self.generate_noise(0.2))
            self.sounds['explosion'] = explosion_sound
            
            # صدای سکه
            coin_sound = mixer.Sound(self.generate_sine_wave(880, 0.05))
            self.sounds['coin'] = coin_sound
            
        except Exception as e:
            print(f"⚠️ Sound loading failed: {e}")

    def generate_sine_wave(self, frequency, duration):
        """تولید موج سینوسی برای صدا"""
        sample_rate = 44100
        samples = int(sample_rate * duration)
        buffer = np.zeros((samples, 2), dtype=np.int16)
        max_amplitude = 2 ** 15 - 1
        
        for i in range(samples):
            sample = max_amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            buffer[i][0] = sample
            buffer[i][1] = sample
            
        return pygame.sndarray.make_sound(buffer)

    def generate_noise(self, duration):
        """تولید نویز برای انفجار"""
        sample_rate = 44100
        samples = int(sample_rate * duration)
        buffer = np.random.randint(-32768, 32767, (samples, 2), dtype=np.int16)
        return pygame.sndarray.make_sound(buffer)

    def create_3d_models(self):
        """ایجاد مدل‌های سه‌بعدی ساده"""
        # مدل سفینه بازیکن
        self.player_model = self.create_spaceship_model()
        
        # مدل دشمن
        self.enemy_model = self.create_enemy_model()
        
        # مدل سیارک
        self.asteroid_model = self.create_asteroid_model()
        
        # مدل سکه
        self.coin_model = self.create_coin_model()

    def create_spaceship_model(self):
        """ایجاد مدل سه‌بعدی سفینه"""
        vertices = [
            # بدنه اصلی
            [0, 0.5, 0],    # بالا
            [-0.3, -0.3, 0], # چپ پایین
            [0.3, -0.3, 0],  # راست پایین
            [0, -0.1, 0.5],  # عقب
        ]
        
        faces = [
            [0, 1, 2],  # پایه
            [0, 1, 3],  # بال چپ
            [0, 2, 3],  # بال راست
            [1, 2, 3],  # عقب
        ]
        
        return {'vertices': vertices, 'faces': faces, 'color': (0, 0.8, 1)}

    def create_enemy_model(self):
        """ایجاد مدل سه‌بعدی دشمن"""
        vertices = [
            [0, 0.3, 0],     # مرکز بالا
            [-0.4, -0.2, 0], # چپ پایین
            [0.4, -0.2, 0],  # راست پایین
            [0, -0.4, 0],    # پایین
            [0, 0, 0.3],     # جلو
        ]
        
        faces = [
            [0, 1, 2],
            [0, 1, 4],
            [0, 2, 4],
            [1, 2, 3],
            [1, 3, 4],
            [2, 3, 4],
        ]
        
        return {'vertices': vertices, 'faces': faces, 'color': (1, 0.2, 0.2)}

    def create_asteroid_model(self):
        """ایجاد مدل سه‌بعدی سیارک"""
        vertices = []
        for i in range(12):
            angle = 2 * math.pi * i / 12
            x = math.cos(angle) * (0.5 + random.random() * 0.2)
            y = math.sin(angle) * (0.5 + random.random() * 0.2)
            z = (random.random() - 0.5) * 0.3
            vertices.append([x, y, z])
        
        faces = []
        for i in range(10):
            faces.append([0, i+1, (i+2)%11])
        
        return {'vertices': vertices, 'faces': faces, 'color': (0.6, 0.6, 0.6)}

    def create_coin_model(self):
        """ایجاد مدل سه‌بعدی سکه"""
        vertices = []
        for i in range(16):
            angle = 2 * math.pi * i / 16
            x = math.cos(angle) * 0.3
            y = math.sin(angle) * 0.3
            vertices.append([x, y, 0.1])
            vertices.append([x, y, -0.1])
        
        faces = []
        for i in range(16):
            faces.append([i*2, (i*2+2)%32, (i*2+3)%32])
            faces.append([i*2, (i*2+3)%32, (i*2+1)%32])
        
        return {'vertices': vertices, 'faces': faces, 'color': (1, 0.8, 0)}

    def create_game_world(self):
        """ایجاد دنیای بازی"""
        # ایجاد بازیکن
        self.player = PlayerShip()
        
        # ایجاد ستاره‌ها
        self.create_starfield()
        
        # ایجاد سیارک‌های اولیه
        for _ in range(20):
            self.spawn_asteroid()
        
        print("✅ Game world created successfully!")

    def create_starfield(self):
        """ایجاد زمینه ستاره‌ای"""
        self.stars = []
        for _ in range(self.star_count):
            star = {
                'pos': [
                    random.uniform(-50, 50),
                    random.uniform(-50, 50),
                    random.uniform(-20, -1)
                ],
                'size': random.uniform(0.01, 0.1),
                'brightness': random.uniform(0.3, 1.0)
            }
            self.stars.append(star)

    def spawn_asteroid(self):
        """تولید سیارک جدید"""
        asteroid = {
            'pos': [
                random.uniform(-8, 8),
                random.uniform(-6, 6),
                random.uniform(-15, -5)
            ],
            'vel': [
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1),
                random.uniform(0.05, 0.2)
            ],
            'rot': [0, 0, 0],
            'rot_vel': [
                random.uniform(-2, 2),
                random.uniform(-2, 2),
                random.uniform(-2, 2)
            ],
            'size': random.uniform(0.5, 2.0),
            'health': 3
        }
        self.asteroids.append(asteroid)

    def spawn_enemy(self):
        """تولید دشمن جدید"""
        enemy = {
            'pos': [
                random.uniform(-7, 7),
                random.uniform(-5, 5),
                random.uniform(-12, -8)
            ],
            'vel': [0, 0, 0.1],
            'rot': [0, 0, 0],
            'health': 2,
            'type': random.choice(['fighter', 'bomber', 'scout']),
            'last_shot': 0,
            'shot_cooldown': random.uniform(1, 3)
        }
        self.enemies.append(enemy)

    def play_background_music(self):
        """پخش موسیقی پس‌زمینه"""
        try:
            # تولید موسیقی ساده
            music_data = self.generate_space_music(30)
            self.music = pygame.sndarray.make_sound(music_data)
            self.music.play(-1)  # تکرار بی‌نهایت
        except Exception as e:
            print(f"⚠️ Could not play music: {e}")

    def generate_space_music(self, duration):
        """تولید موسیقی فضایی"""
        sample_rate = 44100
        samples = int(sample_rate * duration)
        music = np.zeros((samples, 2), dtype=np.int16)
        
        t = np.linspace(0, duration, samples)
        
        # ملودی اصلی
        melody = 0.3 * np.sin(2 * np.pi * 220 * t)
        melody += 0.2 * np.sin(2 * np.pi * 277.18 * t)
        melody += 0.1 * np.sin(2 * np.pi * 329.63 * t)
        
        # بیس
        bass = 0.4 * np.sin(2 * np.pi * 55 * t)
        
        # افکت فضایی
        space_effect = 0.1 * np.random.normal(0, 1, samples)
        
        combined = melody + bass + space_effect
        combined = np.clip(combined, -1, 1)
        
        music[:, 0] = (combined * 32767).astype(np.int16)
        music[:, 1] = (combined * 32767).astype(np.int16)
        
        return music

    def run(self):
        """حلقه اصلی بازی"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)

    def handle_events(self):
        """مدیریت رویدادها"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.handle_keydown(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons = pygame.mouse.get_pressed()
                self.handle_mouse_click(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons = pygame.mouse.get_pressed()

    def handle_keydown(self, key):
        """مدیریت فشار دکمه"""
        if key == pygame.K_ESCAPE:
            if self.game_state == "PLAYING":
                self.game_state = "PAUSED"
            elif self.game_state == "PAUSED":
                self.game_state = "PLAYING"
        elif key == pygame.K_SPACE and self.game_state == "PLAYING":
            self.shoot_projectile()
        elif key == pygame.K_RETURN:
            if self.game_state == "MAIN_MENU":
                self.start_game()
            elif self.game_state == "GAME_OVER":
                self.restart_game()

    def handle_mouse_click(self, button):
        """مدیریت کلیک ماوس"""
        if button == 1:  # کلیک چپ
            if self.game_state == "PLAYING":
                self.shoot_projectile()

    def update(self):
        """به‌روزرسانی وضعیت بازی"""
        if self.game_state != "PLAYING":
            return

        self.game_time += 1/self.fps
        
        # به‌روزرسانی بازیکن
        self.update_player()
        
        # به‌روزرسانی دشمنان
        self.update_enemies()
        
        # به‌روزرسانی سیارک‌ها
        self.update_asteroids()
        
        # به‌روزرسانی پرتابه‌ها
        self.update_projectiles()
        
        # به‌روزرسانی ذرات
        self.update_particles()
        
        # تولید دشمنان جدید
        self.spawn_entities()
        
        # بررسی برخوردها
        self.check_collisions()
        
        # به‌روزرسانی سوخت
        self.update_fuel()

    def update_player(self):
        """به‌روزرسانی وضعیت بازیکن"""
        if not self.player:
            return

        # حرکت بر اساس کلیدها
        speed = 0.1
        if pygame.K_LEFT in self.keys_pressed:
            self.player.pos[0] -= speed
        if pygame.K_RIGHT in self.keys_pressed:
            self.player.pos[0] += speed
        if pygame.K_UP in self.keys_pressed:
            self.player.pos[1] += speed
        if pygame.K_DOWN in self.keys_pressed:
            self.player.pos[1] -= speed
            
        # محدود کردن به مرزهای صفحه
        self.player.pos[0] = max(-4, min(4, self.player.pos[0]))
        self.player.pos[1] = max(-3, min(3, self.player.pos[1]))

    def update_enemies(self):
        """به‌روزرسانی دشمنان"""
        current_time = self.game_time
        
        for enemy in self.enemies[:]:
            # حرکت به سمت بازیکن
            dx = self.player.pos[0] - enemy['pos'][0]
            dy = self.player.pos[1] - enemy['pos'][1]
            dz = self.player.pos[2] - enemy['pos'][2]
            
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            if distance > 0:
                enemy['vel'][0] = dx / distance * 0.05
                enemy['vel'][1] = dy / distance * 0.05
            
            # به‌روزرسانی موقعیت
            enemy['pos'][0] += enemy['vel'][0]
            enemy['pos'][1] += enemy['vel'][1]
            enemy['pos'][2] += enemy['vel'][2]
            
            # به‌روزرسانی چرخش
            enemy['rot'][0] += enemy.get('rot_vel', [0,0,0])[0]
            enemy['rot'][1] += enemy.get('rot_vel', [0,0,0])[1]
            enemy['rot'][2] += enemy.get('rot_vel', [0,0,0])[2]
            
            # شلیک
            if current_time - enemy['last_shot'] > enemy['shot_cooldown']:
                self.enemy_shoot(enemy)
                enemy['last_shot'] = current_time
            
            # حذف اگر خارج از صفحه شد
            if enemy['pos'][2] > 2:
                self.enemies.remove(enemy)

    def update_asteroids(self):
        """به‌روزرسانی سیارک‌ها"""
        for asteroid in self.asteroids[:]:
            # به‌روزرسانی موقعیت
            asteroid['pos'][0] += asteroid['vel'][0]
            asteroid['pos'][1] += asteroid['vel'][1]
            asteroid['pos'][2] += asteroid['vel'][2]
            
            # به‌روزرسانی چرخش
            asteroid['rot'][0] += asteroid['rot_vel'][0]
            asteroid['rot'][1] += asteroid['rot_vel'][1]
            asteroid['rot'][2] += asteroid['rot_vel'][2]
            
            # حذف اگر خارج از صفحه شد
            if asteroid['pos'][2] > 5:
                self.asteroids.remove(asteroid)
                self.spawn_asteroid()

    def update_projectiles(self):
        """به‌روزرسانی پرتابه‌ها"""
        for projectile in self.projectiles[:]:
            projectile['pos'][2] += projectile['vel'][2]
            
            # حذف اگر خارج از صفحه شد
            if abs(projectile['pos'][2]) > 20:
                self.projectiles.remove(projectile)

    def update_particles(self):
        """به‌روزرسانی ذرات"""
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                particle['pos'][0] += particle['vel'][0]
                particle['pos'][1] += particle['vel'][1]
                particle['pos'][2] += particle['vel'][2]
                particle['vel'][1] -= 0.01  # گرانش

    def spawn_entities(self):
        """تولید موجودیت‌های جدید"""
        current_time = self.game_time
        
        # تولید دشمن
        if current_time - self.last_spawn_time > 2:  # هر 2 ثانیه
            self.spawn_enemy()
            self.last_spawn_time = current_time

    def check_collisions(self):
        """بررسی برخوردها"""
        self.check_player_collisions()
        self.check_projectile_collisions()

    def check_player_collisions(self):
        """بررسی برخوردهای بازیکن"""
        player_pos = self.player.pos
        
        # برخورد با دشمنان
        for enemy in self.enemies[:]:
            if self.calculate_distance(player_pos, enemy['pos']) < 1:
                self.handle_player_hit()
                self.create_explosion(enemy['pos'])
                self.enemies.remove(enemy)
                break
        
        # برخورد با سیارک‌ها
        for asteroid in self.asteroids[:]:
            if self.calculate_distance(player_pos, asteroid['pos']) < asteroid['size']:
                self.handle_player_hit()
                self.create_explosion(asteroid['pos'])
                self.asteroids.remove(asteroid)
                break

    def check_projectile_collisions(self):
        """بررسی برخورد پرتابه‌ها"""
        for projectile in self.projectiles[:]:
            # برخورد با دشمنان
            for enemy in self.enemies[:]:
                if self.calculate_distance(projectile['pos'], enemy['pos']) < 0.5:
                    enemy['health'] -= 1
                    if enemy['health'] <= 0:
                        self.score += 100
                        self.create_explosion(enemy['pos'])
                        self.enemies.remove(enemy)
                    self.projectiles.remove(projectile)
                    break
            
            # برخورد با سیارک‌ها
            for asteroid in self.asteroids[:]:
                if self.calculate_distance(projectile['pos'], asteroid['pos']) < asteroid['size']:
                    asteroid['health'] -= 1
                    if asteroid['health'] <= 0:
                        self.score += 50
                        self.create_explosion(asteroid['pos'])
                        self.asteroids.remove(asteroid)
                        self.spawn_asteroid()
                    self.projectiles.remove(projectile)
                    break

    def calculate_distance(self, pos1, pos2):
        """محاسبه فاصله بین دو نقطه"""
        return math.sqrt(
            (pos1[0]-pos2[0])**2 + 
            (pos1[1]-pos2[1])**2 + 
            (pos1[2]-pos2[2])**2
        )

    def handle_player_hit(self):
        """مدیریت برخورد بازیکن"""
        self.lives -= 1
        self.fuel -= 20
        
        if self.lives <= 0:
            self.game_over()
        else:
            # ایجاد افکت لرزش
            self.create_screen_shake()

    def game_over(self):
        """پایان بازی"""
        self.game_state = "GAME_OVER"
        self.sounds['explosion'].play()

    def create_explosion(self, pos):
        """ایجاد انفجار"""
        self.sounds['explosion'].play()
        
        # ایجاد ذرات انفجار
        for _ in range(20):
            particle = {
                'pos': pos.copy(),
                'vel': [
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.1, 0.1)
                ],
                'life': random.randint(20, 40),
                'color': (
                    random.uniform(0.8, 1),
                    random.uniform(0.3, 0.6),
                    random.uniform(0, 0.2)
                ),
                'size': random.uniform(0.05, 0.2)
            }
            self.particles.append(particle)

    def create_screen_shake(self):
        """ایجاد افکت لرزش صفحه"""
        # پیاده‌سازی لرزش دوربین
        self.camera_pos[0] += random.uniform(-0.3, 0.3)
        self.camera_pos[1] += random.uniform(-0.3, 0.3)

    def shoot_projectile(self):
        """شلیک پرتابه"""
        if self.game_state != "PLAYING":
            return
            
        projectile = {
            'pos': self.player.pos.copy(),
            'vel': [0, 0, 0.3],
            'type': 'player',
            'damage': 1
        }
        self.projectiles.append(projectile)

    def enemy_shoot(self, enemy):
        """شلیک دشمن"""
        projectile = {
            'pos': enemy['pos'].copy(),
            'vel': [0, 0, -0.2],
            'type': 'enemy',
            'damage': 1
        }
        self.projectiles.append(projectile)

    def update_fuel(self):
        """به‌روزرسانی سوخت"""
        self.fuel = max(0, self.fuel - 0.02)
        if self.fuel <= 0:
            self.game_over()

    def render(self):
        """رندر کردن صحنه"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # تنظیم دوربین
        gluLookAt(
            self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
            0, 0, -5,
            0, 1, 0
        )
        
        if self.game_state == "PLAYING":
            self.render_game()
        elif self.game_state == "MAIN_MENU":
            self.render_main_menu()
        elif self.game_state == "PAUSED":
            self.render_game()
            self.render_pause_menu()
        elif self.game_state == "GAME_OVER":
            self.render_game()
            self.render_game_over()
        
        pygame.display.flip()

    def render_game(self):
        """رندر صحنه بازی"""
        # رسم ستاره‌ها
        self.render_stars()
        
        # رسم سیارک‌ها
        for asteroid in self.asteroids:
            self.render_asteroid(asteroid)
        
        # رسم دشمنان
        for enemy in self.enemies:
            self.render_enemy(enemy)
        
        # رسم پرتابه‌ها
        for projectile in self.projectiles:
            self.render_projectile(projectile)
        
        # رسم ذرات
        for particle in self.particles:
            self.render_particle(particle)
        
        # رسم بازیکن
        self.render_player()
        
        # رسم HUD
        self.render_hud()

    def render_stars(self):
        """رسم ستاره‌ها"""
        glBegin(GL_POINTS)
        for star in self.stars:
            glColor3f(star['brightness'], star['brightness'], star['brightness'])
            glVertex3f(star['pos'][0], star['pos'][1], star['pos'][2])
        glEnd()

    def render_player(self):
        """رسم سفینه بازیکن"""
        if not self.player:
            return
            
        glPushMatrix()
        glTranslatef(self.player.pos[0], self.player.pos[1], self.player.pos[2])
        self.draw_model(self.player_model)
        glPopMatrix()

    def render_enemy(self, enemy):
        """رسم دشمن"""
        glPushMatrix()
        glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
        glRotatef(enemy['rot'][0], 1, 0, 0)
        glRotatef(enemy['rot'][1], 0, 1, 0)
        glRotatef(enemy['rot'][2], 0, 0, 1)
        self.draw_model(self.enemy_model)
        glPopMatrix()

    def render_asteroid(self, asteroid):
        """رسم سیارک"""
        glPushMatrix()
        glTranslatef(asteroid['pos'][0], asteroid['pos'][1], asteroid['pos'][2])
        glRotatef(asteroid['rot'][0], 1, 0, 0)
        glRotatef(asteroid['rot'][1], 0, 1, 0)
        glRotatef(asteroid['rot'][2], 0, 0, 1)
        glScalef(asteroid['size'], asteroid['size'], asteroid['size'])
        self.draw_model(self.asteroid_model)
        glPopMatrix()

    def render_projectile(self, projectile):
        """رسم پرتابه"""
        glPushMatrix()
        glTranslatef(projectile['pos'][0], projectile['pos'][1], projectile['pos'][2])
        
        if projectile['type'] == 'player':
            glColor3f(0, 1, 1)  # آبی فیروزه‌ای
        else:
            glColor3f(1, 0, 0)  # قرمز
        
        glutSolidSphere(0.1, 8, 8)
        glPopMatrix()

    def render_particle(self, particle):
        """رسم ذره"""
        glPushMatrix()
        glTranslatef(particle['pos'][0], particle['pos'][1], particle['pos'][2])
        glColor3f(particle['color'][0], particle['color'][1], particle['color'][2])
        glutSolidSphere(particle['size'], 6, 6)
        glPopMatrix()

    def draw_model(self, model):
        """رسم مدل سه‌بعدی"""
        glColor3f(model['color'][0], model['color'][1], model['color'][2])
        
        glBegin(GL_TRIANGLES)
        for face in model['faces']:
            for vertex_index in face:
                vertex = model['vertices'][vertex_index]
                glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def render_hud(self):
        """رسم رابط کاربری"""
        # ذخیره حالت OpenGL
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # غیرفعال کردن نورپردازی برای HUD
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # رسم اطلاعات بازی
        self.draw_text(f"Score: {self.score}", 10, self.height - 30)
        self.draw_text(f"Level: {self.level}", 10, self.height - 60)
        self.draw_text(f"Lives: {self.lives}", 10, self.height - 90)
        self.draw_text(f"Fuel: {int(self.fuel)}%", 10, self.height - 120)
        
        # نوار سوخت
        self.draw_fuel_bar()
        
        # بازیابی حالت OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_text(self, text, x, y):
        """رسم متن (ساده)"""
        # در این نسخه ساده، از رسم متن OpenGL استفاده می‌کنیم
        glColor3f(1, 1, 1)
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

    def draw_fuel_bar(self):
        """رسم نوار سوخت"""
        bar_width = 200
        bar_height = 20
        x = 10
        y = self.height - 150
        
        # پس‌زمینه نوار
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + bar_width, y)
        glVertex2f(x + bar_width, y + bar_height)
        glVertex2f(x, y + bar_height)
        glEnd()
        
        # نوار سوخت
        fuel_width = (self.fuel / self.max_fuel) * bar_width
        if self.fuel > 50:
            glColor3f(0, 1, 0)  # سبز
        elif self.fuel > 20:
            glColor3f(1, 1, 0)  # زرد
        else:
            glColor3f(1, 0, 0)  # قرمز
            
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + fuel_width, y)
        glVertex2f(x + fuel_width, y + bar_height)
        glVertex2f(x, y + bar_height)
        glEnd()

    def render_main_menu(self):
        """رسم منوی اصلی"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # عنوان بازی
        self.draw_text("🚀 GALAXY ADVANCED 3D GAME", self.width//2 - 150, self.height//2 + 100)
        self.draw_text("ACTOn Game Studio", self.width//2 - 80, self.height//2 + 70)
        
        # دکمه‌ها
        self.draw_text("Press ENTER to Start", self.width//2 - 80, self.height//2)
        self.draw_text("Press ESC to Quit", self.width//2 - 70, self.height//2 - 40)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render_pause_menu(self):
        """رسم منوی توقف"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # پس‌زمینه نیمه شفاف
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # متن توقف
        self.draw_text("PAUSED", self.width//2 - 40, self.height//2 + 20)
        self.draw_text("Press ESC to Continue", self.width//2 - 90, self.height//2 - 20)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render_game_over(self):
        """رسم صفحه پایان بازی"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # پس‌زمینه نیمه شفاف
        glColor4f(0, 0, 0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # متن پایان بازی
        self.draw_text("GAME OVER", self.width//2 - 50, self.height//2 + 50)
        self.draw_text(f"Final Score: {self.score}", self.width//2 - 70, self.height//2)
        self.draw_text("Press ENTER to Restart", self.width//2 - 90, self.height//2 - 40)
        self.draw_text("Press ESC to Quit", self.width//2 - 70, self.height//2 - 80)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def start_game(self):
        """شروع بازی جدید"""
        self.game_state = "PLAYING"
        self.score = 0
        self.level = 1
        self.lives = 3
        self.fuel = 100
        self.player = PlayerShip()
        self.enemies.clear()
        self.asteroids.clear()
        self.projectiles.clear()
        self.particles.clear()
        self.create_game_world()

    def restart_game(self):
        """شروع مجدد بازی"""
        self.start_game()

class PlayerShip:
    """کلاس سفینه بازیکن"""
    
    def __init__(self):
        self.pos = [0, 0, -2]  # موقعیت اولیه
        self.vel = [0, 0, 0]   # سرعت
        self.rot = [0, 0, 0]   # چرخش
        self.health = 100
        self.max_health = 100
        self.speed = 0.1

def main():
    """تابع اصلی"""
    print("🚀 Starting Galaxy Advanced 3D Game...")
    print("🎮 Controls: Arrow Keys to move, SPACE to shoot, ESC to pause")
    print("🏆 Developed by ACTOn Game Studio")
    
    try:
        game = Galaxy3DEngine()
        game.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        pygame.quit()
        print("👋 Game closed successfully!")

if __name__ == "__main__":
    main()
