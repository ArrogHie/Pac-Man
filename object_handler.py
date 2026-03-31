from sprite_object import *
from npc import *
from map import *


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_path = "resource/sprite/npc/ghost/"
        self.static_sprite_path = "resource/sprite/static_sprite/"
        self.animated_sprite_path = "resource/sprite/animated_sprite/"
        add_s = self.add_sprite
        add_n = self.add_npc
        sS = self.static_sprite_path
        aS = self.animated_sprite_path
        nS = self.npc_path

        """add_s(SpriteObject(game))
        add_s(AnimatedSprite(game))
        add_s(SpriteObject(game, path=sS + "bean.png", pos=(2.5, 2.5), scale=0.1, shift=4))"""

        add_n(Blinky(game, path=self.npc_path + "dayun" + "/0.jpg", pos=(22.5, 2.5), scale=0.7, home=(22, 2), sound_path="resource/audio/dayun.mp3"))
        add_n(
            Pinky(
                game,
                path=self.npc_path + "loli" + "/frame_0000.png",
                pos=(1.5, 2.5),
                animation_time=50,
                home=(1, 2),
                sound_path="resource/audio/loli.mp3",
            )
        )
        add_n(
            Inky(
                game,
                path=self.npc_path + "oiia" + "/frame_0000.png",
                pos=(22.5, 28.5),
                animation_time=50,
                home=(22, 28),
                sound_path="resource/audio/oiia.mp3",
            )
        )
        add_n(
            Clyde(
                game,
                path=self.npc_path + "pop" + "/0.png",
                pos=(1.5, 30.5),
                scale=0.7,
                animation_time=150,
                home=(1, 30),
                sound_path="resource/audio/pop.mp3",
            )
        )

        self.bean_list = {}
        for i, row in enumerate(mini_map):
            for j, val in enumerate(row):
                if not val:
                    self.bean_list[(j, i)] = SpriteObject(game, path=sS + "bean.png", pos=(j + 0.5, i + 0.5), scale=0.1, shift=4)
                    add_s(self.bean_list[(j, i)])
                    self.game.score += 1

    def update(self):
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
