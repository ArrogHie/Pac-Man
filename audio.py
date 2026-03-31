import pygame
import math


class AudioSource:
    def __init__(self, game, sound_path, max_distance=8):
        """
        :param game: 主游戏对象，用于访问 player 坐标与朝向
        :param sound_path: 音频文件路径
        :param pos: 音源位置 (x, y)
        :param max_distance: 超出该距离音量为0
        """
        self.game = game
        self.max_distance = max_distance
        self.min_distance = 0.5
        self.len = max_distance - 0.5
        self.sound = pygame.mixer.Sound(sound_path)
        self.channel = None  # 声道对象
        self.is_playing = False  # 播放状态标记
        self.play()

    def play(self):
        if not self.is_playing:
            self.channel = self.sound.play(loops=-1)
            if self.channel:
                self.channel.set_volume(0, 0)
                self.is_playing = True

    def stop(self):
        if self.channel:
            self.channel.stop()
            self.is_playing = False

    def update(self, pos):
        if not self.is_playing or not self.channel:
            return

        player_x = self.game.player.x
        player_y = self.game.player.y
        player_angle = self.game.player.angle

        dx = pos[0] - player_x
        dy = pos[1] - player_y
        distance = math.hypot(dx, dy)

        # 距离 → 音量（指数衰减）
        if distance > self.max_distance:
            volume = 0.0
        else:
            k = 4 / self.len
            volume = math.exp(-k * (distance - self.min_distance))

        # 玩家朝向与音源方向的夹角
        player_dir = (math.cos(player_angle), math.sin(player_angle))
        to_sound = (dx / (distance + 1e-6), dy / (distance + 1e-6))

        dot = player_dir[0] * to_sound[0] + player_dir[1] * to_sound[1]
        cross = player_dir[0] * to_sound[1] - player_dir[1] * to_sound[0]

        angle = math.acos(max(min(dot, 1), -1))
        pan = cross  # -1 左，+1 右

        pan = max(-1.0, min(1.0, pan))
        left = volume * (1 - pan) / 2
        right = volume * (1 + pan) / 2

        self.channel.set_volume(left, right)
