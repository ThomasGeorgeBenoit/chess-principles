import chess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import re
import sys
import os

# extracts features and build csvs from them.
# output format: when_castled,num_center_squares_controlled,material_difference,num_unique_pieces_moved,win

# main program entry
def main(args:list):
    start = time.time()
    path = str(args[0])
    csvs = get_csvs(path)
    print("processing",len(csvs),"csvs:")
    for csv in csvs:
        print("\t",csv)
    iterate_csvs(csvs, path)
    end = time.time() - start
    print("Done. Took",end,"seconds.")

# opens all the files and returns a list of file objects instead of strings
def open_all(out_names:list):
    files = []
    for name in out_names:
        #f = open(name, "w")
        #f.close()
        f = open(name, "a")
        files.append(f)

    return files

def process(csv, data, out):
    # data: the data in CSV:
    # |moves|result|
    for i, game in data.iterrows():
        result = int(game[1])
        moves = str(game[0])
        when_castled_w, when_castled_b,\
        num_center_squares_controlled_w, num_center_squares_controlled_b,\
        material_difference,\
        extract_num_unique_pieces_moved_w, extract_num_unique_pieces_moved_b\
        = extract_features(moves, result)
        save_game(out, result,  when_castled_w, when_castled_b,\
            num_center_squares_controlled_w, num_center_squares_controlled_b,\
            material_difference,\
            extract_num_unique_pieces_moved_w, extract_num_unique_pieces_moved_b)

# extract the features we want.
def extract_features(moves:str, result:int):
    if '%' in moves:
        return -1, -1, -1, -1, -1, -1, -1
    moves_ar = get_moves_ar(moves)
    if moves_ar[0] == "bad game":
        return -1, -1, -1, -1, -1, -1, -1
    # extract the features
    # (this takes the vast majority of runtime)
    num_unique_pieces_moved_w = extract_num_unique_pieces_moved_w(moves_ar,7)
    num_unique_pieces_moved_b = extract_num_unique_pieces_moved_b(moves_ar,7)
    when_castled_w = extract_when_castled_w(moves_ar)
    when_castled_b = extract_when_castled_b(moves_ar)
    material_difference = extract_material_difference(moves_ar, 4) # material difference k moves in.
    num_center_squares_controlled_w, num_center_squares_controlled_b = extract_num_center_squares_controlled(moves_ar, 5)
    # return the features
    return when_castled_w, when_castled_b,\
        num_center_squares_controlled_w, num_center_squares_controlled_b,\
        material_difference,\
        num_unique_pieces_moved_w, num_unique_pieces_moved_b

# save the game to out in a csv format
# when_castled,num_center_squares_controlled,material_difference,num_unique_pieces_moved,win
# outputs 2 lines, one for white's features and one for black's features
def save_game(out, result,  when_castled_w, when_castled_b,\
        num_center_squares_controlled_w, num_center_squares_controlled_b,\
        material_difference,\
        num_unique_pieces_moved_w, num_unique_pieces_moved_b):
    # win corresponds to if a COLOR wins, so we have to change this depending on which color is saved
    win = 0
    if int(result) == 1:
        win = 1
    white_print = str(when_castled_w)+","+str(num_center_squares_controlled_w)+","+str(material_difference)+","+str(num_unique_pieces_moved_w)+","+str(win)+"\n"
    out.write(white_print)
    win = 0
    if int(result) == 2:
        win = 1
    black_print = str(when_castled_b)+","+str(num_center_squares_controlled_b)+","+str(material_difference)+","+str(num_unique_pieces_moved_b)+","+str(win)+"\n"
    out.write(black_print)

#returns the number of unique pieces moved by white in k turns
def extract_num_unique_pieces_moved_w(moves_ar,k):
    # number of unique pieces
    num_unique = 0
    # list of starting points of pieces that have moved in row 1
    row_1 = []
    # list of starting points of pieces that have moved in row 2
    row_2 = []
    # simulate the board
    board = chess.Board()
    # if there are less than k moves, use moves # instead of k
    length = 0
    if len(moves_ar) < k:
        length = len(moves_ar)
    else:
        length = k
    for i in range(length):
        # assigns starting position of piece that moved to start_pos 
        # ex: input move "e4" would return "e2" i.e. pawn goes from e2 to e4
        if moves_ar[i][0][0] == 'O':
            num_unique += 2
            row_1.append("e1")
            board.push_san(moves_ar[i][0])
            if moves_ar[i][0] == "O-O":
                row_1.append("h1")
            else:
                row_1.append("a1")
        else:
            try:
                start_pos = board.push_san(moves_ar[i][0]).uci()[:2]
            except:
                pass
            if start_pos[1] == '1':
                if start_pos not in row_1:
                    num_unique += 1
                    row_1.append(start_pos)
            elif start_pos[1] == '2':
                if start_pos not in row_2:
                    num_unique += 1
                    row_2.append(start_pos)
        if len(moves_ar[i]) == 2:
            board.push_san(moves_ar[i][1])
    return num_unique

