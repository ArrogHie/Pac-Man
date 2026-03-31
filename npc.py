from sprite_object import *
from random import randint, random, choice
from collections import deque
from audio import *

SCATTER, CHASE, PAUSE = 0, 1, 2

directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
directions_key = {(-1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}


class NPC(AnimatedSprite):

    def __init__(
        self,
        game,
        path="resource/sprite/npc/ghost/Blinky/0.png",
        pos=(9.5, 4.5),
        scale=1,
        shift=0,
        animation_time=180,
        home=(1, 1),
        sound_path="resource/audio/pop.mp3",
    ):
        super().__init__(game, path, pos, scale, shift, animation_time)

        self.home = home
        self.speed = NPC_SPEED
        self.size = 30
        self.model = SCATTER
        self.dirc = 0
        self.radius = self.size / 100
        self.change_time = 0
        self.change_need_time = CHANGE_TIME[0] * FPS  # 状态切换时间
        self.change_not = 0  # 切换次数

        self.bgm = AudioSource(game, sound_path)

    def action(self):
        pass

    def update(self):
        super().update()
        self.check_animation_time()
        self.get_sprite()
        self.action()
        self.bgm.update((self.x, self.y))
        if math.sqrt((self.x - self.game.player.x) ** 2 + (self.y - self.game.player.y) ** 2) < 0.5:
            self.game.game_over_condition = True

        if self.game.game_over_condition or self.game.menu_active or self.game.victory_active:
            self.bgm.stop()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def movement(self, gold):
        # 1. 检查是否在格子中心
        current_cell = (int(self.x), int(self.y))
        target_center = (current_cell[0] + 0.5, current_cell[1] + 0.5)
        distance_to_center = math.sqrt((self.x - target_center[0]) ** 2 + (self.y - target_center[1]) ** 2)
        self.at_center = distance_to_center < 0.05

        # 2. 如果在格子中心，重新选择方向
        if self.at_center or self.next_cell is None:
            self.next_cell = self.get_next_cell(current_cell, gold)

            # 如果无法找到路径，尝试掉头
            if self.next_cell is None:
                dx, dy = directions[(self.dirc + 2) % 4]
                self.next_cell = (current_cell[0] + dx, current_cell[1] + dy)
                if not self.check_wall(*self.next_cell):
                    self.dirc = (self.dirc + 2) % 4  # 更新方向为掉头

        # pg.draw.rect(self.game.screen, "blue", (self.next_cell[0] * 100, self.next_cell[1] * 100, 100, 100))

        # 3. 计算移动方向
        target_center = (self.next_cell[0] + 0.5, self.next_cell[1] + 0.5)
        dx = target_center[0] - self.x
        dy = target_center[1] - self.y
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        # 4. 移动NPC
        speed = self.speed * self.game.delta_time
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed

        # 5. 检查碰撞
        if self.check_wall(int(new_x), int(self.y)):
            self.x = new_x
        if self.check_wall(int(self.x), int(new_y)):
            self.y = new_y

    def get_next_cell(self, current_cell, gold):
        """选择下一个移动格子（吃豆人幽灵逻辑）"""
        # 获取三个候选方向：前方、左方、右方
        candidate_dirs = [self.dirc, (self.dirc + 3) % 4, (self.dirc + 1) % 4]  # 当前方向  # 左转  # 右转

        # 排除掉头方向
        candidate_dirs = [d for d in candidate_dirs if d != (self.dirc + 2) % 4]

        # 获取可行方向
        possible_dirs = []
        for d in candidate_dirs:
            dx, dy = directions[d]
            next_cell = (current_cell[0] + dx, current_cell[1] + dy)
            if self.check_wall(*next_cell):
                possible_dirs.append((d, next_cell))

        # 如果没有可行方向，返回None（将触发掉头）
        if not possible_dirs:
            return None

        # 计算每个方向到目标的实际距离
        player_cell = gold
        min_distance = float("inf")
        best_cell = None

        for d, cell in possible_dirs:
            distance = self.bfs_distance(cell, player_cell)
            if distance < min_distance:
                min_distance = distance
                best_cell = cell
                self.dirc = d  # 更新方向

        return best_cell

    def check_collision(self, x, y):
        """检查周围多个点是否碰撞"""
        # 检查中心点
        if (int(x), int(y)) in self.game.map.world_map:
            return True

        # 检查周围的点（根据半径）
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

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    # bfs寻路
    def bfs_distance(self, start, target):
        """使用BFS计算两个格子之间的最短路径长度"""
        if start == target:
            return 0

        queue = deque()
        visited = set()

        queue.append((start, 0))
        visited.add(start)
        visited.add((int(self.x), int(self.y)))

        while queue:
            (x, y), steps = queue.popleft()

            # 找到目标
            if (x, y) == target:
                return steps

            # 检查四个方向
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                next_cell = (nx, ny)

                # 如果是墙壁或已访问，跳过
                if not self.check_wall(nx, ny) or next_cell in visited:
                    continue

                visited.add(next_cell)
                queue.append((next_cell, steps + 1))

        # 如果无法到达目标，返回一个大数
        return 1000


class Blinky(NPC):

    def __init__(
        self,
        game,
        path="resource/sprite/npc/ghost/Blinky/0.png",
        pos=(9.5, 4.5),
        scale=1,
        shift=0,
        animation_time=180,
        home=(1, 1),
        sound_path="resource/audio/pop.mp3",
    ):
        super().__init__(game, path, pos, scale, shift, animation_time, home, sound_path)

    def action(self):
        if self.model == CHASE or self.change_not > 6:
            if NPC_DRAW:
                pg.draw.rect(self.game.screen, "red", (int(self.player.x) * TEST_SIZE, int(self.player.y) * TEST_SIZE, TEST_SIZE, TEST_SIZE))

            self.movement((int(self.player.x), int(self.player.y)))
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = SCATTER

        elif self.model == SCATTER:
            self.movement(self.home)
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = CHASE

    def update(self):
        super().update()

        if NPC_DRAW:
            pg.draw.circle(self.game.screen, "orange", (self.x * TEST_SIZE, self.y * TEST_SIZE), 10)


class Pinky(NPC):

    def __init__(
        self,
        game,
        path="resource/sprite/npc/ghost/Blinky/0.png",
        pos=(9.5, 4.5),
        scale=1,
        shift=0,
        animation_time=180,
        home=(1, 1),
        sound_path="resource/audio/pop.mp3",
    ):
        super().__init__(game, path, pos, scale, shift, animation_time, home, sound_path)

    def action(self):
        if self.model == CHASE or self.change_not > 6:
            pos_x, pos_y = int(self.player.x + 3 * math.cos(self.player.angle)), int(self.player.y + 3 * math.sin(self.player.angle))

            if NPC_DRAW:
                pg.draw.rect(self.game.screen, "pink", (int(pos_x) * TEST_SIZE, int(pos_y) * TEST_SIZE, TEST_SIZE, TEST_SIZE))

            self.movement((pos_x, pos_y))
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = SCATTER

        elif self.model == SCATTER:
            self.movement(self.home)
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = CHASE

    def update(self):
        super().update()

        if NPC_DRAW:
            pg.draw.circle(self.game.screen, "orange", (self.x * TEST_SIZE, self.y * TEST_SIZE), 10)


class Inky(NPC):

    def __init__(
        self,
        game,
        path="resource/sprite/npc/ghost/Blinky/0.png",
        pos=(9.5, 4.5),
        scale=1,
        shift=0,
        animation_time=180,
        home=(1, 1),
        sound_path="resource/audio/pop.mp3",
    ):
        super().__init__(game, path, pos, scale, shift, animation_time, home, sound_path)

    def action(self):
        if self.model == CHASE or self.change_not > 6:
            # 目标点为Blinky的位置关于玩家方向前两格的对称点
            blinky = self.game.object_handler.npc_list[0]  # 假设Blinky是第一个NPC
            blinky_x, blinky_y = blinky.x, blinky.y

            # 计算玩家前方两格的位置
            p_x = self.player.x + math.cos(self.player.angle)
            p_y = self.player.y + math.sin(self.player.angle)

            # 计算对称点：向量翻倍
            pos_x = 2 * p_x - blinky_x
            pos_y = 2 * p_y - blinky_y

            if NPC_DRAW:
                pg.draw.rect(self.game.screen, "blue", (int(pos_x) * TEST_SIZE, int(pos_y) * TEST_SIZE, TEST_SIZE, TEST_SIZE))

            self.movement((int(pos_x), int(pos_y)))
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = SCATTER

        elif self.model == SCATTER:
            self.movement(self.home)
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = CHASE

    def update(self):
        super().update()

        if NPC_DRAW:
            pg.draw.circle(self.game.screen, "orange", (self.x * TEST_SIZE, self.y * TEST_SIZE), 10)


class Clyde(NPC):
    def __init__(
        self,
        game,
        path="resource/sprite/npc/ghost/Blinky/0.png",
        pos=(9.5, 4.5),
        scale=1,
        shift=0,
        animation_time=180,
        home=(1, 1),
        sound_path="resource/audio/pop.mp3",
    ):
        super().__init__(game, path, pos, scale, shift, animation_time, home, sound_path)

    def action(self):
        if self.model == CHASE or self.change_not > 6:
            pos = (0, 0)
            if math.sqrt((self.x - self.player.x) ** 2 + (self.y - self.player.y) ** 2) <= 4:
                pos = self.home
            else:
                pos = (int(self.player.x), int(self.player.y))
            self.movement(pos)
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = SCATTER

        elif self.model == SCATTER:
            self.movement(self.home)
            self.change_time += 1
            if self.change_time >= self.change_need_time:
                self.change_time = 0
                self.change_not += 1
                self.change_need_time = CHANGE_TIME[self.change_not] * FPS
                self.model = CHASE

    def update(self):
        super().update()

        if NPC_DRAW:
            pg.draw.circle(self.game.screen, "orange", (self.x * TEST_SIZE, self.y * TEST_SIZE), 10)
