import math
import random
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

@dataclass
class Vector3:
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector3(self.x/length, self.y/length, self.z/length)
        return Vector3(0, 0, 0)

class GameObject:
    """کلاس پایه برای تمام اشیاء بازی"""
    
    def __init__(self, position: Vector3, rotation: Vector3 = None):
        self.position = position
        self.rotation = rotation or Vector3(0, 0, 0)
        self.velocity = Vector3(0, 0, 0)
        self.scale = Vector3(1, 1, 1)
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        
    def update(self, delta_time: float):
        """به‌روزرسانی وضعیت شیء"""
        self.position = self.position + self.velocity * delta_time
        
    def take_damage(self, damage: int):
        """دریافت آسیب"""
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
            self.on_death()
    
    def on_death(self):
        """وقتی شیء از بین می‌رود"""
        pass

class PlayerShip(GameObject):
    """سفینه بازیکن"""
    
    def __init__(self):
        super().__init__(Vector3(0, 0, -2))
        self.speed = 5.0
        self.rotation_speed = 2.0
        self.weapon_cooldown = 0.0
        self.weapon_rate = 0.2  # شلیک در هر ثانیه
        self.invulnerable = 0.0
        
    def update(self, delta_time: float):
        super().update(delta_time)
        
        # به‌روزرسانی زمان‌سنج‌ها
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= delta_time
            
        if self.invulnerable > 0:
            self.invulnerable -= delta_time
    
    def move(self, direction: Vector3, delta_time: float):
        """حرکت سفینه"""
        self.velocity = direction.normalize() * self.speed
        
    def rotate(self, rotation: Vector3, delta_time: float):
        """چرخش سفینه"""
        self.rotation.x += rotation.x * self.rotation_speed * delta_time
        self.rotation.y += rotation.y * self.rotation_speed * delta_time
        self.rotation.z += rotation.z * self.rotation_speed * delta_time
        
    def can_shoot(self) -> bool:
        """آیا می‌تواند شلیک کند؟"""
        return self.weapon_cooldown <= 0
        
    def shoot(self):
        """شلیک کردن"""
        if self.can_shoot():
            self.weapon_cooldown = 1.0 / self.weapon_rate
            return Projectile(
                self.position + Vector3(0, 0, 0.5),
                Vector3(0, 0, 1),
                "player"
            )
        return None
        
    def take_damage(self, damage: int):
        """دریافت آسیب با در نظر گرفتن حالت آسیب‌ناپذیر"""
        if self.invulnerable <= 0:
            super().take_damage(damage)
            self.invulnerable = 1.0  # 1 ثانیه آسیب‌ناپذیر

class EnemyShip(GameObject):
    """سفینه دشمن"""
    
    def __init__(self, position: Vector3, enemy_type: str = "fighter"):
        super().__init__(position)
        self.enemy_type = enemy_type
        self.speed = 2.0
        self.weapon_cooldown = 0.0
        self.detection_range = 10.0
        self.attack_range = 5.0
        
        # تنظیمات بر اساس نوع دشمن
        if enemy_type == "fighter":
            self.health = 50
            self.max_health = 50
            self.weapon_rate = 1.0
        elif enemy_type == "bomber":
            self.health = 100
            self.max_health = 100
            self.weapon_rate = 0.5
        elif enemy_type == "scout":
            self.health = 30
            self.max_health = 30
            self.weapon_rate = 2.0
            
    def update(self, delta_time: float, player_position: Vector3):
        """به‌روزرسانی دشمن"""
        super().update(delta_time)
        
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= delta_time
            
        # AI ساده برای تعقیب بازیکن
        direction = player_position - self.position
        distance = direction.length()
        
        if distance < self.detection_range:
            # حرکت به سمت بازیکن
            if distance > self.attack_range:
                self.velocity = direction.normalize() * self.speed
            else:
                # مانور در فاصله حمله
                self.velocity = Vector3(0, 0, 0)
                
    def can_shoot(self, player_position: Vector3) -> bool:
        """آیا می‌تواند به بازیکن شلیک کند؟"""
        if self.weapon_cooldown > 0:
            return False
            
        direction = player_position - self.position
        return direction.length() <= self.attack_range
        
    def shoot(self, player_position: Vector3):
        """شلیک به سمت بازیکن"""
        if self.can_shoot(player_position):
            self.weapon_cooldown = 1.0 / self.weapon_rate
            direction = (player_position - self.position).normalize()
            return Projectile(
                self.position,
                direction,
                "enemy"
            )
        return None

