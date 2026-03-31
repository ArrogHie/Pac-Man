import pygame as pg
import os
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *


class Button:
    def __init__(self, x, y, width, height, text, game):
        self.rect = pg.Rect(0, y, WIDTH, height)
        self.text = text
        self.state = "normal"  # normal, hover, clicked
        self.game = game
        self.font = pg.font.SysFont(None, 48)

    def draw(self, surface):
        # 根据状态选择颜色
        if self.state == "hover" or self.state == "clicked":
            Rect = pg.Surface((self.rect[2], self.rect[3]), pg.SRCALPHA)
            pg.draw.rect(Rect, (128, 128, 128, 40), (0, 0, self.rect[2], self.rect[3]))
            surface.blit(Rect, (self.rect[0], self.rect[1]))

        # 绘制文字
        text_surf = self.font.render(self.text, True, (220, 220, 220))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.state = "hover"
            return True
        self.state = "normal"
        return False

    def check_click(self, pos, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.state = "clicked"
                return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.state = "hover" if self.rect.collidepoint(pos) else "normal"
        return False


class Slider:
    def __init__(self, x, y, width, height, game):
        self.rect = pg.Rect(x, y, width, height)
        self.min_val = 5
        self.max_val = 100
        self.value = MOUSE_SPEED
        self.handle_rect = pg.Rect(x + int(self.value * width) - 10, y - 10, 20, 40)
        self.dragging = False
        self.game = game
        self.font = pg.font.SysFont(None, 36)

    def draw(self, surface):
        # 绘制滑动条背景
        pg.draw.rect(surface, "black", self.rect, border_radius=10)

        # 绘制填充部分
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pg.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pg.draw.rect(surface, "white", fill_rect, border_radius=10)

        # 绘制手柄
        pg.draw.rect(surface, (200, 200, 200), self.handle_rect, border_radius=8)
        pg.draw.rect(surface, (50, 50, 50), self.handle_rect, 2, border_radius=8)

        # 绘制数值
        value_text = self.font.render(f"Mouse sensitivity: {self.value:.2f}", True, (220, 220, 220))
        surface.blit(value_text, (self.rect.x, self.rect.y - 40))

    def update(self, pos, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.handle_rect.centerx = max(self.rect.left, min(event.pos[0], self.rect.right))
                    relative_pos = (self.handle_rect.centerx - self.rect.left) / self.rect.width
                    self.value = self.min_val + relative_pos * (self.max_val - self.min_val)
                    self.value = max(self.min_val, min(self.value, self.max_val))

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

        if self.dragging:
            self.handle_rect.centerx = max(self.rect.left, min(pos[0], self.rect.right))
            relative_pos = (self.handle_rect.centerx - self.rect.left) / self.rect.width
            self.value = self.min_val + relative_pos * (self.max_val - self.min_val)
            self.value = max(self.min_val, min(self.value, self.max_val))

        self.game.mouse_speed = self.value


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.score = 0
        self.mouse_speed = MOUSE_SPEED

        # 加载菜单背景图
        menu_img = pg.image.load("resource/textures/menu.png").convert_alpha()
        menu_img_ratio = menu_img.get_height() / menu_img.get_width()
        self.menu_width = WIDTH // 2
        self.menu_img = pg.transform.scale(menu_img, (self.menu_width, int(menu_img_ratio * self.menu_width)))

        # 游戏状态
        self.menu_active = True
        self.settings_active = False
        self.victory_active = False

        # 失败动画相关属性
        self.failure_animation_active = False
        self.failure_frames = []
        self.current_frame_index = 0
        self.frame_delay = 20  # 每帧显示时间(毫秒)
        self.last_frame_time = 0
        self.game_over_condition = False

        # 加载失败动画帧
        self.load_failure_animation("resource/failure_animation")

        # 创建菜单按钮
        button_width, button_height = 300, 80
        center_x = WIDTH // 2 - button_width // 2

        self.start_button = Button(center_x, 500, button_width, button_height, "Start", self)
        self.settings_button = Button(center_x, 600, button_width, button_height, "Settings", self)
        self.exit_button = Button(center_x, 700, button_width, button_height, "Quit", self)
        self.back_button = Button(center_x, 700, button_width, 60, "Back", self)

        # 创建滑动条
        slider_width, slider_height = 300, 20
        self.volume_slider = Slider(center_x, 600, slider_width, slider_height, self)

        # 创建字体
        self.title_font = pg.font.SysFont(None, 72)
        self.menu_font = pg.font.SysFont(None, 48)
        self.victory_font = pg.font.SysFont(None, 100)

        # 初始化游戏对象
        self.map = None
        self.player = None
        self.object_renderer = None
        self.object_handler = None
        self.raycasting = None

    def load_failure_animation(self, folder_path):
        """加载失败动画的连续帧"""
        try:
            # 获取文件夹中所有图片文件
            image_files = [f for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))]
            image_files.sort()  # 确保按文件名顺序加载

            for filename in image_files:
                img_path = os.path.join(folder_path, filename)
                img = pg.image.load(img_path).convert_alpha()
                # 缩放图片到适合屏幕大小
                img = pg.transform.scale(img, (WIDTH, HIGH))
                self.failure_frames.append(img)

            if not self.failure_frames:
                print("警告: 没有找到失败动画帧图片!")

        except Exception as e:
            print(f"加载失败动画错误: {e}")

    def start_failure_animation(self):
        """开始播放失败动画"""
        self.failure_animation_active = True
        self.current_frame_index = 0
        self.last_frame_time = pg.time.get_ticks()
        # 隐藏鼠标
        pg.mouse.set_visible(False)

    def update_failure_animation(self):
        """更新失败动画帧"""
        current_time = pg.time.get_ticks()
        if current_time - self.last_frame_time > self.frame_delay:
            self.last_frame_time = current_time
            self.current_frame_index += 1

            # 动画播放完毕
            if self.current_frame_index >= len(self.failure_frames):
                self.end_failure_animation()

    def end_failure_animation(self):
        """结束失败动画并返回主菜单"""
        self.failure_animation_active = False
        self.menu_active = True
        self.game_over_condition = False
        # 显示鼠标
        pg.mouse.set_visible(True)

    def draw_failure_animation(self):
        """绘制当前失败动画帧"""
        if 0 <= self.current_frame_index < len(self.failure_frames):
            self.screen.blit(self.failure_frames[self.current_frame_index], (0, 0))

    def new_game(self):
        # 初始化游戏对象
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.object_handler = ObjectHandler(self)
        self.raycasting = RayCasting(self)

        # 重置游戏状态
        self.score = len(self.object_handler.bean_list)
        self.game_over_condition = False
        self.victory_active = False

        # 设置鼠标状态
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def update(self):
        if self.failure_animation_active:
            self.update_failure_animation()
        elif not self.menu_active and not self.settings_active:
            # 只有在游戏状态下才更新游戏逻辑
            self.player.update()
            self.raycasting.update()
            self.object_handler.update()

            # 检查胜利条件
            if self.score <= 0:
                self.victory_active = True
                self.object_handler.update()  # 停止音效
                pg.mouse.set_visible(True)
                pg.event.set_grab(False)

            # 检查失败条件
            if self.game_over_condition and not self.failure_animation_active:
                self.object_handler.update()
                self.start_failure_animation()

        pg.display.flip()

    def draw(self):
        if self.failure_animation_active:
            self.draw_failure_animation()
        elif not self.menu_active and not self.settings_active:
            # 游戏状态下的绘制
            self.object_renderer.draw()
            self.map.draw()

            # 绘制分数
            score_text = self.menu_font.render(f"{self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (HALF_WIDTH, 20))

            settings_text = self.menu_font.render("Press shift to run", True, "white")
            self.screen.blit(settings_text, (20, 800))

    def check_game_events(self):
        if self.failure_animation_active:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            return
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                # 按ESC返回主菜单
                self.menu_active = True
                self.object_handler.update()  # 停止音效
                pg.mouse.set_visible(True)
                pg.event.set_grab(False)
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # 测试用：按空格键改变分数
                self.score -= 100
            elif event.type == pg.KEYDOWN and event.key == pg.K_g:
                # 测试用：按G键触发游戏失败
                self.game_over_condition = True

    def check_menu_events(self):
        mouse_pos = pg.mouse.get_pos()
        events = pg.event.get()

        if self.failure_animation_active:
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            return

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.settings_active:
                    self.settings_active = False
                else:
                    pg.quit()
                    sys.exit()

            # 主菜单按钮处理
            if not self.settings_active and not self.victory_active:
                if self.start_button.check_click(mouse_pos, event):
                    self.menu_active = False
                    self.settings_active = False
                    self.victory_active = False
                    self.new_game()
                elif self.settings_button.check_click(mouse_pos, event):
                    self.settings_active = True
                elif self.exit_button.check_click(mouse_pos, event):
                    pg.quit()
                    sys.exit()

            # 设置菜单按钮处理
            elif self.settings_active:
                if self.back_button.check_click(mouse_pos, event):
                    self.settings_active = False

            # 胜利画面按钮处理
            elif self.victory_active:
                if self.start_button.check_click(mouse_pos, event):
                    self.victory_active = False
                    self.new_game()
                elif self.back_button.check_click(mouse_pos, event):
                    self.victory_active = False
                    self.menu_active = True

        # 更新UI状态
        if self.menu_active and not self.settings_active and not self.victory_active:
            self.start_button.check_hover(mouse_pos)
            self.settings_button.check_hover(mouse_pos)
            self.exit_button.check_hover(mouse_pos)
        elif self.settings_active:
            self.back_button.check_hover(mouse_pos)
            self.volume_slider.update(mouse_pos, events)
        elif self.victory_active:
            self.start_button.check_hover(mouse_pos)
            self.back_button.check_hover(mouse_pos)

    def draw_menu(self):
        # 绘制背景
        self.screen.fill("black")
        self.screen.blit(self.menu_img, (HALF_WIDTH - self.menu_width // 2, 0))

        if self.settings_active:
            # 绘制设置菜单
            settings_text = self.menu_font.render("Settings", True, "white")
            self.screen.blit(settings_text, (WIDTH // 2 - settings_text.get_width() // 2, 450))

            self.volume_slider.draw(self.screen)
            self.back_button.draw(self.screen)
        elif self.victory_active:
            # 绘制胜利画面
            victory_text = self.victory_font.render("YOU WIN!", True, "white")
            self.screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, 450))
            self.back_button.draw(self.screen)
        else:
            # 绘制主菜单
            self.start_button.draw(self.screen)
            self.settings_button.draw(self.screen)
            self.exit_button.draw(self.screen)

        pg.display.flip()

    def run(self):
        pygame.display.set_caption("吃豆神人")
        while True:
            if self.failure_animation_active:
                # 失败动画模式
                self.check_game_events()  # 处理事件（包括跳过）
                self.update()
                self.draw()
                self.clock.tick(FPS)
            elif self.menu_active or self.settings_active or self.victory_active:
                # 菜单/设置/胜利模式
                self.check_menu_events()
                self.draw_menu()
                self.clock.tick(FPS)
            else:
                # 游戏模式
                self.check_game_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
