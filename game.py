import random
import pygame
import sys

# constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
INTERVAL = 1500  # in millisecond
BLINK_INTERVAL = 500  # in millisecond
TRANSITION_DURATION = 500  # in millisecond
FADE_DURATION = 50  # in millisecond
PIPE_GAP = 100


class Background:
    def __init__(self, bg1_path, bg2_path, intro_bg, game_over_bg, get_ready_bg, icon_path, win_caption, pos=(0, 0)):
        super().__init__()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window_surf = [
            pygame.image.load(bg1_path).convert_alpha(),
            pygame.image.load(bg2_path).convert_alpha()
        ]
        self.win_caption = win_caption
        self.icon_path = icon_path
        self.pos = pos
        self.current_bg = random.choice(self.window_surf)

        self.intro_bg = pygame.image.load(intro_bg).convert_alpha()
        self.intro_bg_rect = self.intro_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

        self.get_ready_bg = pygame.image.load(get_ready_bg).convert_alpha()
        self.get_ready_bg_rect = self.get_ready_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.game_over_bg = pygame.image.load(game_over_bg).convert_alpha()
        self.game_over_bg_rect = self.game_over_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

        self.flappy_font = pygame.font.SysFont("assets/font/FlappybirdyRegular-KaBW.ttf", 35)
        self.intro_font = self.flappy_font.render("Press S to start", False, (0, 0, 0))
        self.intro_font_rect = self.intro_font.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 * 2))
        self.game_over_font = self.flappy_font.render("Press R to restart", False, (0, 0, 0))
        self.game_over_font_rect = self.game_over_font.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 * 2))

        self.text_blink_timer = pygame.time.get_ticks()
        self.show_text = True

    def update_blink(self):
        # Update the blink timer
        current_time = pygame.time.get_ticks()
        if current_time - self.text_blink_timer > BLINK_INTERVAL:
            self.show_text = not self.show_text
            self.text_blink_timer = current_time
            # print(f"Blink Update: {self.show_text}")

    def win_displaying(self):
        pygame.display.set_caption(self.win_caption)
        pygame.display.set_icon(pygame.image.load(self.icon_path).convert_alpha())
        self.current_bg = random.choice(self.window_surf)

    def draw_intro(self):
        self.window.blit(self.intro_bg, self.intro_bg_rect)
        if self.show_text:
            self.window.blit(self.intro_font, self.intro_font_rect)

    def draw_get_ready(self):
        self.window.blit(self.get_ready_bg, self.get_ready_bg_rect)

    def draw_game_over(self):
        self.window.blit(self.game_over_bg, self.game_over_bg_rect)
        if self.show_text:
            self.window.blit(self.game_over_font, self.game_over_font_rect)

    def draw(self):
        self.window.blit(self.current_bg, self.pos)


class Floor(pygame.sprite.Sprite):
    def __init__(self, floor_path):
        super().__init__()
        self.floor_img = pygame.image.load(floor_path).convert_alpha()
        self.floor_width = self.floor_img.get_width()

        self.floor_rect1 = self.floor_img.get_rect(bottomleft=(0, SCREEN_HEIGHT))
        self.floor_rect2 = self.floor_img.get_rect(bottomleft=(self.floor_width, SCREEN_HEIGHT))

    def update(self):
        self.floor_rect1.x -= 2
        self.floor_rect2.x -= 2

        if self.floor_rect1.x + self.floor_width < 0:
            self.floor_rect1.x = self.floor_rect2.x + self.floor_width

        if self.floor_rect2.x + self.floor_width < 0:
            self.floor_rect2.x = self.floor_rect1.x + self.floor_width

    def draw(self, window):
        window.blit(self.floor_img, self.floor_rect1)
        window.blit(self.floor_img, self.floor_rect2)