class Asteroid(GameObject):
    """سیارک"""
    
    def __init__(self, position: Vector3, size: float = 1.0):
        super().__init__(position)
        self.size = size
        self.rotation_velocity = Vector3(
            random.uniform(-2, 2),
            random.uniform(-2, 2),
            random.uniform(-2, 2)
        )
        
        # سلامت بر اساس اندازه
        self.health = int(size * 20)
        self.max_health = self.health
        
    def update(self, delta_time: float):
        super().update(delta_time)
        
        # چرخش سیارک
        self.rotation.x += self.rotation_velocity.x * delta_time
        self.rotation.y += self.rotation_velocity.y * delta_time
        self.rotation.z += self.rotation_velocity.z * delta_time

class Projectile(GameObject):
    """پرتابه"""
    
    def __init__(self, position: Vector3, direction: Vector3, owner: str):
        super().__init__(position)
        self.direction = direction
        self.speed = 10.0
        self.owner = owner  # "player" یا "enemy"
        self.damage = 25 if owner == "player" else 10
        self.lifetime = 3.0  # زمان زندگی بر حسب ثانیه
        
    def update(self, delta_time: float):
        self.position = self.position + self.direction * self.speed * delta_time
        self.lifetime -= delta_time
        
        if self.lifetime <= 0:
            self.is_alive = False

class PowerUp(GameObject):
    """قدرت‌افزایی"""
    
    def __init__(self, position: Vector3, power_type: str):
        super().__init__(position)
        self.power_type = power_type  # "health", "fuel", "weapon", "shield"
        self.rotation_velocity = Vector3(0, 2, 0)
        
    def update(self, delta_time: float):
        super().update(delta_time)
        
        # چرخش آرام
        self.rotation.y += self.rotation_velocity.y * delta_time

class ParticleSystem:
    """سیستم ذرات برای افکت‌های بصری"""
    
    def __init__(self):
        self.particles = []
        
    def create_explosion(self, position: Vector3, count: int = 20):
        """ایجاد افکت انفجار"""
        for _ in range(count):
            particle = {
                'position': Vector3(position.x, position.y, position.z),
                'velocity': Vector3(
                    random.uniform(-2, 2),
                    random.uniform(-2, 2),
                    random.uniform(-1, 1)
                ),
                'life': random.uniform(0.5, 2.0),
                'max_life': 2.0,
                'size': random.uniform(0.1, 0.3),
                'color': (
                    random.uniform(0.8, 1.0),
                    random.uniform(0.3, 0.6),
                    random.uniform(0.0, 0.2)
                )
            }
            self.particles.append(particle)
            
    def create_engine_trail(self, position: Vector3, velocity: Vector3):
        """ایجاد رد موتور"""
        particle = {
            'position': Vector3(position.x, position.y, position.z),
            'velocity': velocity * -0.5 + Vector3(
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1)
            ),
            'life': random.uniform(0.3, 1.0),
            'max_life': 1.0,
            'size': random.uniform(0.05, 0.15),
            'color': (0.2, 0.8, 1.0)
        }
        self.particles.append(particle)
        
    def update(self, delta_time: float):
        """به‌روزرسانی تمام ذرات"""
        for particle in self.particles[:]:
            # به‌روزرسانی موقعیت
            particle['position'] = particle['position'] + particle['velocity'] * delta_time
            
            # کاهش عمر
            particle['life'] -= delta_time
            
            # حذف ذرات مرده
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def get_particles(self):
        """دریافت لیست ذرات"""
        return self.particles

