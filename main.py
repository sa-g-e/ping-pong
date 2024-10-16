import pygame
import sys
import random
import logging

# Set up logging
logging.basicConfig(filename='pong_game.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FONT = pygame.font.Font(None, 36)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Ping")

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 5

# Ball settings
BALL_SIZE = 20
INITIAL_BALL_SPEED = 3

# Score settings
MAX_SCORE = 5
WINNING_MARGIN = 2  


class Paddle:
    """Class to represent the paddle."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        logging.info(f"Paddle created at position: {self.rect}")

    def move(self, up, down):
        """Move the paddle based on user input."""
        original_y = self.rect.y
        if up and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
            logging.debug(f"Paddle moved up from {original_y} to {self.rect.y}")
        if down and self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED
            logging.debug(f"Paddle moved down from {original_y} to {self.rect.y}")
        
        # Assert paddle stays within screen boundaries
        assert self.rect.top >= 0, f"Paddle moved beyond top boundary: {self.rect.top}"
        assert self.rect.bottom <= HEIGHT, f"Paddle moved beyond bottom boundary: {self.rect.bottom}"

    def draw(self):
        """Draw the paddle on the screen."""
        pygame.draw.rect(screen, BLACK, self.rect)


class Ball:
    """Class to represent the ball."""
    def __init__(self):
        self.reset()
        logging.info("Ball initialized and reset.")

    def move(self):
        """Update the ball's position based on its speed."""
        original_x, original_y = self.rect.x, self.rect.y
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        logging.debug(f"Ball moved from ({original_x}, {original_y}) to ({self.rect.x}, {self.rect.y})")
        
        # Assert ball stays within horizontal boundaries (before scoring)
        assert self.rect.left >= -BALL_SIZE, f"Ball moved too far left: {self.rect.left}"
        assert self.rect.right <= WIDTH + BALL_SIZE, f"Ball moved too far right: {self.rect.right}"
        assert self.rect.top >= -BALL_SIZE, f"Ball moved too far up: {self.rect.top}"
        assert self.rect.bottom <= HEIGHT + BALL_SIZE, f"Ball moved too far down: {self.rect.bottom}"

    def bounce(self, axis):
        """Bounce the ball off surfaces based on the axis."""
        if axis == 'x':
            self.speed_x *= -1
            logging.info(f"Ball bounced on X-axis. New speed_x: {self.speed_x}")
            self.increase_speed()  # Increase speed on paddle hit
        elif axis == 'y':
            self.speed_y *= -1
            logging.info(f"Ball bounced on Y-axis. New speed_y: {self.speed_y}")

    def increase_speed(self):
        """Increase the ball's speed."""
        self.speed_x *= 1.08  # Increase speed by 8%
        self.speed_y *= 1.08
        logging.debug(f"Ball speed increased to ({self.speed_x}, {self.speed_y})")

    def reset(self):
        """Reset the ball to the center with a random direction.""" 
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.speed_x = INITIAL_BALL_SPEED * random.choice((1, -1))
        self.speed_y = INITIAL_BALL_SPEED * random.choice((1, -1))
        logging.info(f"Ball reset to center with speed ({self.speed_x}, {self.speed_y})")

    def draw(self):
        """Draw the ball on the screen.""" 
        pygame.draw.ellipse(screen, BLACK, self.rect)


class Button:
    """Create buttons for the menu."""
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self):
        """Draw the button and its text on the screen.""" 
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Handle button events.""" 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                logging.info(f"Button '{self.text}' clicked.")
                self.action()


class Game:
    """Main Class for game manager."""
    def __init__(self):
        self.left_paddle = Paddle(50, (HEIGHT - PADDLE_HEIGHT) // 2)
        self.right_paddle = Paddle(WIDTH - 50 - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT) // 2)
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.high_scores = []
        self.state = "menu"
        self.create_menu()
        self.load_high_scores()  
        logging.info("Game initialized")

    def create_menu(self):
        """Create the main menu buttons."""
        button_width, button_height = 200, 50
        start_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 - button_height, button_width, button_height, "Start", GRAY, WHITE, self.start_game)
        exit_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 + button_height, button_width, button_height, "Exit", GRAY, WHITE, sys.exit)
        self.menu_buttons = [start_button, exit_button]

    def start_game(self):
        """Start a new game session.""" 
        self.state = "game"
        self.left_score = 0
        self.right_score = 0
        self.ball.reset()
        logging.info("Game started")

    def handle_collision(self):
        """Check for collisions with walls and paddles.""" 
        if self.ball.rect.top <= 0 or self.ball.rect.bottom >= HEIGHT:
            self.ball.bounce('y')
            logging.info(f"Ball bounced on top/bottom: {self.ball.rect}")
        
        if self.ball.rect.colliderect(self.left_paddle.rect) or self.ball.rect.colliderect(self.right_paddle.rect):
            self.ball.bounce('x')
            logging.info(f"Ball bounced on paddle: {self.ball.rect}")
        
        if self.ball.rect.left <= 0:  # Right player scores
            self.right_score += 1
            logging.info(f"Right player scored. Score: {self.right_score}")
            self.ball.reset()  # Reset the ball position and speed
        elif self.ball.rect.right >= WIDTH:  # Left player scores
            self.left_score += 1
            logging.info(f"Left player scored. Score: {self.left_score}")
            self.ball.reset()  # Reset the ball position and speed

    def draw_scores(self):
        """Draw the current scores on the screen.""" 
        left_score_text = FONT.render(str(self.left_score), True, BLACK)
        right_score_text = FONT.render(str(self.right_score), True, BLACK)
        # Position scores appropriately
        screen.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))  
        screen.blit(right_score_text, (3 * WIDTH // 4 - right_score_text.get_width() // 2, 20))  

    def get_player_initials(self):
        """Get player initials for high score entry.""" 
        initials = ""
        input_active = True
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                        logging.info(f"Player entered initials: {initials}")
                    elif event.key == pygame.K_BACKSPACE:
                        initials = initials[:-1]
                        logging.debug(f"Player deleted a character. Current initials: {initials}")
                    elif len(initials) < 3 and event.unicode.isalpha():
                        initials += event.unicode.upper()
                        logging.debug(f"Player added a character. Current initials: {initials}")
                    else:
                        logging.warning(f"Invalid input for initials: '{event.unicode}'")
            
            screen.fill(WHITE)
            prompt = FONT.render("Enter your initials (3 letters):", True, BLACK)
            initials_text = FONT.render(initials, True, BLACK)
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(initials_text, (WIDTH // 2 - initials_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()
        
        return initials

    def update_high_scores(self, winner_score):
        """Update high scores list with new entries.""" 
        initials = self.get_player_initials()
        if initials:  # Ensure initials are not empty
            self.high_scores.append((initials, winner_score))    
            self.save_high_scores()
            logging.info(f"High scores updated. New entry: {initials} - {winner_score}")
        else:
            logging.warning("No initials entered. High score not updated.")

    def display_high_scores(self):
        """Display top 3 high scores on main menu.""" 
        for i, (initials, score) in enumerate(self.high_scores[:3]):
            score_text = FONT.render(f"{i + 1}. {initials}: {score}", True, BLACK)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 100 + i * 40))

    def save_high_scores(self):
        """Save high scores to a file.""" 
        try:
            with open("high_scores.txt", "w") as f:
                for initials, score in self.high_scores:
                    f.write(f"{initials},{score}\n")
            logging.info("High scores saved successfully")
        except IOError as e:
            logging.error(f"Error saving high scores: {e}")

    def load_high_scores(self):
        """Load high scores from a file."""
        try:
            with open("high_scores.txt", "r") as f:
                # Read and parse the high scores
                self.high_scores = [line.strip().split(",") for line in f if line.strip()]
                self.high_scores = [(initials, int(score)) for initials, score in self.high_scores]
                
                # Sort high scores by score in descending order
                self.high_scores.sort(key=lambda x: x[1], reverse=True)

                logging.info(f"High scores loaded successfully: {self.high_scores}")
        except FileNotFoundError:
            logging.warning("High scores file not found. Starting with empty high scores.")
            self.high_scores = []
        except IOError as e:
            logging.error(f"Error loading high scores: {e}")
        except ValueError as e:
            logging.error(f"Error processing high scores: {e}")
            self.high_scores = []

    def display_instructions(self):
        """Display instructions on the main menu."""
        instructions = [
            "Controls:",
            "Left Paddle: W (up), S (down)",
            "Right Paddle: UP (up), DOWN (down)",
            "",
            "Win Condition:",
            f"First player to score {MAX_SCORE} points wins!",
            f"Player must win by a margin of {WINNING_MARGIN} points."
        ]
        for i, line in enumerate(instructions):
            instruction_text = FONT.render(line, True, BLACK)
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 100 + i * 30))

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.info("Game exited by user.")
                    pygame.quit()
                    sys.exit()

                # Handle button events in the menu state
                if self.state == "menu":
                    for button in self.menu_buttons:
                        button.handle_event(event)

                # Handle key presses in the game state
                if self.state == "game":
                    if event.type == pygame.KEYDOWN:
                        if event.key not in [pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN]:
                            logging.warning(f"Unexpected key pressed: {pygame.key.name(event.key)}")
            
            # Game logic
            if self.state == "game":
                keys = pygame.key.get_pressed()
                self.left_paddle.move(keys[pygame.K_w], keys[pygame.K_s])  # W for up, S for down
                self.right_paddle.move(keys[pygame.K_UP], keys[pygame.K_DOWN])  # Arrow keys

                self.ball.move()
                self.handle_collision()

                # Check for winning conditions
                if (self.left_score >= MAX_SCORE and 
                    (self.left_score - self.right_score) >= WINNING_MARGIN):
                    logging.info("Left player has won the game.")
                    self.update_high_scores(self.left_score)
                    self.state = "menu"  # Return to menu after the left player wins
                elif (self.right_score >= MAX_SCORE and 
                      (self.right_score - self.left_score) >= WINNING_MARGIN):
                    logging.info("Right player has won the game.")
                    self.update_high_scores(self.right_score)
                    self.state = "menu"  # Return to menu after the right player wins

            # Rendering
            screen.fill(WHITE)  # Clear screen

            # Draw title
            title_text = FONT.render("Pong Game", True, BLACK)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

            # Draw elements based on the game state
            if self.state == "game":
                self.left_paddle.draw()
                self.right_paddle.draw()
                self.ball.draw()
                self.draw_scores()
            else:  # In menu state
                for button in self.menu_buttons:
                    button.draw()
                self.display_high_scores()
                self.display_instructions()  

            pygame.display.flip()  # Update the full display
            clock.tick(60)  # Maintain 60 FPS


# Run the game
if __name__ == "__main__":
    try:
        game_instance = Game()
        game_instance.run()
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
        pygame.quit()
        sys.exit()