class Bird(pygame.sprite.Sprite):
    def __init__(self,
                 red_bird_paths,
                 blue_bird_paths,
                 yellow_bird_paths,
                 flap_sound_path,
                 pass_sound_path,
                 dead_sound_path,
                 hit_sound_path,
                 swoosh_sound_path,
                 current_flap="mid",
                 velocity_y=0,
                 flap_power=-4,
                 flap_delay=15):
        super().__init__()
        self.bird_dict = {
            "red": [
                pygame.image.load(red_bird_paths[0]).convert_alpha(),
                pygame.image.load(red_bird_paths[1]).convert_alpha(),
                pygame.image.load(red_bird_paths[2]).convert_alpha()
            ],
            "blue": [
                pygame.image.load(blue_bird_paths[0]).convert_alpha(),
                pygame.image.load(blue_bird_paths[1]).convert_alpha(),
                pygame.image.load(blue_bird_paths[2]).convert_alpha()
            ],
            "yellow": [
                pygame.image.load(yellow_bird_paths[0]).convert_alpha(),
                pygame.image.load(yellow_bird_paths[1]).convert_alpha(),
                pygame.image.load(yellow_bird_paths[2]).convert_alpha()
            ]
        }
        self.current_color = random.choice(list(self.bird_dict.keys()))
        self.current_flap = current_flap
        self.current_idx = 0
        self.bird_images = self.bird_dict[self.current_color]
        self.bird_image = self.bird_images[self.current_idx]
        self.bird_rect = self.bird_image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))

        self.velocity_y = velocity_y
        self.flap_power = flap_power
        self.flap_delay = flap_delay
        self.flap_counter = 0
        self.angle = 0

        self.flap_sound = pygame.mixer.Sound(flap_sound_path)
        self.pass_sound = pygame.mixer.Sound(pass_sound_path)
        self.dead_sound = pygame.mixer.Sound(dead_sound_path)
        self.hit_sound = pygame.mixer.Sound(hit_sound_path)
        self.swoosh_sound = pygame.mixer.Sound(swoosh_sound_path)

        self.flap_channel = pygame.mixer.Channel(1)

        self.intro = True
        self.game_over = False
        self.animate = True

    def flap(self):
        if not self.game_over:
            self.velocity_y = self.flap_power
            self.current_idx = 0  # reset img index
            self.current_flap = "up"
            self.angle = 25  # tilt bird

    def gravity(self):
        # implement gravity
        self.velocity_y += 0.3
        self.bird_rect.y += self.velocity_y

        # bird needs to stay within window
        self.bird_rect.y = max(0, min(SCREEN_HEIGHT - self.bird_rect.height, self.bird_rect.y))

        # rotate bird
        if self.velocity_y < 0:
            self.angle = min(self.angle + 5, 25)
        else:
            self.angle = max(self.angle - 5, -80)

    def animate_bird(self):
        if self.flap_counter >= self.flap_delay and self.animate:
            self.current_idx = (self.current_idx + 1) % len(self.bird_images)
            self.bird_image = self.bird_images[self.current_idx]
            self.flap_counter = 0  # reset flap counter
        else:
            self.flap_counter += 1

    def update(self):
        # apply gravity
        if not self.intro:
            self.gravity()

        # animate flappy bird
        self.animate_bird()

    def sound_play(self):
        self.flap_channel.play(self.flap_sound)

    def sound_stop(self):
        self.flap_channel.stop()

    def hit_sound_play(self):
        self.hit_sound.play()

    def dead_sound_play(self):
        self.dead_sound.play()

    def pass_sound_play(self):
        self.pass_sound.play()

    def swoosh_sound_play(self):
        self.swoosh_sound.play()

    def draw(self, window):
        rotate_bird = pygame.transform.rotate(self.bird_image, self.angle)
        new_bird_rect = rotate_bird.get_rect(center=self.bird_rect.center)
        window.blit(rotate_bird, new_bird_rect.topleft)


