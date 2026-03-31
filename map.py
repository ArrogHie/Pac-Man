import pygame as pg
from settings import *

_ = False
x = True
string_map = """
xxxxxxxxxxxxxxxxxxxxxxxx
x                      x
x xxx x xxx xxxxxx xxx x
x xxx x xxx xxxxxx xxx x
x xx  x xxx xxxxxx  xx x
x     x xxx            x
x xxxxx xxx xxxxxxxxxx x
x xxxxx xxx xxxxxxxxxx x
x xxxxx xxx xxxxxxxxxx x
x xxxxx xxx xxxxxxxx   x
x xxx   xxx xxxxxxxx xxx
x                    xxx
x xxx   xx   xx xxx  xxx
x xxxx xxxxxxxx xxx  xxx
x xxxx      xxx xxx    x
x xxxxxxxxx xxx xxxxxx x
x xxxxxxxxx xxx xxxxxx x
x    xxxxxx xxx xxxxxx x
xxxx xxxxxx xxx xxxxxx x
xxxx                   x
x    xxxxxx xxx xxxxxx x
x xxxxxxxxx xxx xxxxxx x
x xxxxxxxxx xxx xxxxxx x
x xxxxxxxxx xxx x    x x
x                      x
x xxxxxxxxx xxx xxxxxx x
x xxxxxxxxx xxx xxxxxx x
x xxxxxxxxx xxx xxxxxx x
x     xxxxx     xxxxxx x
x xxx xxxxx xxxxxxx    x
x xxx xxxxx xxxxxxx  xxx
x  xx xxxxx xxxxxxx xxxx
x                   xxxx
xxxxxxxxxxxxxxxxxxxxxxxx
"""

mini_map = [[x if char == "x" else _ for char in line] for line in string_map.strip().splitlines()]

# 输出查看结果
"""for row in mini_map:
    print(row)"""


class Map:
    def __init__(self, game):
        self.game = game
        self.width = 16
        self.high = 9
        self.mini_map = mini_map
        self.world_map = {}
        self.get_map()
        self.canvas_map = pg.Surface((270, 270), pg.SRCALPHA)
        self.map_cx, self.map_cy = 135, 135

    def get_map(self):
        for j, row in enumerate(self.mini_map):
            for i, valve in enumerate(row):
                if valve:
                    self.world_map[(i, j)] = valve

    def draw(self):
        # 小地图绘制
        self.canvas_map.fill((0, 0, 0, 0))
        pg.draw.circle(self.canvas_map, "black", (self.map_cx, self.map_cy), self.map_cx)
        for pos in self.world_map:
            x = pos[0] - self.game.player.x
            y = pos[1] - self.game.player.y
            pg.draw.rect(self.canvas_map, "gray", (x * 30 + self.map_cx, y * 30 + self.map_cy, 30, 30))

        for pos in self.game.object_handler.bean_list.keys():
            x = pos[0] - self.game.player.x
            y = pos[1] - self.game.player.y
            pg.draw.circle(self.canvas_map, "yellow", ((x + 0.5) * 30 + self.map_cx, (y + 0.5) * 30 + self.map_cy), 2)

        pg.draw.circle(self.canvas_map, "green", (self.map_cx, self.map_cy), 8)
        angle = self.game.player.angle
        x, y = self.map_cx, self.map_cy
        b_cos = math.cos(angle - math.pi / 2)
        b_sin = math.sin(angle - math.pi / 2)
        pos1 = x + 8 * b_cos, y + 8 * b_sin
        pos2 = x - 8 * b_cos, y - 8 * b_sin
        pos3 = x + 16 * math.cos(angle), y + 16 * math.sin(angle)
        pg.draw.polygon(self.canvas_map, "green", [pos1, pos2, pos3])
        self.blit_circle_mask(self.game.screen, self.canvas_map, (0, 0))
        # self.game.screen.blit(self.canvas_map, (0, HIGH - 300))

    def blit_circle_mask(self, screen, surf, pos):
        # 创建同样大小的 mask surface（
        size = surf.get_size()
        mask = pg.Surface(size, flags=pg.SRCALPHA)
        mask.fill((0, 0, 0, 0))  # 全透明背景

        # 画一个不透明的圆形遮罩
        pg.draw.circle(mask, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), min(size) // 2)

        # 拷贝原图
        circular_surf = surf.copy()

        # 将 mask 混合到图像，保留圆形区域，其它区域变透明
        circular_surf.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # 最终 blit 到主屏幕
        screen.blit(circular_surf, pos)
