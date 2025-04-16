# Dragon Cave Adventure - A Simple Pygame Platformer for Kids
# Developed for a 5-year-old audience.

# --- Setup Guide ---
# 1. Make sure you have Python installed (version 3.6 or later recommended).
# 2. Install the Pygame library:
#    Open a terminal or command prompt and type: pip install pygame
#    (If you have multiple Python versions, you might need to use 'pip3' instead of 'pip')
# 3. Save this code as a Python file (e.g., dragon_cave_adventure.py).
# 4. (Optional) Create an 'assets' folder in the same directory as the Python file.
#    - Place custom sprite images (e.g., 'caver.png', 'dragon.png', 'gem.png', 'fireball.png', 'rock.png', 'exit.png') in this folder.
#    - Place sound effect files (e.g., 'jump.wav', 'coin.wav', 'roar.wav', 'hit.wav') in this folder.
#    - If you don't have assets, the game will use colored rectangles and print messages instead of playing sounds.
# 5. Run the game from the terminal: python dragon_cave_adventure.py
# --- End Setup Guide ---

import pygame
import random
import os
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230) # Caver color
PURPLE = (128, 0, 128)      # Treasure color
ORANGE = (255, 165, 0)      # Fireball color

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.6
PLAYER_JUMP_POWER = 15
PLAYER_SIZE = (30, 40)

# Dragon properties
DRAGON_SIZE = (60, 50)
DRAGON_WAKE_RANGE = 150 # Pixels
DRAGON_SPEED = 1.5
DRAGON_FIRE_RATE = 120 # Frames between fireballs
DRAGON_DISTRACTION_TIME = 180 # Frames dragon stays distracted

# Fireball properties
FIREBALL_SIZE = (15, 15)
FIREBALL_SPEED = 5

# Treasure properties
TREASURE_SIZE = (20, 20)

# Obstacle properties
OBSTACLE_SIZE = (50, 50)

# Dropped Rock properties
DROPPED_ROCK_SIZE = (15, 15)
DROPPED_ROCK_GRAVITY = 0.8

# Level properties
GROUND_LEVEL = SCREEN_HEIGHT - 40
SCROLL_THRESH = SCREEN_WIDTH // 3 # How far player moves before screen scrolls

# Asset paths (optional)
ASSETS_FOLDER = "assets"

