from game import *

# fps
FPS = 60

# pygame init
pygame.init()
pygame.mixer.init()
pygame.font.init()

# game state
game_state = GameState()

# clock
clock = pygame.time.Clock()

# background
background = Background(
    "assets/flappy-bird-assets/sprites/background-day.png",
    "assets/flappy-bird-assets/sprites/background-night.png",
    "assets/flappy-bird-assets/sprites/title.png",
    "assets/flappy-bird-assets/sprites/gameover.png",
    "assets/flappy-bird-assets/sprites/message.png",
    "assets/flappy-bird-assets/favicon.ico",
    "Flappy Bird"
)

background.win_displaying()

# floor
floor = Floor("assets/flappy-bird-assets/sprites/base.png")

# bird
bird = Bird([
    "assets/flappy-bird-assets/sprites/redbird-upflap.png",
    "assets/flappy-bird-assets/sprites/redbird-midflap.png",
    "assets/flappy-bird-assets/sprites/redbird-downflap.png",
],
    [
        "assets/flappy-bird-assets/sprites/bluebird-upflap.png",
        "assets/flappy-bird-assets/sprites/bluebird-midflap.png",
        "assets/flappy-bird-assets/sprites/bluebird-downflap.png",
    ],
    [
        "assets/flappy-bird-assets/sprites/yellowbird-upflap.png",
        "assets/flappy-bird-assets/sprites/yellowbird-midflap.png",
        "assets/flappy-bird-assets/sprites/yellowbird-downflap.png",
    ],
    "assets/flappy-bird-assets/audio/wing.wav",
    "assets/flappy-bird-assets/audio/point.wav",
    "assets/flappy-bird-assets/audio/die.wav",
    "assets/flappy-bird-assets/audio/hit.wav",
    "assets/flappy-bird-assets/audio/swoosh.wav"
)

# pipe
pipe = Pipe(
    background,
    floor,
    "assets/flappy-bird-assets/sprites/pipe-green.png",
    "assets/flappy-bird-assets/sprites/pipe-red.png"
)
pipe_group = pygame.sprite.Group()

# score
score = Score(
    "assets/flappy-bird-assets/sprites/0.png",
    "assets/flappy-bird-assets/sprites/1.png",
    "assets/flappy-bird-assets/sprites/2.png",
    "assets/flappy-bird-assets/sprites/3.png",
    "assets/flappy-bird-assets/sprites/4.png",
    "assets/flappy-bird-assets/sprites/5.png",
    "assets/flappy-bird-assets/sprites/6.png",
    "assets/flappy-bird-assets/sprites/7.png",
    "assets/flappy-bird-assets/sprites/8.png",
    "assets/flappy-bird-assets/sprites/9.png",
)

# game loop
while game_state.running:
    game_state.run(bird, pipe_group, background, floor, score)
    clock.tick(FPS)