class Pipe(pygame.sprite.Sprite):
    def __init__(self,
                 background,
                 floor,
                 green_pipe_path,
                 red_pipe_path):
        super().__init__()
        self.background = background
        self.floor = floor
        self.pipe_dict = {
            "green": pygame.image.load(green_pipe_path).convert_alpha(),
            "red": pygame.image.load(red_pipe_path).convert_alpha()
        }

        # match background and pipe color
        if self.background.current_bg == self.background.window_surf[0]:
            self.pipe_img = self.pipe_dict["green"]
        else:
            self.pipe_img = self.pipe_dict["red"]

        # bottom pipes
        self.pipe_rect = self.pipe_img.get_rect(
            midtop=(SCREEN_WIDTH+26, random.randint(120, SCREEN_HEIGHT - PIPE_GAP - 30))
        )

        # top pipe
        self.flipped_pipe = pygame.transform.flip(self.pipe_img, False, True)
        self.top_pipe_rect = self.flipped_pipe.get_rect(
            midbottom=(SCREEN_WIDTH+26, self.pipe_rect.top - PIPE_GAP)
        )

        # bird passing flag
        self.bird_passed = False

    def update(self, game_over=False):
        if not game_over:
            self.pipe_rect.x -= 2
            self.top_pipe_rect.x -= 2

            # kill pipe if it goes off window
            if self.pipe_rect.right < 0 and self.top_pipe_rect.right < 0:
                self.kill()

    def check_bird_pass(self, bird):
        # Check if the bird has passed the pipe
        if not self.bird_passed and bird.bird_rect.left > self.pipe_rect.right:
            self.bird_passed = True
            bird.pass_sound_play()  # Play pass sound when bird passes the pipe
            return True
        return False

    def draw(self, window):
        window.blit(self.pipe_img, self.pipe_rect)
        window.blit(self.flipped_pipe, self.top_pipe_rect)


class Score:
    def __init__(self,
                 zero_path,
                 one_path,
                 two_path,
                 three_path,
                 four_path,
                 five_path,
                 six_path,
                 seven_path,
                 eight_path,
                 nine_path):
        super().__init__()
        self.score = 0
        self.score_assets_dict = {
            "0": pygame.image.load(zero_path).convert_alpha(),
            "1": pygame.image.load(one_path).convert_alpha(),
            "2": pygame.image.load(two_path).convert_alpha(),
            "3": pygame.image.load(three_path).convert_alpha(),
            "4": pygame.image.load(four_path).convert_alpha(),
            "5": pygame.image.load(five_path).convert_alpha(),
            "6": pygame.image.load(six_path).convert_alpha(),
            "7": pygame.image.load(seven_path).convert_alpha(),
            "8": pygame.image.load(eight_path).convert_alpha(),
            "9": pygame.image.load(nine_path).convert_alpha()
        }

    def update(self, pipe_group, bird):
        for pipe in pipe_group:
            if pipe.bird_passed:
                continue
            if pipe.check_bird_pass(bird):
                self.score += 1
                pipe.bird_passed = True
                # print(f"Score updated: {self.score}")

    def reset_score(self):
        self.score = 0

    def draw(self, window):
        score_str = str(self.score)
        score_width = 0
        for char in score_str:
            score_width += self.score_assets_dict[char].get_width()

        x = SCREEN_WIDTH//2 - score_width + 10

        for char in score_str:
            window.blit(self.score_assets_dict[char], (x, 20))
            x += self.score_assets_dict[char].get_width()


