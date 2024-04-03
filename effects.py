from enum import IntEnum

import pygame as pg

from colors import *


class ParticleID(IntEnum):
    EXPLOSION = 1

    AMMO = 2
    SPEED = 3
    COOLING = 4
    MAX_HEAT = 5
    WEAPON_GAIN = 6


id_to_text = {
    ParticleID.AMMO: "+10 AMMO",
    ParticleID.SPEED: "+5 SPEED",
    ParticleID.COOLING: "+1 COOLING",
    ParticleID.MAX_HEAT: "+5 MAX HEAT",
    ParticleID.WEAPON_GAIN: "+WEAPON",
}

id_to_color = {
    ParticleID.AMMO: WHITE,
    ParticleID.SPEED: YELLOW,
    ParticleID.COOLING: CYAN,
    ParticleID.MAX_HEAT: GREEN,
    ParticleID.WEAPON_GAIN: WHITE,
}


class Particle(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], vel: tuple[int, int], lifetime: int, eid: ParticleID,
                 radius: float | None = None, wid=None):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.lifetime = lifetime
        self.current_life = pg.time.get_ticks()
        self.id = eid
        self.radius = radius
        self.resolved = False
        self.weapon_id = wid

    def update(self, dt):
        if pg.time.get_ticks() - self.current_life >= self.lifetime:
            self.kill()
            return
        self.pos += self.vel * dt