# --- Asset Loading Function ---
def load_image(filename, size=None):
    """Loads an image, handling errors."""
    path = os.path.join(ASSETS_FOLDER, filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Cannot load image: {filename} - {e}")
        return None

def load_sound(filename):
    """Loads a sound, handling errors."""
    path = os.path.join(ASSETS_FOLDER, filename)
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except (pygame.error, FileNotFoundError) as e: # Catch both errors
        print(f"Cannot load sound: {filename} - {e}")
        # Return a dummy sound object that does nothing
        class DummySound:
            def play(self): pass
        return DummySound()

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image_orig = load_image("caver.png", PLAYER_SIZE)
        if self.image_orig is None:
            self.image = pygame.Surface(PLAYER_SIZE)
            self.image.fill(LIGHT_BLUE)
        else:
             self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 4
        self.rect.bottom = GROUND_LEVEL - 10 # Start slightly above ground
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.last_rock_drop = pygame.time.get_ticks()
        self.rock_cooldown = 1000 # Milliseconds

    def jump(self):
        # Jump only if standing on a platform
        self.rect.y += 1 # Move down 1 pixel to check for collision
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1 # Move back up
        if hits:
            self.vel.y = -PLAYER_JUMP_POWER
            self.game.jump_sound.play()

    def drop_rock(self):
        now = pygame.time.get_ticks()
        if now - self.last_rock_drop > self.rock_cooldown:
            self.last_rock_drop = now
            rock = DroppedRock(self.game, self.rect.centerx, self.rect.centery)
            self.game.all_sprites.add(rock)
            self.game.dropped_rocks.add(rock)
            # Add a small visual/audio cue if needed

    def update(self):
        # --- Physics Calculations ---
        # Apply gravity
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)

        # Get key presses for acceleration
        keys = pygame.key.get_pressed()
        moving_left = keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_RIGHT]

        if moving_left:
            self.acc.x = -PLAYER_ACC
        if moving_right:
            self.acc.x = PLAYER_ACC

        # Apply friction only if not accelerating horizontally
        if not moving_left and not moving_right:
            self.acc.x += self.vel.x * PLAYER_FRICTION

        # Equations of motion: update velocity
        self.vel += self.acc

        # Limit horizontal velocity (optional, but can prevent excessive speed)
        if abs(self.vel.x) > 7: # Increased limit slightly
             self.vel.x = 7 * (1 if self.vel.x > 0 else -1)
        # Prevent tiny drifting when stopping
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

        # --- Movement and Collision ---
        # Update horizontal position
        self.pos.x += self.vel.x
        self.rect.centerx = round(self.pos.x) # Update rect X

        # Check for horizontal collisions
        collision_sprites = self.game.platforms # Check against platforms and obstacles
        hits = pygame.sprite.spritecollide(self, collision_sprites, False)
        for hit in hits:
            if self.vel.x > 0:  # Moving right
                self.rect.right = hit.rect.left
            elif self.vel.x < 0:  # Moving left
                self.rect.left = hit.rect.right
            self.pos.x = self.rect.centerx # Correct vector position
            self.vel.x = 0 # Stop horizontal movement

        # Update vertical position
        self.pos.y += self.vel.y
        self.rect.bottom = round(self.pos.y) # Update rect Y (using bottom)
        self.on_ground = False # Assume not on ground until check

        # Check for vertical collisions
        hits = pygame.sprite.spritecollide(self, collision_sprites, False)
        for hit in hits:
            if self.vel.y > 0: # Moving down (landing)
                self.rect.bottom = hit.rect.top
                self.on_ground = True
                self.vel.y = 0 # Stop vertical movement
            elif self.vel.y < 0: # Moving up (hitting ceiling)
                 self.rect.top = hit.rect.bottom
                 self.vel.y = 0 # Stop vertical movement (hit head)
            self.pos.y = self.rect.bottom # Correct vector position (using bottom)


        # --- Boundary Checks ---
        # Keep player within level bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
            self.vel.x = 0 # Stop movement at edge
        if self.rect.right > self.game.level_width:
            self.rect.right = self.game.level_width
            self.pos.x = self.rect.centerx
            self.vel.x = 0 # Stop movement at edge
        # Optional: Prevent falling through floor if something goes wrong
        if self.rect.bottom > GROUND_LEVEL + 50: # A bit below ground
             self.rect.bottom = GROUND_LEVEL
             self.pos.y = self.rect.bottom
             self.on_ground = True
             self.vel.y = 0

        # Final sync of vector position based on rect (midbottom is often good)
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)


