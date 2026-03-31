import pygame as pg
import math
from settings import *
import os
from collections import deque


class SpriteObject:
    # scale缩放 shift竖直偏移量
    def __init__(self, game, path="resource/sprite/static_sprite/candlebra.png", pos=(8.5, 3.5), scale=1.0, shift=0.3):
        self.x, self.y = pos
        self.game = game
        self.player = game.player
        self.img = pg.image.load(path).convert_alpha()
        self.WIDTH = self.img.get_width()
        self.HALF_WIDTH = self.WIDTH // 2
        self.HIGH = self.img.get_height()
        self.IMAGE_RATIO = self.WIDTH / self.HIGH
        self.SPRITE_SCALE = scale
        self.SPRITE_HIGH_SHIFT = shift

    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.dist * self.SPRITE_SCALE
        proj_width, proj_high = proj * self.IMAGE_RATIO, proj

        img = pg.transform.scale(self.img, (proj_width, proj_high))
        half_width = proj_width // 2
        high_shift = proj_high * self.SPRITE_HIGH_SHIFT
        pos = self.screen_x - half_width, HALF_HIGH - proj_high // 2 + high_shift
        self.game.raycasting.objects_to_render.append((img, pos, self.dist))

    # 计算在屏幕上渲染的位置
    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y

        theta = math.atan2(dy, dx)  # 计算和玩家视角中心的角度差
        delta = theta - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.dist = math.sqrt(dx**2 + dy**2)
        self.dist *= math.cos(delta)

        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE
        if -self.HALF_WIDTH < self.screen_x < (WIDTH + self.HALF_WIDTH):
            self.get_sprite_projection()

    def update(self):
        self.get_sprite()
        if NPC_DRAW:
            pg.draw.circle(self.game.screen, "white", (self.x * TEST_SIZE, self.y * TEST_SIZE), 2)


class AnimatedSprite(SpriteObject):
    # animation_time 动画时间
    def __init__(self, game, path="resource/sprite/animated_sprite/green_light/0.png", pos=(9.5, 3.5), scale=0.8, shift=0.3, animation_time=120):
        super().__init__(game, path, pos, scale, shift)
        self.animation_time = animation_time
        self.path = path.rsplit("/", 1)[0]
        self.images = self.get_images(self.path)
        self.animation_time_prev = pg.time.get_ticks()  # 动画间隔
        self.animation_trigger = False  # 是否绘制下一张

    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.img = images[0]

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path):
        images = deque()

        # 录入动画文件
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + "/" + file_name).convert_alpha()
                images.append(img)
        return images
