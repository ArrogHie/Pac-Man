from settings import *
import pygame as pg
import math

sqrt3 = math.sqrt(3)


class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.speed = PLAYER_SPEED
        self.rot_speed = PLAYER_ROT_SPEED
        self.radius = PLAYER_SIZE / 100  # 玩家半径（相对于地图格子）
        self.eat_radius = self.radius * 2
        self.rel = 0
        self.vis = set()
        self.eat_sound = pg.mixer.Sound("resource/audio/eat.mp3")
        self.eat_sound.set_volume(0.2)

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = self.speed * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()  # 移动

        # 疾跑判定
        if keys[pg.K_LSHIFT]:
            self.speed = PLAYER_SPEED_RUN
        else:
            self.speed = PLAYER_SPEED

        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx -= speed_cos
            dy -= speed_sin
        if keys[pg.K_a]:  # 绘图的y轴正方向向下，所以角度按顺时针为正方向
            dx += speed_sin
            dy -= speed_cos
        if keys[pg.K_d]:
            dx -= speed_sin
            dy += speed_cos

        # 防止斜向移动速度过快
        if math.fabs(dx) > math.fabs(speed_sin) and math.fabs(dx) > math.fabs(speed_cos):
            dx /= sqrt3
        if math.fabs(dy) > math.fabs(speed_sin) and math.fabs(dy) > math.fabs(speed_cos):
            dy /= sqrt3

        # 撞墙判定
        if not self.check_collision(self.x + dx, self.y):
            self.x += dx
        if not self.check_collision(self.x, self.y + dy):
            self.y += dy

        """if keys[pg.K_LEFT]:  # 视角转动
            self.angle -= self.rot_speed * self.game.delta_time
        if keys[pg.K_RIGHT]:
            self.angle += self.rot_speed * self.game.delta_time"""

        # 获取鼠标移动
        pg.mouse.set_pos(WIDTH // 2, HIGH // 2)
        rel_x, rel_y = pg.mouse.get_rel()
        self.rel = rel_x

        # 鼠标根据滑动速度调整转动速度
        self.angle -= self.rot_speed * (-rel_x / HALF_WIDTH * self.game.mouse_speed) * self.game.delta_time

        self.angle %= math.tau

    def check_collision(self, x, y):
        """检查玩家周围多个点是否碰撞"""
        # 检查玩家中心点
        if (int(x), int(y)) in self.game.map.world_map:
            return True

        # 检查玩家周围的点（根据玩家半径）
        r = self.radius
        points_to_check = [
            (x + r, y),  # 右
            (x - r, y),  # 左
            (x, y + r),  # 下
            (x, y - r),  # 上
            (x + r, y + r),  # 右下
            (x + r, y - r),  # 右上
            (x - r, y + r),  # 左下
            (x - r, y - r),  # 左上
        ]

        for px, py in points_to_check:
            if (int(px), int(py)) in self.game.map.world_map:
                return True

        return False

    # 角色位置绘制
    def draw(self):
        pg.draw.circle(self.game.screen, (135, 206, 250), (self.x * TEST_SIZE, self.y * TEST_SIZE), 10)
        pg.draw.line(
            self.game.screen,
            "yellow",
            (self.x * TEST_SIZE, self.y * TEST_SIZE),
            (self.x * TEST_SIZE + WIDTH * math.cos(self.angle), self.y * TEST_SIZE + WIDTH * math.sin(self.angle)),
            2,
        )

    # 监测吃豆
    def eat(self):
        pos = (int(self.x), int(self.y))
        if math.fabs(self.x - pos[0] - 0.5) <= self.eat_radius and math.fabs(self.y - pos[1] - 0.5) <= self.eat_radius:
            if pos not in self.vis:
                self.vis.add(pos)
                self.game.score -= 1
                self.game.object_handler.sprite_list.remove(self.game.object_handler.bean_list[pos])
                del self.game.object_handler.bean_list[pos]
                self.eat_sound.play()

    def update(self):
        self.movement()
        self.eat()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
