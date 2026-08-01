import os
import random
import time
import io
# Trick Pygame into running without a physical monitor screen
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from flask import Flask, Response

app = Flask(__name__)

# Initialize Pygame and virtual screen canvas
pygame.init()
WIDTH, HEIGHT = 300, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors and Game Variables
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (242, 85, 96)
BLUE = (85, 150, 242)

board = [""] * 9
current_player = "X"
game_over = False

def draw_board():
    screen.fill(WHITE)
    # Draw Grid Lines
    pygame.draw.line(screen, BLACK, (100, 0), (100, 300), 4)
    pygame.draw.line(screen, BLACK, (200, 0), (200, 300), 4)
    pygame.draw.line(screen, BLACK, (0, 100), (300, 100), 4)
    pygame.draw.line(screen, BLACK, (0, 200), (300, 200), 4)
    
    # Draw X and O elements
    font = pygame.font.SysFont(None, 80)
    for i, mark in enumerate(board):
        if mark == "": continue
        row, col = i // 3, i % 3
        text = font.render(mark, True, RED if mark == "X" else BLUE)
        screen.blit(text, (col * 100 + 25, row * 100 + 15))
    
    pygame.display.flip()

def check_winner():
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]] != "":
            return True
    return False

def generate_frames():
    global current_player, game_over, board
    while True:
        # Auto-play game logic loop
        if not game_over:
            empty_cells = [i for i, cell in enumerate(board) if cell == ""]
            if empty_cells:
                move = random.choice(empty_cells)
                board[move] = current_player
                if check_winner() or "" not in board:
                    game_over = True
                current_player = "O" if current_player == "X" else "X"
            else:
                game_over = True
        else:
            time.sleep(2) # Pause briefly at game over screen
            board = [""] * 9 # Reset the game board
            current_player = "X"
            game_over = False

        draw_board()
        
        # Convert Pygame visual layout to a streamable JPEG image format
        img_data = pygame.image.tostring(screen, "RGB")
        import PIL.Image as Image
        img = Image.frombytes("RGB", (WIDTH, HEIGHT), img_data)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        frame = buffer.getvalue()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.6) # Play speed delay (adjust to make it run faster/slower)

@app.route('/')
def index():
    # Returns an raw HTML image tag bound to our real-time video generation generator
    return '<body style="background:#111; display:flex; justify-content:center; align-items:center; height:100vh;"><img src="/video_feed" style="border:5px solid white; border-radius:10px;"></body>'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
