import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import re
import sys
import os
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_classif
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

# extracts features and build csvs from them.
# writes and opens a figure of the results

# main program entry
# analyze all FEATURE csvs and 
def main(args:list):
    start = time.time()
    path = str(args[0])
    csvs = get_csvs(path)
    print("Analyzing",len(csvs),"csvs:")
    for csv in csvs:
        print("\t",csv)
    importances = iterate_csvs(csvs, path)
    plt = make_chart(importances, path)
    end = time.time() - start
    print("Done. Took",end,"seconds.")
    plt.show()
    
# makes the matplotlib figure
def make_chart(importances:list, path:str):
    xs = 1
    x1 = []
    x2 = []
    x3 = []
    x4 = []
    # scale to data size
    scale = [1533, 910605, 2192593, 89214]
    for i in range(len(importances)):
        x1.append((importances[i][0]/scale[i])*xs)
        x2.append((importances[i][1]/scale[i])*xs)
        x3.append((importances[i][2]/scale[i])*xs)
        x4.append((importances[i][3]/scale[i])*xs)
    labels = ["0-999", "1000-1499", "1500-1999", "2000+"]
    line_labels = ["Castling", "Center Square Control", "Gambits" ,"Unique Pieces Moved"]
    x = np.arange(len(labels))
    w = 0.2
    plt.bar(x+-.2, x1, width=w, color='g', align='center', label = line_labels[0], edgecolor="black")
    plt.bar(x, x2, width=w, color='c', align='center', label = line_labels[1], edgecolor="black")
    plt.bar(x+.2, x3, width=w, color='b', align='center', label = line_labels[2], edgecolor="black")
    plt.bar(x+.4, x4, width=w, color='m', align='center', label = line_labels[3], edgecolor="black")
    plt.xlabel('Rating Ranges')
    plt.ylabel('F-value scores')
    plt.title('Best Features When Predicting Game Outcome')
    plt.xticks(np.arange(4), (labels))
    plt.legend()
    plt.savefig('FeatureImportance.png')
    return plt

# opens all the files and returns a list of file objects instead of strings
def open_all(out_names:list):
    files = []
    for name in out_names:
        f = open(name, "a")
        files.append(f)
    return files

# do the analysis!
# returns an array that represents the ranking of features using univariate selection
def analyze(csv, data):
    # data: the data in CSV:
    # format: when_castled,num_center_squares_controlled,material_difference,num_unique_pieces_moved,win
    y = data.iloc[:,-1]
    x = data.iloc[:,0:-1]
    scaler = MinMaxScaler()
    x = scaler.fit_transform(x)
    x = pd.DataFrame(x)
    kbest = SelectKBest(score_func=f_classif, k=4)
    importance = pd.DataFrame(kbest.fit(x,y).scores_)
    rating_range = get_range(csv)
    importance = importance.nlargest(4, 0)
    importance_ar = importance[0].tolist()
    return importance_ar

# strips the csv of their GAMES tag.
def strip_csv(csv:str):
    return csv.split("GAMES")[0]

# get all the relevant csvs from the databases directory
def get_csvs(path:str):
    csvs = []
    for root, directories, files in os.walk(path, topdown=False):
	    for name in files:
		    if (".csv" in name) and ("FEATURES" in name): csvs.append(os.path.join(root, name))
	    for name in directories:
		    if (".csv" in name) and ("FEATURES" in name): csvs.append(os.path.join(root, name))
    return csvs

# iterate through all the csvs. calls the processing function.
def iterate_csvs(csvs:list, path:str):
    importances = []
    for csv in csvs:
        data = pd.read_csv(csv)
        print("analyzing",csv)
        rating_range = get_range(csv)
        importance = analyze(csv, data)
        importances.append(importance)
    return importances

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
        print("NOTE: must be run with python3 because of the sklearn library")
    else:
        main(sys.argv[1:])