class Dragon(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image_sleep = load_image("dragon_sleep.png", DRAGON_SIZE) # Need separate sleep image
        self.image_awake = load_image("dragon.png", DRAGON_SIZE)

        if self.image_awake is None:
            self.image_awake = pygame.Surface(DRAGON_SIZE)
            self.image_awake.fill(RED)
        if self.image_sleep is None: # Use awake image if sleep not found
            self.image_sleep = self.image_awake.copy()
            pygame.draw.circle(self.image_sleep, BLACK, (int(DRAGON_SIZE[0]*0.7), int(DRAGON_SIZE[1]*0.3)), 3) # Draw 'zzz' maybe :)

        self.image = self.image_sleep # Start sleeping
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.state = "sleeping" # states: sleeping, waking, chasing, distracted
        self.last_fireball = pygame.time.get_ticks()
        self.wake_timer = 0
        self.distraction_target = None
        self.distraction_timer = 0

    def wake_up(self):
        if self.state == "sleeping":
            self.state = "waking"
            self.image = self.image_awake # Change sprite
            self.game.dragon_roar_sound.play()
            # Maybe add a short waking animation/timer later
            self.state = "chasing"
            self.last_fireball = pygame.time.get_ticks() # Reset fireball timer

    def get_distracted(self, target_pos):
        if self.state == "chasing" or self.state == "distracted":
            self.state = "distracted"
            self.distraction_target = pygame.math.Vector2(target_pos)
            self.distraction_timer = pygame.time.get_ticks()
            print("Dragon distracted!")

    def update(self):
        if self.state == "sleeping":
            # Check if player is too close
            dist_to_player = self.pos.distance_to(self.game.player.pos)
            if dist_to_player < DRAGON_WAKE_RANGE:
                 # Add a visual cue maybe (e.g., question mark) before waking?
                 print("Dragon senses player!")
                 self.wake_up()
            return # Do nothing else if sleeping

        if self.state == "waking":
            # Could add a small delay or animation here
            self.state = "chasing"
            return

        target = None
        if self.state == "distracted":
            now = pygame.time.get_ticks()
            if now - self.distraction_timer > DRAGON_DISTRACTION_TIME * 1000 / FPS:
                print("Dragon no longer distracted.")
                self.state = "chasing"
                self.distraction_target = None
                target = self.game.player.pos
            else:
                target = self.distraction_target
                # Check if reached distraction target
                if self.pos.distance_to(target) < 10: # Close enough
                     print("Dragon reached distraction spot.")
                     # Stay here until timer runs out or maybe look around?
                     self.vel = pygame.math.Vector2(0, 0) # Stop moving
                else:
                     # Move towards distraction target
                     direction = (target - self.pos).normalize()
                     self.vel = direction * DRAGON_SPEED
                     self.pos += self.vel
                     self.rect.center = self.pos

        elif self.state == "chasing":
            target = self.game.player.pos
            # Basic chase logic: move towards player
            if self.pos.distance_to(target) > 5: # Avoid jittering when close
                 direction = (target - self.pos).normalize()
                 self.vel = direction * DRAGON_SPEED
                 self.pos += self.vel
                 self.rect.center = self.pos

            # Fireball logic (only when chasing)
            now = pygame.time.get_ticks()
            if now - self.last_fireball > DRAGON_FIRE_RATE * 1000 / FPS:
                self.last_fireball = now
                fire_direction = (self.game.player.pos - self.pos)
                # Dont shoot if player is directly above or below maybe?
                if fire_direction.length() > 0: # Avoid zero vector normalization
                    fire_direction = fire_direction.normalize()
                    fireball = Fireball(self.game, self.rect.centerx, self.rect.centery, fire_direction)
                    self.game.all_sprites.add(fireball)
                    self.game.fireballs.add(fireball)


class Fireball(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        super().__init__()
        self.game = game
        self.image_orig = load_image("fireball.png", FIREBALL_SIZE)
        if self.image_orig is None:
            self.image = pygame.Surface(FIREBALL_SIZE)
            self.image.fill(ORANGE)
        else:
             self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = direction * FIREBALL_SPEED
        self.rect.center = self.pos

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        # Remove if it goes off-screen
        if not self.game.world_rect.colliderect(self.rect):
            self.kill()
        # Check collision with obstacles
        if pygame.sprite.spritecollide(self, self.game.obstacles, False):
            self.kill() # Fireball disappears on hitting an obstacle


class Treasure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_orig = load_image("gem.png", TREASURE_SIZE)
        if self.image_orig is None:
            self.image = pygame.Surface(TREASURE_SIZE)
            self.image.fill(PURPLE)
        else:
             self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(BROWN) # Simple brown platforms
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Obstacle(pygame.sprite.Sprite):
    """Obstacles like rocks player can hide behind."""
    def __init__(self, x, y):
        super().__init__()
        self.image_orig = load_image("rock.png", OBSTACLE_SIZE)
        if self.image_orig is None:
            self.image = pygame.Surface(OBSTACLE_SIZE)
            self.image.fill(GRAY)
        else:
            self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y


class DroppedRock(pygame.sprite.Sprite):
    """Rocks dropped by the player to distract the dragon."""
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface(DROPPED_ROCK_SIZE)
        self.image.fill(DARK_GRAY)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.vel_y = 0
        self.rect.center = self.pos
        self.landed = False
        self.land_pos = None

    def update(self):
        if not self.landed:
            self.vel_y += DROPPED_ROCK_GRAVITY
            self.pos.y += self.vel_y
            self.rect.centery = self.pos.y

            # Check for landing on a platform or ground
            if self.rect.bottom >= GROUND_LEVEL:
                self.rect.bottom = GROUND_LEVEL
                self.landed = True
                self.vel_y = 0
                self.land_pos = self.rect.midbottom
            else:
                 # Check platform collision
                 # Note: This collision check is basic. It assumes rocks fall straight down.
                 hit_platforms = pygame.sprite.spritecollide(self, self.game.platforms, False)
                 if hit_platforms:
                     self.rect.bottom = hit_platforms[0].rect.top
                     self.landed = True
                     self.vel_y = 0
                     self.land_pos = self.rect.midbottom

            # Remove if it goes off bottom of screen somehow
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        size = (40, 60)
        self.image_orig = load_image("exit.png", size)
        if self.image_orig is None:
            self.image = pygame.Surface(size)
            self.image.fill(GREEN)
        else:
            self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y


# --- Game Class ---

class Game:
    def __init__(self):
        # Initialize Pygame and create window
        pygame.init()
        pygame.mixer.init() # For sounds
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dragon Cave Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font('arial') # Find a default font
        self.state = "start" # states: start, playing, game_over
        self.score = 0
        self.world_shift = 0
        self.level_width = 2000 # Width of the entire level

        # Define the bounds of the game world
        self.world_rect = pygame.Rect(0, 0, self.level_width, SCREEN_HEIGHT)


        self.load_data()

    def load_data(self):
        """Load game assets"""
        self.jump_sound = load_sound("jump.wav")
        self.coin_sound = load_sound("coin.wav")
        self.dragon_roar_sound = load_sound("roar.wav")
        self.hit_sound = load_sound("hit.wav")
        # Load background - optional
        self.background = load_image("cave_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.background is None:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(DARK_GRAY) # Default dark background
        self.background_rect = self.background.get_rect()


    def new(self):
        """Start a new game"""
        self.score = 0
        self.world_shift = 0
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.treasures = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        self.dropped_rocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group() # Group for things that hurt player

        # Create player
        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Create Dragon
        # Position dragon further into the level
        self.dragon = Dragon(self, self.level_width * 0.7, GROUND_LEVEL)
        self.all_sprites.add(self.dragon)
        self.enemies.add(self.dragon)

        # Define level layout (platforms, treasures, obstacles, exit)
        # Platform format: (x, y, width, height)
        # Treasure format: (x, y_bottom) - places bottom center at x, y
        # Obstacle format: (x, y_bottom)
        # Exit format: (x, y_bottom)

        # Ground platform spanning the level width
        ground = Platform(0, GROUND_LEVEL, self.level_width, 40)
        self.all_sprites.add(ground)
        self.platforms.add(ground)

        # Example level elements:
        level_elements = [
            # Platforms
            Platform(200, SCREEN_HEIGHT - 150, 150, 20),
            Platform(500, SCREEN_HEIGHT - 250, 100, 20),
            Platform(750, SCREEN_HEIGHT - 180, 120, 20),
            Platform(1000, SCREEN_HEIGHT - 300, 150, 20),
            Platform(1300, SCREEN_HEIGHT - 200, 100, 20),
            # Treasures
            Treasure(250, SCREEN_HEIGHT - 150), # On first platform
            Treasure(550, SCREEN_HEIGHT - 250), # On second platform
            Treasure(150, GROUND_LEVEL),
            Treasure(900, GROUND_LEVEL),
            Treasure(1100, SCREEN_HEIGHT - 300), # On fourth platform
            Treasure(1400, GROUND_LEVEL),
            # Obstacles (rocks to hide behind)
            Obstacle(400, GROUND_LEVEL),
            Obstacle(1200, GROUND_LEVEL),
            # Exit
            Exit(self.level_width - 100, GROUND_LEVEL)
        ]

        for element in level_elements:
            self.all_sprites.add(element)
            if isinstance(element, Platform):
                self.platforms.add(element)
            elif isinstance(element, Treasure):
                self.treasures.add(element)
            elif isinstance(element, Obstacle):
                self.obstacles.add(element)
                self.platforms.add(element) # Treat obstacles as platforms for collision
            elif isinstance(element, Exit):
                self.exit_sprite = element # Store ref to exit

        self.state = "playing"
        self.run()

    def run(self):
        """Game Loop"""
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        """Game Loop - Update"""
        self.all_sprites.update()

        # --- Scrolling ---
        scroll = 0
        
        # Calculate potential shift based on player position and screen thresholds
        player_screen_x = self.player.rect.centerx + self.world_shift

        # If player moves past the right scroll threshold towards the right
        if player_screen_x > SCREEN_WIDTH - SCROLL_THRESH and self.player.vel.x > 0:
            scroll = -int(self.player.vel.x) # Shift world left

        # If player moves past the left scroll threshold towards the left
        elif player_screen_x < SCROLL_THRESH and self.player.vel.x < 0:
            scroll = -int(self.player.vel.x) # Shift world right

        # Clamp the world_shift to the level boundaries
        potential_new_shift = self.world_shift + scroll
        max_left_shift = 0
        max_right_shift = -(self.level_width - SCREEN_WIDTH)

        # Apply clamping
        self.world_shift = max(max_right_shift, min(max_left_shift, potential_new_shift))

        # Recalculate the actual scroll applied after clamping (for sprite shifting)
        actual_scroll = self.world_shift - (potential_new_shift - scroll) 

        # Apply the *actual* scroll to all sprites EXCEPT the player
        if actual_scroll != 0:
            for sprite in self.all_sprites:
                if sprite != self.player:
                    sprite.rect.x += actual_scroll
                    # Need to update position vectors for sprites that use them (Dragon, Fireball)
                    if hasattr(sprite, 'pos'):
                        sprite.pos.x += actual_scroll

        # Player boundary checks are now handled entirely within Player.update relative to level_width
        # No need for extra boundary checks or player position adjustments here.
        
        # --- Game Logic ---
        # Player collects treasures
        treasure_hits = pygame.sprite.spritecollide(self.player, self.treasures, True) # True removes the treasure
        for treasure in treasure_hits:
            self.score += 1
            self.coin_sound.play()
            # Check if collecting treasure wakes dragon (optional noise mechanic)
            if self.dragon.state == "sleeping":
                 dist_to_dragon = self.player.pos.distance_to(self.dragon.pos)
                 # Make noise more likely to wake dragon if closer
                 wake_chance = (DRAGON_WAKE_RANGE * 1.5 - dist_to_dragon) / (DRAGON_WAKE_RANGE * 1.5)
                 if random.random() < wake_chance * 0.5: # 50% chance based on proximity
                      print("Treasure collection noise woke the dragon!")
                      self.dragon.wake_up()

        # Player hits exit
        if pygame.sprite.collide_rect(self.player, self.exit_sprite):
            print("You Win!")
            self.playing = False
            self.state = "game_over_win"

        # Player hits dragon or fireballs
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_rect_ratio(0.8)) # Smaller hitbox
        fireball_hits = pygame.sprite.spritecollide(self.player, self.fireballs, True, pygame.sprite.collide_rect_ratio(0.8)) # Fireballs disappear on hit

        if enemy_hits or fireball_hits:
            if self.dragon.state != "sleeping": # Only lose if dragon is awake
                print("Game Over!")
                self.hit_sound.play()
                self.playing = False
                self.state = "game_over_lose"


        # Dropped rocks hit dragon (distraction)
        if self.dragon.state != "sleeping":
             rock_hits = pygame.sprite.spritecollide(self.dragon, self.dropped_rocks, False) # Don't kill rock yet
             for rock in rock_hits:
                  if rock.landed: # Only landed rocks distract
                       self.dragon.get_distracted(rock.land_pos)
                       rock.kill() # Remove the rock once it hits

        # Player hits obstacles (stop movement) - Handled partly in Player update, could refine here
        obstacle_hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if obstacle_hits:
            # Basic horizontal collision response
            if self.player.vel.x > 0: # Moving right
                self.player.rect.right = obstacle_hits[0].rect.left
            elif self.player.vel.x < 0: # Moving left
                self.player.rect.left = obstacle_hits[0].rect.right
            self.player.pos.x = self.player.rect.centerx
            self.player.vel.x = 0

            # Basic vertical collision response (if falling onto obstacle)
            if self.player.vel.y > 0 and self.player.rect.bottom > obstacle_hits[0].rect.top:
                self.player.rect.bottom = obstacle_hits[0].rect.top + 1
                self.player.pos.y = self.player.rect.bottom
                self.player.vel.y = 0
                self.player.on_ground = True # Can jump off obstacles

        # Keep player and dragon within world bounds (redundant check, but safe)
        if self.player.rect.left < 0: self.player.rect.left = 0; self.player.pos.x = self.player.rect.centerx
        if self.player.rect.right > self.level_width: self.player.rect.right = self.level_width; self.player.pos.x = self.player.rect.centerx
        if self.dragon.rect.left < 0: self.dragon.rect.left = 0; self.dragon.pos.x = self.dragon.rect.centerx
        if self.dragon.rect.right > self.level_width: self.dragon.rect.right = self.level_width; self.dragon.pos.x = self.dragon.rect.centerx


    def events(self):
        """Game Loop - Events"""
        for event in pygame.event.get():
            # Check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # Check for key presses
            if event.type == pygame.KEYDOWN:
                 if self.state == "playing":
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_SPACE:
                        self.player.drop_rock()
                 elif self.state == "start" or self.state.startswith("game_over"):
                     # Any key press starts a new game from start/game over screens
                     if event.key != pygame.K_ESCAPE: # Allow ESC to quit always
                          self.state = "playing" # Trigger new game start
                          self.playing = False # End current loop (start/game over)

                 if event.key == pygame.K_ESCAPE: # Global quit key
                      self.running = False
                      if self.playing:
                           self.playing = False


    def draw(self):
        """Game Loop - Draw"""
        # Draw background (relative to screen)
        self.screen.blit(self.background, self.background_rect)

        # Draw all sprites (shifted by world_shift)
        for sprite in self.all_sprites:
            # Adjust draw position based on world_shift
            # Only draw sprites that are potentially visible on screen
            # This is a basic visibility check
            screen_rect = self.screen.get_rect()
            sprite_screen_pos = sprite.rect.move(self.world_shift, 0)
            if screen_rect.colliderect(sprite_screen_pos):
                 self.screen.blit(sprite.image, sprite_screen_pos)


        # Draw Score
        self.draw_text(f"Treasures: {self.score}", 22, WHITE, SCREEN_WIDTH / 2, 15)

        # Draw Dragon State (for debugging/clarity)
        if self.dragon.state == "sleeping":
            self.draw_text("Dragon: Zzzz", 18, WHITE, SCREEN_WIDTH - 100, 15)
        elif self.dragon.state == "chasing":
             self.draw_text("Dragon: AWAKE!", 18, RED, SCREEN_WIDTH - 100, 15)
        elif self.dragon.state == "distracted":
              self.draw_text("Dragon: Distracted", 18, YELLOW, SCREEN_WIDTH - 100, 15)


        # After drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        """Display the start screen"""
        self.screen.blit(self.background, self.background_rect) # Use game background
        self.draw_text("Dragon Cave Adventure!", 48, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        self.draw_text("Use ARROW keys to move, UP to jump", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.draw_text("SPACEBAR to drop a rock (distracts awake dragon)", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        self.draw_text("Collect treasures and reach the exit!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80)
        self.draw_text("Don't get too close to the sleeping dragon...", 22, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120)
        self.draw_text("Press any key to start", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        pygame.display.flip()
        self.wait_for_key()

    def show_game_over_screen(self, win):
        """Display game over screen"""
        if not self.running: # Don't show if we quit during game over
             return
        self.screen.blit(self.background, self.background_rect) # Use game background
        if win:
            self.draw_text("YOU WIN!", 48, GREEN, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
            self.draw_text(f"You collected {self.score} treasures!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        else:
            self.draw_text("GAME OVER!", 48, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
            self.draw_text("The dragon got you!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.draw_text("Press any key to play again", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        """Pause the game until a key is pressed"""
        waiting = True
        while waiting:
            self.clock.tick(FPS / 2) # Lower FPS while waiting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP: # Use KEYUP to avoid holding key issues
                    if event.key == pygame.K_ESCAPE: # Allow quitting from wait screens
                         waiting = False
                         self.running = False
                    else:
                        waiting = False # Any other key ends wait

    def draw_text(self, text, size, color, x, y):
        """Helper function to draw text on screen"""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color) # True for anti-aliasing
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

# --- Main Execution ---
g = Game()
g.show_start_screen()
while g.running:
    g.new() # Start a new game instance
    if g.state == "game_over_win":
        g.show_game_over_screen(win=True)
    elif g.state == "game_over_lose":
         g.show_game_over_screen(win=False)
    # If g.running is False after show_game_over_screen (due to ESC), loop will terminate

pygame.quit()


# --- Potential Modifications/Improvements ---
# - Add more levels: Create a level loading system (e.g., from text files or lists).
# - Add more enemy types or obstacles.
# - Implement parallax scrolling for the background layers.
# - Refine collision detection (e.g., pixel-perfect or more robust AABB).
# - Add animations for player (walking, jumping) and dragon (waking, roaring, breathing fire).
# - Improve dragon AI (e.g., pathfinding, different attack patterns).
# - Add power-ups (e.g., temporary speed boost, shield).
# - Adjust difficulty: Change PLAYER_SPEED, DRAGON_SPEED, DRAGON_WAKE_RANGE, DRAGON_FIRE_RATE.
# - Create better placeholder art or find free sprites (e.g., on sites like OpenGameArt.org).
# - Add background music.
# - Implement a pause menu.
# - Add particle effects (e.g., for fireballs, collecting gems).
# - Adjust collision handling to prevent player from being reset to the bottom left.
# --- End Modifications --- 