# returns the number of unique pieces moved by black in k turns
def extract_num_unique_pieces_moved_b(moves_ar,k):
    # number of unique pieces
    num_unique = 0
    # list of starting points of pieces that have moved in row 8
    row_8 = []
    # list of starting points of pieces that have moved in row 7
    row_7 = []
    # simulate the board
    board = chess.Board()
    # if there are less than k moves, use moves # instead of k
    length = 0
    if len(moves_ar) < k:
        length = len(moves_ar)
    else:
        length = k
    # -1 so that we can deal with the last data point later since it might not have
    # a move for black
    for i in range(length - 1):
        board.push_san(moves_ar[i][0])

        if moves_ar[i][1][0] == 'O':
            num_unique += 2
            row_8.append("e8")
            board.push_san(moves_ar[i][1])
            if moves_ar[i][0] == "O-O":
                row_8.append("h8")
            else:
                row_8.append("a8")
        else:
            # assigns starting position of piece that moved to start_pos
            # ex: input move "e4" would return "e2" i.e. pawn goes from e2 to e4a
            start_pos = board.push_san(moves_ar[i][1]).uci()[:2]
            if start_pos[1] == '8':
                if start_pos not in row_8:
                    num_unique += 1
                    row_8.append(start_pos)

            elif start_pos[1] == '7':
                if start_pos not in row_7:
                    num_unique += 1
                    row_7.append(start_pos)
    # checking just the last data point since it could only have white's move and not blacks
    board.push_san(moves_ar[length-1][0])
    if len(moves_ar[length-1]) == 2:
        if moves_ar[length-1][1][0] == 'O':
            num_unique += 2
            row_8.append("e8")
            board.push_san(moves_ar[length-1][1])
            if moves_ar[i][0] == "O-O":
                row_8.append("h8")
            else:
                row_8.append("a8")
        else:        
            start_pos = board.push_san(moves_ar[length-1][1]).uci()[:2]
            if start_pos[1] == '8':
                if start_pos not in row_8:
                    num_unique += 1
                    row_8.append(start_pos)

            elif start_pos[1] == '7':
                if start_pos not in row_7:
                    num_unique += 1
                    row_7.append(start_pos)
    return num_unique

# extracts and returns the material count k-moves into the game
# 0 means even material, negative num means black is up, positive num means white is up
def extract_material_difference(moves_ar, k):
    # simulate the board
    board = sim_board(moves_ar, k)
    # Change the board into just a string of pieces.
    # We don't care about piece positions. just the peice count.
    # capital letters = white, lower-case = black.
    board_str = str(board).replace(".","").replace("\n","").replace(" ","")
    # even though this ^ looks messy, it actually speeds up the later char checking by a fair bit!
    material = 0 # 0 means even material, negative means black is up, positive means white is up
    for c in board_str:
        if c.lower() != c: # means we are looking at white, so just check for white pieces
            if c == 'R':
                material += 5
            elif c == 'N' or c == 'B':
                material += 3
            elif c == 'Q':
                material += 9
            elif c == 'P':
                material += 1
        else: #just check for black pieces  
            if c == 'r':
                material -= 5
            elif c == 'n' or c == 'b':
                material -= 3
            elif c == 'q':
                material -= 9
            elif c == 'p':
                material -= 1
    return material


