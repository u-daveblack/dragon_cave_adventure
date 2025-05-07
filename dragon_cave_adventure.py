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

# Big Treasure properties
BIG_TREASURE_SIZE = (50, 50) # Adjust as needed

# Obstacle properties
OBSTACLE_SIZE = (50, 50)

# Dropped Rock properties
DROPPED_ROCK_SIZE = (15, 15)
DROPPED_ROCK_GRAVITY = 0.8
LAND_SOUND_RADIUS = 100 # How far away the dragon hears a rock land

# Level properties
GROUND_LEVEL = SCREEN_HEIGHT - 40
SCROLL_THRESH = SCREEN_WIDTH // 3 # How far player moves before screen scrolls

# Asset paths (optional)
ASSETS_FOLDER = "assets"

# Define level data structure (outside the Game class)
LEVELS = [
    # Level 1 (Original Layout - slightly adjusted)
    {
        "platforms": [
            (0, GROUND_LEVEL, 2000, 40), # Ground floor - make sure it covers level width
            (200, SCREEN_HEIGHT - 150, 150, 20),
            (500, SCREEN_HEIGHT - 250, 100, 20),
            (750, SCREEN_HEIGHT - 180, 120, 20),
            (1000, SCREEN_HEIGHT - 300, 150, 20),
            (1300, SCREEN_HEIGHT - 200, 100, 20),
        ],
        "treasures": [
            (250, SCREEN_HEIGHT - 150),
            (550, SCREEN_HEIGHT - 250),
            (150, GROUND_LEVEL),
            (900, GROUND_LEVEL),
            (1100, SCREEN_HEIGHT - 300),
            (1400, GROUND_LEVEL),
        ],
        "obstacles": [
            (400, GROUND_LEVEL),
            (1200, GROUND_LEVEL),
        ],
        "dragons_start": [(1600, GROUND_LEVEL)], # Start dragon further away
        "exit_pos": (1900, GROUND_LEVEL),
        "level_width": 2000,
    },
    # Level 2 (More gaps, slightly trickier platforms)
    {
        "platforms": [
            (0, GROUND_LEVEL, 300, 40),
            (400, GROUND_LEVEL, 500, 40), # Gap in ground
            (1000, GROUND_LEVEL, 1000, 40),# Another gap
            (150, SCREEN_HEIGHT - 120, 100, 20),
            (350, SCREEN_HEIGHT - 200, 80, 20), # Smaller platform
            (600, SCREEN_HEIGHT - 150, 150, 20),
            (850, SCREEN_HEIGHT - 280, 100, 20),
            (1100, SCREEN_HEIGHT - 200, 120, 20),
            (1400, SCREEN_HEIGHT - 100, 150, 20),
            (1700, SCREEN_HEIGHT - 250, 80, 20),
        ],
        "treasures": [
            (200, SCREEN_HEIGHT - 120),
            (400, SCREEN_HEIGHT - 200),
            (650, SCREEN_HEIGHT - 150),
             (50, GROUND_LEVEL),
            (900, SCREEN_HEIGHT - 280),
            (1150, SCREEN_HEIGHT - 200),
            (1450, SCREEN_HEIGHT - 100),
            (1750, SCREEN_HEIGHT - 250),
            (1950, GROUND_LEVEL),
        ],
        "obstacles": [
            (700, GROUND_LEVEL),
            (1300, GROUND_LEVEL),
            (1600, GROUND_LEVEL),
        ],
        "dragons_start": [(1800, GROUND_LEVEL)],
        "exit_pos": (1950, GROUND_LEVEL),
        "level_width": 2000,
    },
    # Level 3 (Verticality, more obstacles)
     {
        "platforms": [
            (0, GROUND_LEVEL, 2200, 40),
            (100, SCREEN_HEIGHT - 100, 80, 20),
            (300, SCREEN_HEIGHT - 180, 100, 20),
            (500, SCREEN_HEIGHT - 260, 120, 20), # Higher platforms
            (750, SCREEN_HEIGHT - 150, 100, 20),
            (950, SCREEN_HEIGHT - 320, 80, 20),
            (1200, SCREEN_HEIGHT - 220, 150, 20),
            (1450, SCREEN_HEIGHT - 120, 100, 20),
            (1700, SCREEN_HEIGHT - 300, 100, 20),
            (1950, SCREEN_HEIGHT - 200, 100, 20),
        ],
        "treasures": [
            (150, SCREEN_HEIGHT - 100),
            (350, SCREEN_HEIGHT - 180),
            (560, SCREEN_HEIGHT - 260),
            (800, SCREEN_HEIGHT - 150),
            (1000, SCREEN_HEIGHT - 320),
            (1275, SCREEN_HEIGHT - 220),
            (1500, SCREEN_HEIGHT - 120),
             (50, GROUND_LEVEL),
            (1750, SCREEN_HEIGHT - 300),
            (2000, SCREEN_HEIGHT - 200),
             (1050, GROUND_LEVEL),
             (1600, GROUND_LEVEL),
        ],
        "obstacles": [
            (250, GROUND_LEVEL),
            (650, SCREEN_HEIGHT - 180), # Obstacle on platform
            (900, GROUND_LEVEL),
            (1400, GROUND_LEVEL),
             (1850, GROUND_LEVEL),
        ],
        "dragons_start": [(1900, SCREEN_HEIGHT - 300)], # Dragon starts higher
        "exit_pos": (2150, GROUND_LEVEL),
        "level_width": 2200,
    },
    # Level 4 (Narrow passages, dragon guarding exit more closely)
     {
        "platforms": [
             # Ground sections
             (0, GROUND_LEVEL, 400, 40),
             (600, GROUND_LEVEL, 500, 40),
             (1300, GROUND_LEVEL, 1100, 40),
             # Mid platforms - create bottlenecks
             (450, SCREEN_HEIGHT - 150, 100, 20), # Jump over gap
             (500, SCREEN_HEIGHT - 250, 80, 20), # Higher jump
             (700, SCREEN_HEIGHT - 180, 150, 20),
             (900, SCREEN_HEIGHT - 300, 100, 20),
             (1150, SCREEN_HEIGHT - 220, 100, 20), # Jump over gap
             (1400, SCREEN_HEIGHT - 160, 120, 20),
             (1650, SCREEN_HEIGHT - 280, 80, 20),
             (1900, SCREEN_HEIGHT - 120, 100, 20),
             (2100, SCREEN_HEIGHT - 200, 100, 20), # Near exit
        ],
        "treasures": [
             (50, GROUND_LEVEL),
             (500, SCREEN_HEIGHT - 150),
             (550, SCREEN_HEIGHT - 250),
             (750, SCREEN_HEIGHT - 180),
             (950, SCREEN_HEIGHT - 300),
             (1200, SCREEN_HEIGHT - 220),
             (800, GROUND_LEVEL),
             (1450, SCREEN_HEIGHT - 160),
             (1700, SCREEN_HEIGHT - 280),
             (1950, SCREEN_HEIGHT - 120),
             (2150, SCREEN_HEIGHT - 200),
             (1500, GROUND_LEVEL),
             (2350, GROUND_LEVEL), # Treasure past exit start
        ],
        "obstacles": [
             (300, GROUND_LEVEL),
             (800, GROUND_LEVEL),
             (1050, GROUND_LEVEL), # Obstacle before gap
             (1550, GROUND_LEVEL),
             (1800, SCREEN_HEIGHT - 160), # Obstacle on platform
             (2200, GROUND_LEVEL), # Near exit
        ],
        "dragons_start": [(2000, GROUND_LEVEL)], # Closer to the later part
        "exit_pos": (2350, GROUND_LEVEL),
        "level_width": 2400,
    },
    # Level 5 (Longer level, two dragons)
     {
        "platforms": [
             (0, GROUND_LEVEL, 2600, 40),
             # Series of small, spaced platforms
             (150, SCREEN_HEIGHT - 100, 70, 20),
             (350, SCREEN_HEIGHT - 150, 70, 20),
             (550, SCREEN_HEIGHT - 200, 70, 20),
             (750, SCREEN_HEIGHT - 120, 70, 20),
             (950, SCREEN_HEIGHT - 250, 70, 20),
             (1150, SCREEN_HEIGHT - 180, 70, 20),
             # Larger central platform area
             (1300, SCREEN_HEIGHT - 300, 200, 20),
             (1550, SCREEN_HEIGHT - 250, 150, 20),
             # More small platforms
             (1750, SCREEN_HEIGHT - 150, 70, 20),
             (1950, SCREEN_HEIGHT - 280, 70, 20),
             (2150, SCREEN_HEIGHT - 100, 70, 20),
             (2350, SCREEN_HEIGHT - 220, 70, 20),
        ],
        "treasures": [
             (185, SCREEN_HEIGHT - 100), (385, SCREEN_HEIGHT - 150),
             (585, SCREEN_HEIGHT - 200), (785, SCREEN_HEIGHT - 120),
             (985, SCREEN_HEIGHT - 250), (1185, SCREEN_HEIGHT - 180),
             (1400, SCREEN_HEIGHT - 300), (1625, SCREEN_HEIGHT - 250),
             (1785, SCREEN_HEIGHT - 150), (1985, SCREEN_HEIGHT - 280),
             (2185, SCREEN_HEIGHT - 100), (2385, SCREEN_HEIGHT - 220),
             (50, GROUND_LEVEL), (1000, GROUND_LEVEL), (2000, GROUND_LEVEL),
        ],
        "obstacles": [
             (450, GROUND_LEVEL),
             (900, GROUND_LEVEL),
             (1450, SCREEN_HEIGHT - 300), # Obstacle on high platform
             (1700, GROUND_LEVEL),
             (2100, GROUND_LEVEL),
             (2450, GROUND_LEVEL),
        ],
        "dragons_start": [
            (2200, GROUND_LEVEL),
            (1400, SCREEN_HEIGHT - 300) # Second dragon on central high platform
        ],
        "exit_pos": (2550, GROUND_LEVEL),
        "level_width": 2600,
    },
    # Level 6 (Maze-like platforms, two dragons)
    {
        "platforms": [
            (0, GROUND_LEVEL, 200, 40),
            (300, GROUND_LEVEL, 300, 40),
            (700, GROUND_LEVEL, 400, 40),
            (1200, GROUND_LEVEL, 300, 40),
            (1600, GROUND_LEVEL, 1200, 40),
            # Ascending section
            (100, SCREEN_HEIGHT - 100, 80, 20),
            (250, SCREEN_HEIGHT - 180, 80, 20),
             (150, SCREEN_HEIGHT - 260, 80, 20), # Step back
             (300, SCREEN_HEIGHT - 340, 80, 20),
             # Mid-air section
             (500, SCREEN_HEIGHT - 250, 100, 20),
             (650, SCREEN_HEIGHT - 180, 100, 20),
             (800, SCREEN_HEIGHT - 280, 100, 20),
             (950, SCREEN_HEIGHT - 210, 100, 20),
             # Descending section
             (1100, SCREEN_HEIGHT - 300, 80, 20),
             (1250, SCREEN_HEIGHT - 200, 80, 20),
             (1400, SCREEN_HEIGHT - 120, 80, 20),
             # High path near dragon
             (1700, SCREEN_HEIGHT - 350, 150, 20),
             (1900, SCREEN_HEIGHT - 280, 100, 20),
             (2100, SCREEN_HEIGHT - 320, 150, 20),
             (2400, SCREEN_HEIGHT - 250, 100, 20),
        ],
        "treasures": [
            (140, SCREEN_HEIGHT - 100), (290, SCREEN_HEIGHT - 180),
            (190, SCREEN_HEIGHT - 260), (340, SCREEN_HEIGHT - 340),
            (550, SCREEN_HEIGHT - 250), (700, SCREEN_HEIGHT - 180),
            (850, SCREEN_HEIGHT - 280), (1000, SCREEN_HEIGHT - 210),
            (1140, SCREEN_HEIGHT - 300), (1290, SCREEN_HEIGHT - 200),
            (1440, SCREEN_HEIGHT - 120), (1775, SCREEN_HEIGHT - 350),
            (1950, SCREEN_HEIGHT - 280), (2175, SCREEN_HEIGHT - 320),
            (2450, SCREEN_HEIGHT - 250),
             (50, GROUND_LEVEL), (800, GROUND_LEVEL), (1300, GROUND_LEVEL), (2750, GROUND_LEVEL)
        ],
        "obstacles": [
            (400, GROUND_LEVEL),
            (600, SCREEN_HEIGHT - 180), # Obstacle on platform
            (1050, GROUND_LEVEL),
             (1300, SCREEN_HEIGHT - 200), # Obstacle on platform
             (1650, GROUND_LEVEL),
             (2000, GROUND_LEVEL),
             (2300, SCREEN_HEIGHT - 320), # High obstacle
             (2600, GROUND_LEVEL),
        ],
        "dragons_start": [
            (2500, SCREEN_HEIGHT - 350), # Original high up dragon
            (1000, GROUND_LEVEL)        # Second dragon on ground path
        ],
        "exit_pos": (2750, GROUND_LEVEL),
        "level_width": 2800,
    },
    # Level 7 (Requires dropping rocks strategically, two dragons)
     {
        "platforms": [
             (0, GROUND_LEVEL, 2800, 40),
             # Section requiring distraction?
             (200, SCREEN_HEIGHT - 100, 300, 20), # Platform above dragon start?
             (600, SCREEN_HEIGHT - 180, 100, 20),
             (800, SCREEN_HEIGHT - 250, 150, 20),
             (1100, SCREEN_HEIGHT - 150, 100, 20),
             # Raised section with obstacles
             (1400, SCREEN_HEIGHT - 280, 200, 20),
             (1700, SCREEN_HEIGHT - 350, 150, 20), # High point
             (2000, SCREEN_HEIGHT - 260, 100, 20),
             # Final stretch
             (2300, SCREEN_HEIGHT - 120, 150, 20),
             (2550, SCREEN_HEIGHT - 200, 100, 20),
        ],
        "treasures": [
             (350, SCREEN_HEIGHT - 100), (650, SCREEN_HEIGHT - 180),
             (875, SCREEN_HEIGHT - 250), (1150, SCREEN_HEIGHT - 150),
             (1500, SCREEN_HEIGHT - 280), (1775, SCREEN_HEIGHT - 350),
             (2050, SCREEN_HEIGHT - 260), (2375, SCREEN_HEIGHT - 120),
             (2600, SCREEN_HEIGHT - 200),
             (100, GROUND_LEVEL), (1000, GROUND_LEVEL), (1900, GROUND_LEVEL), (2700, GROUND_LEVEL)
        ],
        "obstacles": [
             (500, GROUND_LEVEL), # Hiding spot before dragon?
             (750, GROUND_LEVEL),
             (1200, GROUND_LEVEL),
             (1500, SCREEN_HEIGHT - 280), # Obstacle on platform
             (1650, SCREEN_HEIGHT - 280), # Double obstacle
             (2150, GROUND_LEVEL),
             (2450, GROUND_LEVEL), # Obstacle near end
        ],
        "dragons_start": [
            (950, GROUND_LEVEL),        # Original early dragon
            (1800, SCREEN_HEIGHT - 350) # Second dragon near high point
        ],
        "exit_pos": (2750, GROUND_LEVEL),
        "level_width": 2800,
    },
     # Level 8 (More complex fireball dodging sections, two dragons)
     {
         "platforms": [
             (0, GROUND_LEVEL, 3000, 40),
             # Open area for dodging
             (100, SCREEN_HEIGHT - 100, 100, 20),
             (300, SCREEN_HEIGHT - 150, 100, 20),
             (500, SCREEN_HEIGHT - 100, 100, 20),
             (700, SCREEN_HEIGHT - 200, 200, 20), # Wider platform
             # Narrow ledges under dragon
             (1000, SCREEN_HEIGHT - 300, 80, 20),
             (1150, SCREEN_HEIGHT - 320, 80, 20),
             (1300, SCREEN_HEIGHT - 340, 80, 20),
             # Upward climb
             (1500, SCREEN_HEIGHT - 250, 100, 20),
             (1700, SCREEN_HEIGHT - 350, 100, 20), # High platform
             (1900, SCREEN_HEIGHT - 280, 100, 20),
             # Final platforms
             (2200, SCREEN_HEIGHT - 180, 150, 20),
             (2500, SCREEN_HEIGHT - 240, 100, 20),
             (2800, SCREEN_HEIGHT - 150, 100, 20),
         ],
         "treasures": [
             (150, SCREEN_HEIGHT - 100), (350, SCREEN_HEIGHT - 150),
             (550, SCREEN_HEIGHT - 100), (800, SCREEN_HEIGHT - 200),
             (1040, SCREEN_HEIGHT - 300), (1190, SCREEN_HEIGHT - 320),
             (1340, SCREEN_HEIGHT - 340), (1550, SCREEN_HEIGHT - 250),
             (1750, SCREEN_HEIGHT - 350), (1950, SCREEN_HEIGHT - 280),
             (2275, SCREEN_HEIGHT - 180), (2550, SCREEN_HEIGHT - 240),
             (2850, SCREEN_HEIGHT - 150),
             (400, GROUND_LEVEL), (1400, GROUND_LEVEL), (2100, GROUND_LEVEL), (2950, GROUND_LEVEL)
         ],
        "obstacles": [
             (600, GROUND_LEVEL),
             (900, SCREEN_HEIGHT - 200), # Obstacle on platform
             (1600, GROUND_LEVEL),
             (1800, SCREEN_HEIGHT - 350), # High obstacle
             (2400, GROUND_LEVEL),
             (2700, SCREEN_HEIGHT - 180), # Obstacle near end
        ],
        "dragons_start": [
            (1100, SCREEN_HEIGHT - 150), # Original dragon over narrow ledges
            (2400, GROUND_LEVEL)        # Second dragon on ground near end
        ],
         "exit_pos": (2950, GROUND_LEVEL),
         "level_width": 3000,
     },
    # Level 9 (Very high platforms, risk of falling, two dragons)
     {
        "platforms": [
             # Minimal ground
             (0, GROUND_LEVEL, 100, 40),
             (2900, GROUND_LEVEL, 100, 40),
             # Series of high, small platforms
             (200, SCREEN_HEIGHT - 150, 60, 20),
             (400, SCREEN_HEIGHT - 250, 60, 20),
             (600, SCREEN_HEIGHT - 350, 60, 20), # Very high
             (800, SCREEN_HEIGHT - 280, 60, 20),
             (1000, SCREEN_HEIGHT - 400, 60, 20), # Extremely high
             (1200, SCREEN_HEIGHT - 320, 60, 20),
             # Central structure
             (1400, SCREEN_HEIGHT - 200, 150, 20),
             (1600, SCREEN_HEIGHT - 300, 100, 20),
             (1800, SCREEN_HEIGHT - 400, 80, 20), # Peak
             (2000, SCREEN_HEIGHT - 300, 100, 20),
             (2200, SCREEN_HEIGHT - 200, 150, 20),
             # Descent
             (2400, SCREEN_HEIGHT - 350, 60, 20),
             (2600, SCREEN_HEIGHT - 250, 60, 20),
             (2800, SCREEN_HEIGHT - 150, 60, 20),
        ],
        "treasures": [
             (230, SCREEN_HEIGHT - 150), (430, SCREEN_HEIGHT - 250),
             (630, SCREEN_HEIGHT - 350), (830, SCREEN_HEIGHT - 280),
             (1030, SCREEN_HEIGHT - 400), (1230, SCREEN_HEIGHT - 320),
             (1475, SCREEN_HEIGHT - 200), (1650, SCREEN_HEIGHT - 300),
             (1840, SCREEN_HEIGHT - 400), (2050, SCREEN_HEIGHT - 300),
             (2275, SCREEN_HEIGHT - 200), (2430, SCREEN_HEIGHT - 350),
             (2630, SCREEN_HEIGHT - 250), (2830, SCREEN_HEIGHT - 150),
             # Only one ground treasure at start
             (50, GROUND_LEVEL),
        ],
        "obstacles": [
             # Obstacles mostly on platforms
             (500, SCREEN_HEIGHT - 250),
             (900, SCREEN_HEIGHT - 280),
             (1500, SCREEN_HEIGHT - 200),
             (1700, SCREEN_HEIGHT - 300),
             (2100, SCREEN_HEIGHT - 300),
             (2500, SCREEN_HEIGHT - 350),
        ],
        "dragons_start": [
            (1700, SCREEN_HEIGHT - 150), # Original mid-level dragon
            (300, SCREEN_HEIGHT - 150)  # Second dragon on early high platform
        ],
        "exit_pos": (2950, GROUND_LEVEL),
        "level_width": 3000,
    },
     # Level 10 (Final challenge: long, complex, THREE dragons near exit)
     {
        "platforms": [
             (0, GROUND_LEVEL, 3500, 40), # Very long ground
             # Early climb
             (150, SCREEN_HEIGHT - 100, 100, 20),
             (350, SCREEN_HEIGHT - 200, 100, 20),
             (550, SCREEN_HEIGHT - 300, 100, 20),
             # Mid-section with gaps and obstacles
             (800, SCREEN_HEIGHT - 150, 150, 20),
             (1100, SCREEN_HEIGHT - 250, 100, 20),
             (1300, SCREEN_HEIGHT - 100, 80, 20), # Drop down
             (1500, SCREEN_HEIGHT - 350, 120, 20), # High jump
             (1750, SCREEN_HEIGHT - 220, 100, 20),
             # High path near dragon's zone
             (2000, SCREEN_HEIGHT - 400, 200, 20),
             (2300, SCREEN_HEIGHT - 300, 150, 20),
             (2550, SCREEN_HEIGHT - 420, 100, 20), # Very high peak
             (2750, SCREEN_HEIGHT - 350, 150, 20),
             # Descent to exit
             (3000, SCREEN_HEIGHT - 200, 100, 20),
             (3200, SCREEN_HEIGHT - 120, 100, 20),
        ],
        "treasures": [
             (200, SCREEN_HEIGHT - 100), (400, SCREEN_HEIGHT - 200),
             (600, SCREEN_HEIGHT - 300), (875, SCREEN_HEIGHT - 150),
             (1150, SCREEN_HEIGHT - 250), (1340, SCREEN_HEIGHT - 100),
             (1560, SCREEN_HEIGHT - 350), (1800, SCREEN_HEIGHT - 220),
             (2100, SCREEN_HEIGHT - 400), (2375, SCREEN_HEIGHT - 300),
             (2600, SCREEN_HEIGHT - 420), (2825, SCREEN_HEIGHT - 350),
             (3050, SCREEN_HEIGHT - 200), (3250, SCREEN_HEIGHT - 120),
             # Lots of ground treasures too
             (50, GROUND_LEVEL), (1000, GROUND_LEVEL), (1600, GROUND_LEVEL),
             (2200, GROUND_LEVEL), (2900, GROUND_LEVEL), (3450, GROUND_LEVEL),
        ],
        "obstacles": [
             (450, GROUND_LEVEL),
             (700, SCREEN_HEIGHT - 150),
             (1200, GROUND_LEVEL),
             (1400, SCREEN_HEIGHT - 100),
             (1650, SCREEN_HEIGHT - 350),
             (1900, GROUND_LEVEL),
             (2100, SCREEN_HEIGHT - 400), # Obstacles high up
             (2450, SCREEN_HEIGHT - 300),
             (2700, GROUND_LEVEL),
             (2950, SCREEN_HEIGHT - 200),
             (3150, GROUND_LEVEL),
             (3350, GROUND_LEVEL), # Obstacle right before exit
        ],
        "dragons_start": [
            (3100, GROUND_LEVEL),       # Original dragon guarding the exit
            (1500, SCREEN_HEIGHT - 350), # Second dragon mid-level, high platform
            (600, SCREEN_HEIGHT - 300)   # Third dragon on early high platform
        ],
        "exit_pos": (3450, GROUND_LEVEL),
        "level_width": 3500,
    },
]

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


