import pygame
import sys
import random
from collections import deque, defaultdict


# Constants
GRID_SIZE = 4
TILE_SIZE = 120
TILE_MARGIN = 10
HEADER_HEIGHT = 80

# Calculate the width
width = (GRID_SIZE * TILE_SIZE) + ((GRID_SIZE + 1) * TILE_MARGIN) + 400

# Calculate the height
height = (GRID_SIZE * TILE_SIZE) + ((GRID_SIZE + 1) * TILE_MARGIN) + HEADER_HEIGHT

# Set the new window size
WINDOW_SIZE = (width, height)

# Set the font size
FONT_SIZE = TILE_SIZE // 4  # or TILE_SIZE // 3

print("WINDOW_SIZE:", WINDOW_SIZE)
print("FONT_SIZE:", FONT_SIZE)
# Colors
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}
TEXT_COLOR = (119, 110, 101)
BUTTON_COLOR = (119, 110, 101)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("2048")
font = pygame.font.Font(None, FONT_SIZE)
button_font = pygame.font.Font(None, 36)

# Initialize Music
pygame.mixer.init()

def play_background_music():
    pygame.mixer.music.load('C:\\Users\\DELL\\Downloads\\background_music.mp3')
    pygame.mixer.music.play(-1)  # Play music continuously

def show_intro_video(): 
     pass

def draw_start_screen():
    screen.fill(BACKGROUND_COLOR)
    start_button = pygame.Rect(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 50, 200, 100)
    pygame.draw.rect(screen, BUTTON_COLOR, start_button)
    start_text = button_font.render('Start Game', True, BUTTON_TEXT_COLOR)
    screen.blit(start_text, start_text.get_rect(center=start_button.center))
    pygame.display.flip()
    return start_button

def new_tile():
    return 4 if random.random() > 0.9 else 2

def place_random_tile(board):
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if not empty_tiles:
        return
    r, c = random.choice(empty_tiles)
    board[r][c] = new_tile()

def initialize_board():
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    place_random_tile(board)
    place_random_tile(board)
    return board