# (counts x-rays, ex: unmoved queens count towards center count)
def extract_num_center_squares_controlled(moves_ar, k):
    # simulate the board
    board = sim_board(moves_ar, k)
    board_str = str(board).replace(' ', '').replace('\n', '')
    w = 0
    b = 0
    # pieces in positions that control the center: (inclusive)
    # board format:
    # 0  1  2  3  4  5  6  7
    # 8  9  10 11 12 13 14 15
    # ...
    # pawns: 10-13, 19-20, 35-36, 42-45
    # horsies: 10-13, 17-22, 25-26, 29-30, 33-34, 37-38, 41-46, 50-53
    # horsies again: 18, 21, 42, 45 (knights on these squares control two center squares!)
    # bishops: 9, 14, 18, 21, 42, 45, 49, 54
    # queens: 3, 10-12, 17, 19, 21, 24, 30-32, 38-39, 41, 43, 45, 51-52, 59
    # suprisingly, this is actually quite efficient, albeit tedious
    pawns = board_str[10:14]+board_str[19:21]+board_str[35:37]+board_str[42:46]
    horsies = board_str[10:14]+board_str[17:23]+board_str[25:27]+board_str[29:31]\
        +board_str[33:35]+board_str[37:39]+board_str[42:46]+board_str[50:54]
    horsies += board_str[18]+board_str[21]+board_str[42]+board_str[45]
    bishops = board_str[9]+board_str[14]+board_str[18]+board_str[21]\
        +board_str[42]+board_str[45]+board_str[49]+board_str[54]
    queens = board_str[3]+board_str[10-12]+board_str[17]+board_str[19]+board_str[21]\
        +board_str[24]+board_str[30:33]+board_str[38:40]+board_str[41]+board_str[43]\
        +board_str[45]+board_str[51:53]+board_str[59]
    w = pawns.count('P') + horsies.count('K') + bishops.count('B') + queens.count('Q')
    b = pawns.count('p') + horsies.count('k') + bishops.count('b') + queens.count('q')
    return w, b

# extracts on what move white castled
def extract_when_castled_w(moves_ar:list):
    i = 1
    for move in moves_ar:
        if len(move) > 0:
            if "O-O" in move[0]:
                return i
        i+=1
    return i # player never castled. just put the number of moves in the game.

# extracts on what move black castled
def extract_when_castled_b(moves_ar:list):
    i = 1
    for move in moves_ar:
        if len(move) > 0:
            # for black, we need to check a move was even played!
            try:
                if "O-O" in move[1]:
                    return i
            except:
                pass
        i+=1
    return i

# simulate k-moves and return a python-chess board representing this position
def sim_board(moves_ar, k):
    board = chess.Board()
    for i in range(k):
        try: # no error on short games or games with early checkmate or resignation
            board.push_san(moves_ar[i][0])
            board.push_san(moves_ar[i][1])
        except:
            pass
    return board

# takes a moves str and returns an array where each index = one full turn (2 moves)
def get_moves_ar(moves:str):
    m = []
    moves_ = moves.split(".")
    for move in moves_[1:-1]:
        move = move.strip()
        move = move.split(" ")[:-1]
        m.append(move)
    last_move = moves_[-1].strip().split(" ")
    # we need to check if white stalemated.
    if "1/2" not in last_move:
        m.append(last_move)
    if len(m) == 0:
        return ["bad game"]
    return m

# strips the csv of their GAMES tag.
def strip_csv(csv:str):
    return csv.split("GAMES")[0]

# get all the relevant csvs from the databases directory
def get_csvs(path:str):
    csvs = []
    for root, directories, files in os.walk(path, topdown=False):
	    for name in files:
		    if (".csv" in name) and ("FEATURES" not in name): csvs.append(os.path.join(root, name))
	    for name in directories:
		    if (".csv" in name) and ("FEATURES" not in name): csvs.append(os.path.join(root, name))
    return csvs

# iterate through all the csvs. calls the processing function.
def iterate_csvs(csvs:list, path:str):
    for csv in csvs:
        data = pd.read_csv(csv)
        print("analyzing",csv)
        rating_range = get_range(csv)
        out_path = path+rating_range+"FEATURES.csv"
        out = open(out_path, "a")
        print("writing to "+out_path)
        out.write("when_castled,num_center_squares_controlled,material_difference,num_unique_pieces_moved,win\n")
        process(csv, data, out)

# extract the rating range from a csv string
def get_range(csv:str):
    if "1000" in csv:
        return "1000-1499"
    elif "1500" in csv:
        return "1500-1999"
    elif "2000" in csv:
        return "2000+"
    elif "999" in csv:
        return "0-999"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USEAGE: python process.py <path-to-csvs-directory>")
        print("NOTE: must be run with python2 because of the python-chess library")
    else:
        main(sys.argv[1:])