class GameWorld:
    """مدیر دنیای بازی"""
    
    def __init__(self):
        self.player = None
        self.enemies = []
        self.asteroids = []
        self.projectiles = []
        self.powerups = []
        self.particle_system = ParticleSystem()
        
    def spawn_enemy(self, position: Vector3, enemy_type: str = "fighter"):
        """تولید دشمن جدید"""
        enemy = EnemyShip(position, enemy_type)
        self.enemies.append(enemy)
        return enemy
        
    def spawn_asteroid(self, position: Vector3 = None, size: float = None):
        """تولید سیارک جدید"""
        if position is None:
            position = Vector3(
                random.uniform(-15, 15),
                random.uniform(-10, 10),
                random.uniform(-20, -10)
            )
            
        if size is None:
            size = random.uniform(0.5, 3.0)
            
        asteroid = Asteroid(position, size)
        self.asteroids.append(asteroid)
        return asteroid
        
    def spawn_powerup(self, position: Vector3, power_type: str):
        """تولید قدرت‌افزایی جدید"""
        powerup = PowerUp(position, power_type)
        self.powerups.append(powerup)
        return powerup
        
    def update(self, delta_time: float):
        """به‌روزرسانی تمام موجودیت‌های دنیا"""
        # به‌روزرسانی بازیکن
        if self.player:
            self.player.update(delta_time)
            
        # به‌روزرسانی دشمنان
        for enemy in self.enemies[:]:
            if self.player:
                enemy.update(delta_time, self.player.position)
            if not enemy.is_alive:
                self.enemies.remove(enemy)
                self.particle_system.create_explosion(enemy.position)
                
        # به‌روزرسانی سیارک‌ها
        for asteroid in self.asteroids[:]:
            asteroid.update(delta_time)
            if not asteroid.is_alive:
                self.asteroids.remove(asteroid)
                self.particle_system.create_explosion(asteroid.position, 30)
                
        # به‌روزرسانی پرتابه‌ها
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)
            if not projectile.is_alive:
                self.projectiles.remove(projectile)
                
        # به‌روزرسانی قدرت‌افزایی‌ها
        for powerup in self.powerups[:]:
            powerup.update(delta_time)
            
        # به‌روزرسانی سیستم ذرات
        self.particle_system.update(delta_time)
        
    def check_collisions(self):
        """بررسی برخورد بین موجودیت‌ها"""
        if not self.player:
            return
            
        # برخورد پرتابه‌ها با دشمنان
        for projectile in self.projectiles[:]:
            if projectile.owner == "player":
                for enemy in self.enemies[:]:
                    if self.is_colliding(projectile, enemy):
                        enemy.take_damage(projectile.damage)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break
                        
            elif projectile.owner == "enemy":
                if self.is_colliding(projectile, self.player):
                    self.player.take_damage(projectile.damage)
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                        
        # برخورد بازیکن با دشمنان
        for enemy in self.enemies[:]:
            if self.is_colliding(self.player, enemy):
                self.player.take_damage(10)
                enemy.take_damage(20)
                
        # برخورد بازیکن با سیارک‌ها
        for asteroid in self.asteroids[:]:
            if self.is_colliding(self.player, asteroid):
                self.player.take_damage(15)
                asteroid.take_damage(50)
                
        # برخورد بازیکن با قدرت‌افزایی‌ها
        for powerup in self.powerups[:]:
            if self.is_colliding(self.player, powerup):
                self.apply_powerup(self.player, powerup.power_type)
                self.powerups.remove(powerup)
                
    def is_colliding(self, obj1: GameObject, obj2: GameObject) -> bool:
        """بررسی برخورد بین دو شیء"""
        distance = (obj1.position - obj2.position).length()
        
        # شعاع برخورد ساده
        radius1 = getattr(obj1, 'size', 1.0) if isinstance(obj1, Asteroid) else 0.5
        radius2 = getattr(obj2, 'size', 1.0) if isinstance(obj2, Asteroid) else 0.5
        
        return distance < (radius1 + radius2)
        
    def apply_powerup(self, player: PlayerShip, power_type: str):
        """اعمال قدرت‌افزایی به بازیکن"""
        if power_type == "health":
            player.health = min(player.max_health, player.health + 30)
        elif power_type == "fuel":
            # در اینجا می‌توان سوخت را افزایش داد
            pass
        elif power_type == "weapon":
            player.weapon_rate *= 1.5  # افزایش سرعت شلیک
        elif power_type == "shield":
            player.invulnerable = 5.0  # 5 ثانیه آسیب‌ناپذیری
            
    def get_all_entities(self):
        """دریافت تمام موجودیت‌های دنیا"""
        entities = []
        if self.player:
            entities.append(self.player)
        entities.extend(self.enemies)
        entities.extend(self.asteroids)
        entities.extend(self.projectiles)
        entities.extend(self.powerups)
        return entities
