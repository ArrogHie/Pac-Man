import pygame as pg
from settings import *


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_texture = self.load_wall_texture()
        self.sky_img = self.get_texture("resource/textures/sky.png", (WIDTH, HALF_HIGH))
        self.sky_offset = 0
        self.floor_surface = pg.Surface((WIDTH, HALF_HIGH), pg.SRCALPHA)
        self.floor_init()

    def floor_init(self):
        for y in range(0, HALF_HIGH):
            # 计算标准化位置（0底部到1顶部）
            normalized_pos = 1 - y / HALF_HIGH

            # 幂级数亮度系数（0-1范围）
            brightness_factor = 1 - normalized_pos**0.5

            # 应用渐变（越靠近底部越亮）
            r = min(int(30 * brightness_factor), 255)
            g = min(int(30 * brightness_factor), 255)
            b = min(int(30 * brightness_factor), 255)

            # 绘制水平线
            pg.draw.line(self.floor_surface, (r, g, b), (0, y), (WIDTH, y))

    def draw(self):
        self.draw_background()
        self.render_game_objects()

    def draw_background(self):
        # 根据鼠标偏移量绘制天空
        self.sky_offset = (self.sky_offset + 0.65 * self.game.mouse_speed / 20 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_img, (-self.sky_offset, 0))
        self.screen.blit(self.sky_img, (-self.sky_offset + WIDTH, 0))

        # 绘制地面
        self.screen.blit(self.floor_surface, (0, HALF_HIGH))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[2], reverse=True)
        for img, pos, depth in list_objects:
            # self.screen.blit(img, pos)

            k = 4.0 / MAX_DEPTH  # 可调节系数，2.0 是经验值
            brightness = math.exp(-k * depth)
            brightness = max(0.0, min(1.0, brightness))  # 限制在 [0,1]

            # === 创建亮度遮罩（保持 alpha 通道为 255） ===
            mask = pg.Surface(img.get_size(), flags=pg.SRCALPHA)
            shade = int(255 * brightness)
            mask.fill((shade, shade, shade, 255))  # 仅调整 RGB，保持透明区域

            img.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

            # === 渲染到屏幕 ===
            self.screen.blit(img, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()  # 导入带透明度的图片
        return pg.transform.scale(texture, res)  # 缩放图片

    def load_wall_texture(self):
        return {1: self.get_texture("resource/textures/1.png")}
