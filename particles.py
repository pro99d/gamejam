import math
import random
import arcade
from base_classes import Vec2

# --- Explosion Particles Related
# How fast the particle will accelerate down. Make 0 if not desired
PARTICLE_GRAVITY = 0.00
PARTICLE_FADE_RATE = 8
PARTICLE_MIN_SPEED = 2.5
PARTICLE_SPEED_RANGE = 2.5
PARTICLE_COUNT = 100
PARTICLE_RADIUS = 3
# Possible particle colors
PARTICLE_COLORS = [arcade.color.ALIZARIN_CRIMSON,
                   arcade.color.LAVA,
                   arcade.color.LAVA,
                   arcade.color.LAVA,
                   arcade.color.KU_CRIMSON,
                   arcade.color.DARK_TANGERINE]

# Chance we'll flip the texture to white and make it 'sparkle'
PARTICLE_SPARKLE_CHANCE = 0.015
# --- Smoke
# Note: Adding smoke trails makes for a lot of sprites and can slow things
# down. If you want a lot, it will be necessary to move processing to GPU
# using transform feedback. If to slow, just get rid of smoke.
SMOKE_START_SCALE = 0.25
SMOKE_EXPANSION_RATE = 0.03
SMOKE_FADE_RATE = 7
SMOKE_RISE_RATE = 0.5
SMOKE_CHANCE = 0.25


class Smoke(arcade.SpriteCircle):
    """Particle with smoke like behavior."""
    def __init__(self, size):
        super().__init__(size, arcade.color.LIGHT_GRAY, soft=True)
        self.change_y = SMOKE_RISE_RATE
        self.scale = SMOKE_START_SCALE

    def update(self, delta_time: float = 1/60):
        """Update this particle"""
        # Take delta_time into account
        time_step = 60 * delta_time

        if self.alpha <= PARTICLE_FADE_RATE:
            # Remove faded out particles
            self.remove_from_sprite_lists()
        else:
            # Update values
            self.alpha -= int(SMOKE_FADE_RATE * time_step)
            self.center_x += self.change_x * time_step
            self.center_y += self.change_y * time_step
            self.add_scale(SMOKE_EXPANSION_RATE * time_step)


class Particle(arcade.SpriteCircle):
    """ Explosion particle"""
    def __init__(self):
        """
        Simple particle sprite based on circle sprite.
        """
        # Make the particle
        super().__init__(PARTICLE_RADIUS, random.choice(PARTICLE_COLORS))

        # Set direction/speed
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

    def update(self, delta_time: float = 1 / 60):
        """Update the particle"""
        # Take delta_time into account
        time_step = 60 * delta_time

        if self.alpha == 0:
            # Faded out, remove
            self.remove_from_sprite_lists()
        else:
            # Gradually fade out the particle. Don't go below 0
            self.alpha = max(0, self.alpha - PARTICLE_FADE_RATE)
            # Move the particle
            self.center_x += self.change_x * time_step
            self.center_y += self.change_y * time_step
            self.change_y -= PARTICLE_GRAVITY * time_step

            # Should we sparkle this?
            if random.random() <= PARTICLE_SPARKLE_CHANCE:
                self.alpha = 255
                self.color = arcade.color.WHITE

            # Leave a smoke particle?
            if random.random() <= SMOKE_CHANCE:
                smoke = Smoke(5)
                smoke.position = self.position
                # Add a smoke particle to the spritelist this sprite is in
                self.sprite_lists[0].append(smoke)

class ParticleSystem:
    def __init__(self):
        self.explosions_list = arcade.SpriteList()

    def draw(self):
        self.explosions_list.draw()

    def update(self, dt: float):
        self.explosions_list.update(dt)

    def create_explosion(self, pos: Vec2, particle_count= PARTICLE_COUNT):
        for i in range(particle_count):
            particle = Particle()
            particle.position = pos.list
            self.explosions_list.append(particle)

        smoke = Smoke(50)
        smoke.position = pos.list
        self.explosions_list.append(smoke)

system = ParticleSystem()
