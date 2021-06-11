import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import re
import os
import sys

# turns pgn format into a more useful format for our calculations (.csv)
# resulting csv = |moves|outcome|

def main(args:list):
    prepreprocess(str(args[0]))

# preprocess all pgn files in path
def prepreprocess(path:str):
    start = time.time()
    pgns = get_files(path)
    print("preprocessing",len(pgns),"files:")
    for pgn in pgns:
        print("\t",pgn)
    # process every pgn file
    out_names = [path+"/0-999GAMES.csv",path+"/1000-1499GAMES.csv", path+"/1500-1999GAMES.csv", path+"/2000+GAMES.csv"]
    out_names = open_all(out_names)
    for out_name in out_names:
        add_header(out_name)
    for pgn in pgns:
        p = open(pgn, "r")
        preprocess(p, out_names) # process the file
        print("completed",pgn,"took",time.time()-start,"seconds.")
    end = time.time() - start
    print("Done. Took",end,"seconds.")

# writes the headers for the csvs
def add_header(out_name):
    out_name.write("moves,result\n")
# opens all the files and returns a list of file objects instead of strings
def open_all(out_names:list):
    files = []
    for name in out_names:
        files.append(open(name, "a"))
    return files

# returns a list of database names from root/directory
def get_files(path:str):
    databases = []
    for root, directories, files in os.walk(path, topdown=False):
	    for name in files:
		    if ( ".pgn" in name) and ("bz2" not in name): databases.append(os.path.join(root, name))
	    for name in directories:
		    if ( ".pgn" in name) and ("bz2" not in name): databases.append(os.path.join(root, name))
    return databases

# do the processing line-by-line.
def preprocess(pgns, out_names:list):
    result = avg_elo = white_elo = 0 # 1 if white win, 0 if draw, 2 if black win
    for line in pgns:
        if line.startswith("[R"): #Result
            quote_val = match_quotes(line)
            result = get_result(quote_val)
        elif line.startswith("[WhiteE"): #WhiteElo
            quote_val = match_quotes(line)
            white_elo = elo_to_int(quote_val)
        elif line.startswith("[BlackE"): #BlackElo
            quote_val = match_quotes(line)
            black_elo = elo_to_int(quote_val)
            # we can assume white's elo is already known because of the PGN format
            avg_elo = get_avg_elo(white_elo, black_elo)
        elif line.startswith("1."): # Moves
            moves = line[:-5].strip()
            #print(moves)
            store_game(moves, result, avg_elo, out_names)

# store games in different files depending on array brackets
def store_game(moves:str, result:int, avg_elo:int, out_names:list):
    if avg_elo < 1000:
        out_names[0].write(str(moves)+","+str(result)+"\n")
    elif avg_elo < 1500:
        out_names[1].write(str(moves)+","+str(result)+"\n")
    elif avg_elo < 2000:
        out_names[2].write(str(moves)+","+str(result)+"\n")
    else:
        out_names[3].write(str(moves)+","+str(result)+"\n")

# clean up files.
def clean_up(open_files:list):
    for file in open_files:
        file.close()

# gets the average elo between two values. Ignored bad elo values.
# returns an int.
def get_avg_elo(elo1:int, elo2:int):
    # check for and ignore bad elo values
    if (elo1 == 0):
        return elo2
    if (elo2 == 0):
        return elo1
    return np.divide(np.add(elo1, elo2), 2)

# cleans up the elo value. returns an int.
# Who decided it was a good idea to include the "?" for unsure elos in the pgn?
def elo_to_int(elo:str):
    elo = strip_questionmark(elo)
    if elo == '':
        return 0
    else:
        return int(elo)

# strip the questionmark out of elos.
# returns the new string
def strip_questionmark(quote_val):
    return quote_val.replace("?","")

# turns results into integers.
# returns an int
def get_result(quote_val:str):
    if quote_val.startswith("1/"): #draw
        return 0
    elif quote_val.startswith("1"): #white win
        return 1
    else: #black win
        return 2

# helpful regex for line processing
def match_quotes(line:str):
    return re.search("\"(.)*\"", line).group(0)[1:-1]

# can call this from the commandline with preprocess.py <path-to-databases-directory>
# but processing will probably call this too.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USEAGE: python preprocess.py <path-to-databases-directory>")
    else:
        main(sys.argv[1:])
