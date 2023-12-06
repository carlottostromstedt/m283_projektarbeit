from load_db import *
from matcher import *

board = "board3.png"
ids = match_images_to_board(board)

for id in ids:
   find_card(id)