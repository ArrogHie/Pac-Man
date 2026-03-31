import pygame as pg
import math
from settings import *


class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []  # 光线计算结果
        self.objects_to_render = []  # 需要渲染的精灵队列
        self.texture = self.game.object_renderer.wall_texture

    def get_object_to_render(self):
        self.objects_to_render = []
        for ray, result in enumerate(self.ray_casting_result):
            depth, proj_high, texture, offset = result

            if proj_high < HIGH:
                wall_column = self.texture[texture].subsurface(offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE)
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_high))
                wall_pos = (ray * SCALE, HALF_HIGH - proj_high // 2)
            else:
                texture_high = TEXTURE_SIZE * HIGH / proj_high
                wall_column = self.texture[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE - texture_high // 2, SCALE, texture_high
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HIGH))
                wall_pos = (ray * SCALE, 0)

            self.objects_to_render.append([wall_column, wall_pos, depth])

    def raycasting(self):  # 光线算法
        self.ray_casting_result = []
        texture_vert, texture_hor = 1, 1  # 墙面类型
        ox, oy = self.game.player.pos  # 角色位置
        map_x, map_y = int(ox), int(oy)  # 角色所在地图块位置
        angle = self.game.player.angle - HALF_FOV + 0.0001  # 光线角度
        for RAYS in range(NUM_RAYS):
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            x_vert, dx = (map_x + 1, 1) if cos_a > 0 else (map_x - 1e-6, -1)  # 通过按列扫描的形式找到光线碰到哪面墙
            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            y_hor, dy = (map_y + 1, 1) if sin_a > 0 else (map_y - 1e-6, -1)  # 通过按行扫描的形式找到光线碰到哪面墙
            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = x_hor if sin_a < 0 else (1 - x_hor)

            # 消除鱼缸效应
            depth *= math.cos(self.game.player.angle - angle)
            depth = min(depth, MAX_DEPTH)

            # 墙体显示高度
            proj_high = SCREEN_DIST / (depth + 0.0001)

            self.ray_casting_result.append((depth, proj_high, texture, offset))

            # 绘制视野范围
            """pg.draw.line(
                self.game.screen,
                (205, 205, 0),
                (ox * 100, oy * 100),
                (ox * 100 + 100 * depth * cos_a, oy * 100 + 100 * depth * sin_a),
                2,
            )"""

            # 绘制第一人称视角
            """
            pg.draw.rect(self.game.screen, (proj_dark, proj_dark, proj_dark), (RAYS * SCALE, HALF_HIGH - proj_high // 2, 2, proj_high))"""

            # 计算墙体纹理

            angle += DELTA_ANGLE

    def update(self):
        self.raycasting()
        self.get_object_to_render()