def draw_board(board, score, comment):
    screen.fill(BACKGROUND_COLOR)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = board[r][c]
            color = TILE_COLORS.get(value, (237, 204, 97))
            rect = pygame.Rect(c * TILE_SIZE + (c + 1) * TILE_MARGIN,
                               r * TILE_SIZE + (r + 1) * TILE_MARGIN + HEADER_HEIGHT,
                               TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            if value != 0:
                text = font.render(str(value), True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
    # Draw Score
    score_text = button_font.render(f'Score: {score}', True, TEXT_COLOR)
    screen.blit(score_text, (20, 10))
    # Draw Comment
    comment_text = button_font.render(f'Comment: {comment}', True, TEXT_COLOR)
    screen.blit(comment_text, (20, 50))
    pygame.display.flip()

def move_left(board):
    new_board = []
    score = 0
    for row in board:
        tight = [num for num in row if num != 0]
        merged = []
        skip = False
        for j in range(len(tight)):
            if skip:
                skip = False
                continue
            if j != len(tight) - 1 and tight[j] == tight[j + 1]:
                merged.append(tight[j] * 2)
                score += tight[j] * 2
                skip = True
            else:
                merged.append(tight[j])
        merged += [0] * (GRID_SIZE - len(merged))
        new_board.append(merged)
    return new_board, score

def rotate_clockwise(board):
    return [[board[GRID_SIZE - c - 1][r] for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

def move_board(board, direction):
    if direction == 'left':
        return move_left(board)
    if direction == 'right':
        rotated = rotate_clockwise(rotate_clockwise(board))
        moved, score = move_left(rotated)
        return rotate_clockwise(rotate_clockwise(moved)), score
    if direction == 'up':
        rotated = rotate_clockwise(rotate_clockwise(rotate_clockwise(board)))
        moved, score = move_left(rotated)
        return rotate_clockwise(moved), score
    if direction == 'down':
        rotated = rotate_clockwise(board)
        moved, score = move_left(rotated)
        return rotate_clockwise(rotate_clockwise(rotate_clockwise(moved))), score

def has_move(board):
    if any(0 in row for row in board):
        return True
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if board[r][c] == board[r][c + 1]:
                return True
    for r in range(GRID_SIZE - 1):
        for c in range(GRID_SIZE):
            if board[r][c] == board[r + 1][c]:
                return True
    return False

def ai_move(board):
    directions = ['left', 'right', 'up', 'down']
    best_move = None
    best_score = -1
    for direction in directions:
        new_board, score = move_board(board, direction)
        if new_board != board and score > best_score:
            best_move = direction
            best_score = score
    return best_move

def draw_buttons():
    button_width = 140
    button_height = 50
    button_x = WINDOW_SIZE[0] - button_width - 20  # Right side positioning
    new_game_button = pygame.Rect(button_x, 20, button_width, button_height)
    quit_button = pygame.Rect(button_x, 80, button_width, button_height)
    ai_button = pygame.Rect(button_x, 140, button_width, button_height)
    undo_button = pygame.Rect(button_x, 200, button_width, button_height)
    
    pygame.draw.rect(screen, BUTTON_COLOR, new_game_button)
    pygame.draw.rect(screen, BUTTON_COLOR, quit_button)
    pygame.draw.rect(screen, BUTTON_COLOR, ai_button)
    pygame.draw.rect(screen, BUTTON_COLOR, undo_button)
    
    new_game_text = button_font.render('New Game', True, BUTTON_TEXT_COLOR)
    quit_text = button_font.render('Quit', True, BUTTON_TEXT_COLOR)
    ai_text = button_font.render('AI Move', True, BUTTON_TEXT_COLOR)
    undo_text = button_font.render('Undo', True, BUTTON_TEXT_COLOR)
    
    screen.blit(new_game_text, new_game_text.get_rect(center=new_game_button.center))
    screen.blit(quit_text, quit_text.get_rect(center=quit_button.center))
    screen.blit(ai_text, ai_text.get_rect(center=ai_button.center))
    screen.blit(undo_text, undo_text.get_rect(center=undo_button.center))

    return new_game_button, quit_button, ai_button, undo_button

def draw_game_over(blessings):
    screen.fill(BACKGROUND_COLOR)
    game_over_text = button_font.render('Game Over', True, BUTTON_TEXT_COLOR)
    screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_SIZE[0] // 2, 100)))
    
    for i, blessing in enumerate(blessings):
        blessing_text = button_font.render(blessing, True, TEXT_COLOR)
        screen.blit(blessing_text, (20, 150 + i * 25))

    congrats_text = font.render('Congratulations!', True, TEXT_COLOR)
    screen.blit(congrats_text, (WINDOW_SIZE[0] // 2 - 100, 750))
    pygame.display.flip()
    pygame.time.wait(5000)

def undo_move(stack, board, score):
    if stack:
        board, score = stack.pop()
    return board, score

# High Score Tracking (Using List)
high_scores = []

def update_high_scores(score):
    global high_scores
    high_scores.append(score)
    high_scores.sort(reverse=True)
    high_scores = high_scores[:5]  # Keep top 5 scores

def draw_high_scores():
    for i, high_score in enumerate(high_scores):
        score_text = button_font.render(f'High Score {i + 1}: {high_score}', True, TEXT_COLOR)
        screen.blit(score_text, (WINDOW_SIZE[0] - 300, 300 + i * 40))

# Power-Up Tiles (Using Dictionary)
power_ups = {
    'double_score': 'D',
    'extra_move': 'E'
}

def place_power_up_tile(board):
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if not empty_tiles:
        return
    r, c = random.choice(empty_tiles)
    board[r][c] = random.choice(list(power_ups.values()))

def handle_power_up(tile):
    if tile == 'D':
        return 'double_score'
    elif tile == 'E':
        return 'extra_move'
    return None

# Move History (Using Linked List)
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements

move_history = LinkedList()

def record_move(board, score):
    move_history.append((list(map(list, board)), score))

def show_move_history():
    history = move_history.display()
    for i, state in enumerate(history):
        print(f'Move {i}: Board - {state[0]}, Score - {state[1]}')

# Achievements (Using Set)
achievements = set()

def check_achievements(board, score):
    if any(2048 in row for row in board):
        achievements.add("2048 Tile Achieved")
    if score >= 10000:
        achievements.add("Score 10,000+")
    if len(achievements) > 0:
        print("Achievements Unlocked:", achievements)

# Leaderboard (Using Queue)
leaderboard = deque(maxlen=5)

def update_leaderboard(score):
    global leaderboard
    leaderboard.append(score)
    leaderboard = deque(sorted(leaderboard, reverse=True))

def show_leaderboard():
    for i, score in enumerate(leaderboard):
        print(f'Rank {i + 1}: {score}')

def main():
    play_background_music()
    
    # Show intro video
    show_intro_video()
    
    start_button = draw_start_screen()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    waiting = False

    board = initialize_board()
    score = 0
    comment = "Good luck!"
    draw_board(board, score, comment)
    new_game_button, quit_button, ai_button, undo_button = draw_buttons()

    move_stack = deque()  # Using deque as a stack for undo functionality

    running = True  # Variable to keep the main loop running
    while running:
        draw_buttons()  # Redraw buttons on each loop
        draw_high_scores()
        pygame.display.flip()  # Update display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Set running to False to exit the loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    board = initialize_board()
                    score = 0
                    comment = "New game started!"
                    draw_board(board, score, comment)
                    move_stack.clear()
                elif quit_button.collidepoint(event.pos):
                    running = False  # Set running to False to exit the loop
                elif ai_button.collidepoint(event.pos):
                    best_move = ai_move(board)
                    if best_move:
                        move_stack.append((list(map(list, board)), score))  # Push current state to stack
                        new_board, move_score = move_board(board, best_move)
                        if new_board != board:
                            board = new_board
                            score += move_score
                            place_random_tile(board)
                            comment = f"AI moved {best_move}"
                            draw_board(board, score, comment)
                            if not has_move(board):
                                blessings = ["Great Job!", "Well Done!", "Awesome!", "Keep Going!", "Fantastic!"]
                                draw_game_over(blessings)  # Add actual blessings here
                                update_high_scores(score)
                                update_leaderboard(score)
                elif undo_button.collidepoint(event.pos):
                    board, score = undo_move(move_stack, board, score)
                    comment = "Move undone"
                    draw_board(board, score, comment)
            if event.type == pygame.KEYDOWN:
                new_board, move_score = None, 0
                if event.key == pygame.K_LEFT:
                    new_board, move_score = move_board(board, 'left')
                    comment = "Moved left"
                elif event.key == pygame.K_RIGHT:
                    new_board, move_score = move_board(board, 'right')
                    comment = "Moved right"
                elif event.key == pygame.K_UP:
                    new_board, move_score = move_board(board, 'up')
                    comment = "Moved up"
                elif event.key == pygame.K_DOWN:
                    new_board, move_score = move_board(board, 'down')
                    comment = "Moved down"

                if new_board and new_board != board:
                    move_stack.append((list(map(list, board)), score))  # Push current state to stack
                    board = new_board
                    score += move_score

                    for r in range(GRID_SIZE):
                        for c in range(GRID_SIZE):
                            power_up = handle_power_up(board[r][c])
                            if power_up == 'double_score':
                                score *= 2
                            elif power_up == 'extra_move':
                                # Extra move logic (e.g., allow another move without placing a new tile)
                                pass

                    place_random_tile(board)
                    draw_board(board, score, comment)
                    record_move(board, score)
                    check_achievements(board, score)
                    if not has_move(board):
                        blessings = ["Great Job!", "Well Done!", "Awesome!", "Keep Going!", "Fantastic!"]
                        draw_game_over(blessings)
                        update_high_scores(score)
                        update_leaderboard(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