class GameState:
    def __init__(self):
        super().__init__()
        self.state = 'intro'
        self.swoosh_played = False
        self.dead_sound_played = False
        self.bird_flap = False
        self.running = True

        self.last_pipe_time = pygame.time.get_ticks()
        self.transition_start_time = 0

        self.fade_alpha = 0
        self.fade_direction = 1
        self.transition_start_time = pygame.time.get_ticks()

    def intro(self, bird, background, floor):
        # intro event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                bird.intro = False
                self.state = 'transition'  # Set state to transition instead of main_game
                self.transition_start_time = pygame.time.get_ticks()  # Record the time when transition starts

                # play swoosh once
                if not self.swoosh_played:
                    bird.swoosh_sound_play()
                    self.swoosh_played = True

        # draw intro elements
        background.update_blink()
        background.draw()
        background.draw_intro()

        floor.update()
        floor.draw(background.window)

        bird.animate_bird()
        bird.draw(background.window)

        pygame.display.flip()

    def transition(self, bird, background):
        # Calculate the fade duration
        current_time = pygame.time.get_ticks()

        # Create a black surface for fading
        fade_surface = pygame.Surface((background.window.get_width(), background.window.get_height()))
        fade_surface.fill((0, 0, 0))  # Black color

        # Adjust the alpha value to create the fade effect
        fade_speed = 255 / (FADE_DURATION / 2)  # Speed of fading
        self.fade_alpha += self.fade_direction * fade_speed

        # Limit alpha values
        self.fade_alpha = max(0, min(255, self.fade_alpha))
        fade_surface.set_alpha(self.fade_alpha)

        # Draw the fade effect
        fade_surface.blit(fade_surface, (0, 0))
        background.window.blit(fade_surface, (0, 0))
        pygame.display.flip()

        # Change fade direction
        if self.fade_alpha >= 255:
            self.fade_direction = -1
            self.transition_start_time = current_time

        # Transition to main game once fully faded out
        elif self.fade_alpha <= 0 and self.fade_direction == -1:
            self.state = 'main_game'
            self.last_pipe_time = pygame.time.get_ticks()

            # Randomize background and bird color
            background.current_bg = random.choice(background.window_surf)
            bird.current_color = random.choice(list(bird.bird_dict.keys()))
            bird.bird_images = bird.bird_dict[bird.current_color]
            bird.bird_image = bird.bird_images[bird.current_idx]


    def main_game(self, bird, pipe_group, background, floor, score):
        # get current time
        current_time = pygame.time.get_ticks()

        # Spawn pipes
        if current_time - self.last_pipe_time > INTERVAL:
            new_pipe = Pipe(
                background,
                floor,
                "assets/flappy-bird-assets/sprites/pipe-green.png",
                "assets/flappy-bird-assets/sprites/pipe-red.png"
            )
            pipe_group.add(new_pipe)
            self.last_pipe_time = current_time

        # main game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                bird.sound_play()
                bird.flap()

        # Check collisions
        if not bird.game_over:
            for pipe in pipe_group:
                if (bird.bird_rect.colliderect(pipe.pipe_rect) or
                        bird.bird_rect.colliderect(pipe.top_pipe_rect) or
                        bird.bird_rect.colliderect(floor.floor_rect1) or
                        bird.bird_rect.colliderect(floor.floor_rect2)):
                    bird.game_over = True
                    if not self.dead_sound_played:
                        bird.hit_sound_play()
                        bird.dead_sound_play()
                        self.dead_sound_played = True
                    self.state = 'game_over'

            # Update score
            score.update(pipe_group, bird)

            # draw
            background.draw()
            pipe_group.update(game_over=False)
            for pipe in pipe_group:
                pipe.draw(background.window)

            floor.update()
            floor.draw(background.window)
            bird.update()
            bird.draw(background.window)
            score.draw(background.window)

        pygame.display.flip()

    def game_over(self, bird, pipe_group, background, floor, score):
        # game over events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reset the game state
                self.state = 'intro'
                self.dead_sound_played = False
                self.swoosh_played = False

                # Reset the bird
                bird.intro = True
                bird.game_over = False
                bird.bird_rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
                bird.velocity_y = 0
                bird.angle = 0
                bird.current_idx = 0
                bird.bird_image = bird.bird_images[bird.current_idx]

                # clear pipe
                pipe_group.empty()

                # reset score
                score.reset_score()

                # Reset transition effect
                self.fade_alpha = 0
                self.fade_direction = 1
                self.transition_start_time = pygame.time.get_ticks()

        # draw
        background.update_blink()
        background.draw()

        pipe_group.update(game_over=True)
        pipe_list = list(pipe_group)
        for i in range(min(2, len(pipe_list))):
            pipe_list[i].draw(background.window)

        background.draw_game_over()
        floor.draw(background.window)
        bird.update()
        bird.draw(background.window)
        score.draw(background.window)
        pygame.display.flip()

    def run(self, bird, pipe_group, background, floor, score):
        if self.state == 'intro':
            self.intro(bird, background, floor)
        elif self.state == 'transition':
            self.transition(bird, background)
        elif self.state == 'main_game':
            self.main_game(bird, pipe_group, background, floor, score)
        elif self.state == 'game_over':
            self.game_over(bird, pipe_group, background, floor, score)