class BigTreasure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_orig = load_image("big_treasure.png", BIG_TREASURE_SIZE)
        if self.image_orig is None:
            self.image = pygame.Surface(BIG_TREASURE_SIZE)
            self.image.fill(YELLOW) # Fallback color
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

            landed_this_frame = False
            # Check for landing on a platform or ground
            if self.rect.bottom >= GROUND_LEVEL:
                self.rect.bottom = GROUND_LEVEL
                landed_this_frame = True
            else:
                 # Check platform collision
                 hit_platforms = pygame.sprite.spritecollide(self, self.game.platforms, False)
                 if hit_platforms:
                     self.rect.bottom = hit_platforms[0].rect.top
                     landed_this_frame = True

            if landed_this_frame:
                 self.landed = True
                 self.vel_y = 0
                 # Convert tuple to Vector2
                 self.land_pos = pygame.math.Vector2(self.rect.midbottom)
                 self.game.newly_landed_rocks.append(self) # Add to game list

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
        self.state = "start" # states: start, playing, level_complete, game_over_lose, game_won_all
        self.total_score = 0 # Score across all levels
        self.current_level_index = 0
        self.world_shift = 0
        self.num_selected_dragons = 1 # Default to 1 dragon
        # level_width and world_rect will be set in new()
        self.level_width = 0
        self.world_rect = None # Will be set based on level width
        self.newly_landed_rocks = [] # Track rocks landing this frame

        self.load_data()
        self.dragons = pygame.sprite.Group() # Group for all dragons
        self.big_treasure_sprite = None
        self.big_treasure_spawned = False
        self.total_treasures_in_level = 0

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


    def new(self, level_index):
        """Start a new game or level"""
        if level_index >= len(LEVELS):
            self.state = "game_won_all" # Finished all levels
            return # Don't proceed with level setup

        self.current_level_index = level_index
        self.level_data = LEVELS[level_index]
        self.level_width = self.level_data["level_width"]
        self.world_rect = pygame.Rect(0, 0, self.level_width, SCREEN_HEIGHT)
        self.score = 0 # Reset score for the new level
        self.world_shift = 0
        self.newly_landed_rocks.clear() # Clear landed rocks for the new level
        self.big_treasure_spawned = False
        self.big_treasure_sprite = None
        self.total_treasures_in_level = 0

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.treasures = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        self.dropped_rocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group() # Group for things that hurt player
        self.dragons = pygame.sprite.Group() # Clear/initialize dragons group for the level

        # Create player
        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Load level elements from self.level_data
        # Platforms (including the ground implicitly if defined)
        for p_data in self.level_data["platforms"]:
            platform = Platform(*p_data)
            self.all_sprites.add(platform)
            self.platforms.add(platform)

        # Treasures
        for t_pos in self.level_data["treasures"]:
            treasure = Treasure(*t_pos)
            self.all_sprites.add(treasure)
            self.treasures.add(treasure)
        self.total_treasures_in_level = len(self.treasures) # Store initial count

        # Obstacles
        for o_pos in self.level_data["obstacles"]:
            obstacle = Obstacle(*o_pos)
            self.all_sprites.add(obstacle)
            self.obstacles.add(obstacle)
            self.platforms.add(obstacle) # Treat obstacles as platforms for collision

        # Create Dragon(s)
        num_to_spawn = self.num_selected_dragons
        spawned_dragon_positions = []

        # Gather predefined positions from level data
        predefined_positions_from_level_raw = []
        if "dragons_start" in self.level_data:
            predefined_positions_from_level_raw.extend(self.level_data["dragons_start"])
        elif "dragon_start" in self.level_data: # Support old single dragon format
            predefined_positions_from_level_raw.append(self.level_data["dragon_start"])

        # Filter predefined positions to be at least 25% into the level
        min_spawn_x = self.level_width * 0.25
        predefined_positions_from_level = [
            pos for pos in predefined_positions_from_level_raw if pos[0] >= min_spawn_x
        ]

        # Use predefined positions first, up to num_to_spawn
        for i in range(min(num_to_spawn, len(predefined_positions_from_level))):
            spawned_dragon_positions.append(predefined_positions_from_level[i])

        # If more dragons are needed, determine positions for them
        num_still_to_spawn = num_to_spawn - len(spawned_dragon_positions)

        if num_still_to_spawn > 0:
            # Gather potential spawn surfaces (tops of actual platforms)
            # self.platforms group is already populated with Platform and Obstacle objects.
            candidate_platform_spawn_points = []
            for plat_sprite in self.platforms.sprites():
                # Ensure we are spawning on actual Platform instances, not Obstacles
                if type(plat_sprite) is Platform:
                    # Dragon constructor expects (game, center_x, bottom_y)
                    # Platform's rect.top is the y-coordinate of its top edge.
                    # So, dragon's bottom will be at platform's top.
                    if plat_sprite.rect.centerx >= min_spawn_x: # Check 25% rule
                        candidate_platform_spawn_points.append((plat_sprite.rect.centerx, plat_sprite.rect.top))

            if not candidate_platform_spawn_points:
                # Fallback: if no platforms (e.g. only empty space or unplatformed ground),
                # use ground level at random x positions. This should be rare if levels
                # always define ground as platforms.
                for _ in range(num_still_to_spawn):
                    spawn_area_start_x = max(50, int(min_spawn_x)) # Ensure at least 25%
                    spawn_area_end_x = self.level_width - 50
                    # Ensure valid range for randint
                    if spawn_area_start_x >= spawn_area_end_x:
                        # Default to center for very narrow levels if range is invalid
                        # or if min_spawn_x pushes start beyond end.
                        rand_x = self.level_width // 2
                        if rand_x < min_spawn_x: # If center is still too early, push it
                            rand_x = int(min_spawn_x + (spawn_area_end_x - min_spawn_x)/2) if min_spawn_x < spawn_area_end_x else int(min_spawn_x)

                    else:
                        rand_x = random.randint(spawn_area_start_x, spawn_area_end_x)
                    spawned_dragon_positions.append((rand_x, GROUND_LEVEL))
            else:
                # Place additional dragons on these platform tops, cycling if necessary
                for i in range(num_still_to_spawn):
                    # Cycle through available platform spawn points
                    chosen_surface_idx = i % len(candidate_platform_spawn_points)
                    chosen_surface = candidate_platform_spawn_points[chosen_surface_idx]
                    spawned_dragon_positions.append(chosen_surface)
        
        # Now, create the dragons from all determined spawned_dragon_positions
        for d_pos_data in spawned_dragon_positions:
            dragon_x_center, dragon_y_bottom = d_pos_data
            dragon = Dragon(self, dragon_x_center, dragon_y_bottom)
            self.all_sprites.add(dragon)
            self.enemies.add(dragon)
            self.dragons.add(dragon)

        # Create Exit
        exit_pos = self.level_data["exit_pos"]
        self.exit_sprite = Exit(*exit_pos)
        self.all_sprites.add(self.exit_sprite)

        self.state = "playing"
        self.run()

    def run(self):
        """Game Loop for a single level"""
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
            # Calculate how much the player has moved past the threshold
            scroll_amount = player_screen_x - (SCREEN_WIDTH - SCROLL_THRESH)
            # Scroll the world left, but don't exceed player's speed
            scroll = -min(int(abs(self.player.vel.x)), int(scroll_amount))


        # If player moves past the left scroll threshold towards the left
        elif player_screen_x < SCROLL_THRESH and self.player.vel.x < 0:
             # Calculate how much the player has moved past the threshold
            scroll_amount = SCROLL_THRESH - player_screen_x
            # Scroll the world right, but don't exceed player's speed
            scroll = min(int(abs(self.player.vel.x)), int(scroll_amount))


        # Clamp the world_shift to the level boundaries
        potential_new_shift = self.world_shift + scroll
        max_left_shift = 0 # Screen aligned with left edge of level
        max_right_shift = -(self.level_width - SCREEN_WIDTH) # Screen aligned with right edge

        # Prevent scrolling beyond level boundaries
        if self.level_width <= SCREEN_WIDTH:
            self.world_shift = 0 # Don't scroll if level fits on screen
        else:
             self.world_shift = max(max_right_shift, min(max_left_shift, potential_new_shift))

        # Calculate the actual scroll applied after clamping (for sprite shifting)
        # This ensures sprites don't shift if the scroll was clamped
        actual_scroll = self.world_shift - (potential_new_shift - scroll)

        # Apply the *actual* scroll to all sprites EXCEPT the player
        if actual_scroll != 0:
            for sprite in self.all_sprites:
                if sprite != self.player:
                    # Update rect position directly
                    sprite.rect.x += actual_scroll
                    # Also update vector positions if they exist (Dragon, Fireball, DroppedRock)
                    if hasattr(sprite, 'pos') and sprite.pos is not None:
                        try:
                            sprite.pos.x += actual_scroll
                        except AttributeError:
                            # Handle cases where pos might not be a Vector2 (e.g., None temporarily)
                            pass


        # Player boundary checks are handled within Player.update relative to level_width

        # --- Game Logic ---
        # Player collects treasures
        treasure_hits = pygame.sprite.spritecollide(self.player, self.treasures, True) # True removes the treasure
        for treasure in treasure_hits:
            self.score += 1
            self.coin_sound.play()
            # Check if collecting treasure wakes dragon (optional noise mechanic)
            for dragon_sprite in self.dragons: # Iterate through all dragons
                if dragon_sprite.state == "sleeping":
                    # Player position is self.player.pos (Vector2 for center)
                    # Dragon position is dragon_sprite.pos (Vector2 for center)
                    dist_to_dragon = self.player.pos.distance_to(dragon_sprite.pos)
                    # Make noise more likely to wake dragon if closer
                    # Ensure DRAGON_WAKE_RANGE is not zero to avoid division error
                    if DRAGON_WAKE_RANGE > 0:
                        wake_chance = max(0, (DRAGON_WAKE_RANGE * 1.5 - dist_to_dragon) / (DRAGON_WAKE_RANGE * 1.5))
                        if random.random() < wake_chance * 0.5: # 50% chance based on proximity
                            print("Treasure collection noise woke a dragon!")
                            dragon_sprite.wake_up()
                            # Potentially, a single treasure could wake multiple nearby sleeping dragons.

        # Check if all treasures collected to spawn Big Treasure
        if self.total_treasures_in_level > 0 and len(self.treasures) == 0 and not self.big_treasure_spawned:
            if self.exit_sprite: # Ensure exit exists
                # Spawn Big Treasure at the exit location
                self.big_treasure_sprite = BigTreasure(self.exit_sprite.rect.centerx, self.exit_sprite.rect.bottom)
                self.all_sprites.add(self.big_treasure_sprite)
                self.big_treasure_spawned = True
                print("All treasures collected! A Big Treasure appears!")

        # Player collects Big Treasure
        if self.big_treasure_sprite and self.big_treasure_sprite.alive(): # Check if it exists and is alive
            if pygame.sprite.collide_rect(self.player, self.big_treasure_sprite):
                self.score *= 2 # Double current level's score
                self.coin_sound.play() # Reuse coin sound
                self.big_treasure_sprite.kill()
                self.big_treasure_sprite = None # Clear reference
                print("Big Treasure collected! Score doubled for this level!")

        # Player hits exit
        if pygame.sprite.collide_rect(self.player, self.exit_sprite):
            print(f"Level {self.current_level_index + 1}/{len(LEVELS)} Complete!")
            self.total_score += self.score # Add level score to total
            self.current_level_index += 1
            self.playing = False # Exit current level loop
            if self.current_level_index >= len(LEVELS):
                self.state = "game_won_all" # Finished last level
            else:
                self.state = "level_complete" # Proceed to next level

        # Player hits dragon or fireballs
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_rect_ratio(0.8)) # Smaller hitbox
        fireball_hits = pygame.sprite.spritecollide(self.player, self.fireballs, True, pygame.sprite.collide_rect_ratio(0.8)) # Fireballs disappear on hit

        player_hit_active_dragon = False
        if enemy_hits:
            for enemy in enemy_hits:
                if isinstance(enemy, Dragon) and enemy.state != "sleeping":
                    player_hit_active_dragon = True
                    break
        
        if player_hit_active_dragon or fireball_hits:
            # Only lose if dragon is awake OR if hit by a fireball (which only exists if dragon is awake/shooting)
            # This condition is now handled by player_hit_active_dragon
            print("Game Over!")
            self.hit_sound.play()
            self.playing = False # Exit current level loop
            self.state = "game_over_lose"


        # Check for distraction by newly landed rocks
        rocks_to_kill_after_distraction = []
        for rock in self.newly_landed_rocks:
            if rock.land_pos:
                if rock in rocks_to_kill_after_distraction: # Already processed this rock
                    continue
                for dragon_sprite in self.dragons:
                    if dragon_sprite.state != "sleeping": # Only active dragons can be distracted
                         dist_to_dragon_from_rock = rock.land_pos.distance_to(dragon_sprite.pos)
                         if dist_to_dragon_from_rock < LAND_SOUND_RADIUS:
                              dragon_sprite.get_distracted(rock.land_pos)
                              rocks_to_kill_after_distraction.append(rock)
                              break # This rock has distracted a dragon, its purpose is served.
        
        for rock_to_kill in rocks_to_kill_after_distraction:
            if rock_to_kill.alive(): # Check if it wasn't killed by something else
                rock_to_kill.kill()

        # Clear the list after checking (do this once per frame)
        self.newly_landed_rocks.clear()


        # Player hits obstacles (stop movement) - Collision handled in Player update

        # --- Remove off-screen fireballs/rocks ---
        for fireball in self.fireballs:
             # Use screen rect shifted by world_shift to check visibility
             screen_bounds = self.screen.get_rect().move(-self.world_shift, 0)
             if not screen_bounds.colliderect(fireball.rect):
                  fireball.kill()
        for rock in self.dropped_rocks:
            if rock.rect.top > SCREEN_HEIGHT: # Or just check if below screen
                 rock.kill()


        # Keep player and dragon within world bounds (mostly handled in sprites, but good failsafe)
        if self.player.rect.left < 0: self.player.rect.left = 0; self.player.pos.x = self.player.rect.centerx
        if self.player.rect.right > self.level_width: self.player.rect.right = self.level_width; self.player.pos.x = self.player.rect.centerx
        for dragon_sprite in self.dragons:
            if dragon_sprite.rect.left < 0: dragon_sprite.rect.left = 0; dragon_sprite.pos.x = dragon_sprite.rect.centerx
            if dragon_sprite.rect.right > self.level_width: dragon_sprite.rect.right = self.level_width; dragon_sprite.pos.x = dragon_sprite.rect.centerx


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
                 # Allow restarting from game over / win screens
                 elif self.state == "start" or self.state == "game_over_lose" or self.state == "game_won_all":
                     if event.key != pygame.K_ESCAPE:
                          # Reset for a completely new game
                          self.current_level_index = 0
                          self.total_score = 0
                          self.state = "playing" # Trigger new game start in main loop
                          self.playing = False # End current screen loop (start/game over)

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
            screen_rect = self.screen.get_rect()
            sprite_screen_pos = sprite.rect.move(self.world_shift, 0)
            if screen_rect.colliderect(sprite_screen_pos):
                 self.screen.blit(sprite.image, sprite_screen_pos)


        # Draw Score and Level Info
        level_text = f"Level: {self.current_level_index + 1}/{len(LEVELS)}"
        self.draw_text(level_text, 22, WHITE, 80, 15) # Top Left
        self.draw_text(f"Treasures: {self.score}", 22, WHITE, SCREEN_WIDTH / 2, 15) # Top Middle (Level Score)
        self.draw_text(f"Total: {self.total_score}", 22, WHITE, SCREEN_WIDTH - 80, 15) # Top Right (Total Score)


        # Draw Dragon State (for debugging/clarity)
        if self.dragons and self.dragons.sprites(): # Check if the group is not empty and has sprites
            first_dragon = self.dragons.sprites()[0]
            state_text = "Dragon(s): "
            state_color = WHITE
            if first_dragon.state == "sleeping":
                state_text += "Zzzz"
            elif first_dragon.state == "waking":
                state_text += "Waking..."
                state_color = YELLOW
            elif first_dragon.state == "chasing":
                state_text += "AWAKE!"
                state_color = RED
            elif first_dragon.state == "distracted":
                state_text += "Distracted"
                state_color = YELLOW
            self.draw_text(state_text, 18, state_color, SCREEN_WIDTH / 2, 45)


        # After drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        """Display the start screen"""
        self.current_level_index = 0 # Ensure starting from level 1
        self.total_score = 0      # Ensure total score is reset
        # self.num_selected_dragons = 1 # Reset here or ensure it's handled before calling new game

        self.screen.blit(self.background, self.background_rect) # Use game background
        self.draw_text("Dragon Cave Adventure!", 48, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 - 20)
        self.draw_text("Use ARROW keys to move, UP to jump", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
        self.draw_text("SPACEBAR to drop a rock (distracts awake dragon)", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.draw_text(f"Collect treasures and clear all {len(LEVELS)} levels!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        self.draw_text("Don't get too close to the sleeping dragon...", 22, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80)

        self.draw_text(f"Number of Dragons (1-5): {self.num_selected_dragons}", 22, LIGHT_BLUE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120)
        self.draw_text("Use + / - keys to change. (Or UP/DOWN arrows)", 18, LIGHT_BLUE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150)

        self.draw_text("Press ENTER to start", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 20)
        pygame.display.flip()
        self.handle_start_screen_input() # Changed from wait_for_key
        # self.state = "playing" # Set state to start the game loop - will be handled by input handler

    def show_game_over_screen(self, status):
        """Display game over or game won screen"""
        if not self.running: # Don't show if we quit during game over
             return
        self.screen.blit(self.background, self.background_rect) # Use game background

        if status == "game_won_all":
            self.draw_text("YOU CONQUERED THE CAVE!", 48, GREEN, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
            self.draw_text(f"You collected a total of {self.total_score} treasures!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        elif status == "game_over_lose":
            self.draw_text("GAME OVER!", 48, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
            self.draw_text("The dragon got you!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.draw_text(f"You reached Level {self.current_level_index + 1} with {self.total_score} total treasures.", 20, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)

        self.draw_text("Press any key to play again (from Level 1)", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        pygame.display.flip()
        self.wait_for_key()

    def handle_start_screen_input(self):
        """Pause the game until a key is pressed, handles dragon selection."""
        waiting = True
        while waiting and self.running: # Check self.running too
            self.clock.tick(FPS / 2) # Lower FPS while waiting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN: # Changed from KEYUP for responsiveness
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS or event.key == pygame.K_UP:
                        self.num_selected_dragons = min(5, self.num_selected_dragons + 1)
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_DOWN:
                        self.num_selected_dragons = max(1, self.num_selected_dragons - 1)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        waiting = False
                        self.state = "playing"
                    # elif event.type == pygame.KEYUP: # Original logic was here for any other key
                    #     waiting = False # Any other key ends wait, now specifically ENTER

            # Redraw screen to show updated dragon count
            if waiting and self.running: # Only redraw if still in this loop
                self.screen.blit(self.background, self.background_rect)
                self.draw_text("Dragon Cave Adventure!", 48, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 - 20)
                self.draw_text("Use ARROW keys to move, UP to jump", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
                self.draw_text("SPACEBAR to drop a rock (distracts awake dragon)", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                self.draw_text(f"Collect treasures and clear all {len(LEVELS)} levels!", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
                self.draw_text("Don't get too close to the sleeping dragon...", 22, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80)
                self.draw_text(f"Number of Dragons (1-5): {self.num_selected_dragons}", 22, LIGHT_BLUE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120)
                self.draw_text("Use + / - keys to change. (Or UP/DOWN arrows)", 18, LIGHT_BLUE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150)
                self.draw_text("Press ENTER to start", 22, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 20)
                pygame.display.flip()

    def wait_for_key(self):
        """Pause the game until a key is pressed"""
        waiting = True
        while waiting and self.running: # Check self.running too
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
g.show_start_screen() # Sets state to "playing" if user proceeds

while g.running:
    if g.state == "playing" or g.state == "level_complete":
        # If starting after a game over/win, index/score are already reset by the logic below
        g.new(g.current_level_index) # Start or continue level (calls run())
        # run() loop finishes, state is now level_complete, game_over_lose, or game_won_all

    # Handle transitions AFTER a level attempt finishes
    if g.state == "game_won_all":
        g.show_game_over_screen("game_won_all") # Displays screen and waits for key
        if g.running: # If user didn't quit on the game over screen
             # Reset for a new game
             g.current_level_index = 0
             g.total_score = 0
             g.state = "playing" # Set state to start level 1 on next loop iteration
    elif g.state == "game_over_lose":
         g.show_game_over_screen("game_over_lose") # Displays screen and waits for key
         if g.running: # If user didn't quit on the game over screen
              # Reset for a new game
              g.current_level_index = 0
              g.total_score = 0
              g.state = "playing" # Set state to start level 1 on next loop iteration

    # If state is "level_complete", the top 'if' condition will catch it
    # on the next iteration and call g.new() with the incremented index.
    # If g.running becomes False (e.g., ESC pressed during wait_for_key), the loop terminates.


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
# - Add level transition screen (e.g., "Level X Complete!")
# - Save high scores.
# --- End Modifications --- 