"""
Author: Kaikai Du
NOTE: requires stopwords.txt and numpy
"""

import sys
import numpy as np
import re

def parse_stopwords():
    stopwords = set()
    try:
        with open('stopwords.txt','r') as file:
            for line in file:
                line = line.strip().split()
                stopwords.update(line)
    except Exception as e:
        print(f"Error: {e} occured when reading stopwords")
    return stopwords

def get_block(file):
    block = []
    for raw_line in file: 
        line = raw_line.strip().lower()
        if not line.strip():
            if block:
                return block
            else:
                continue
        else:
            block.append(line)
    return block or None

def strip_stopwords(raw_bio,stopwords):
    bio = set()
    for raw_line in raw_bio:
        line = raw_line.split()
        for word in line:
            word = re.sub(r'[^a-zA-Z]', '', word)   
            #I strip punctuation here since I believe it makes sense, but it is not explicitly stated to do so in the spec
            if len(word) > 2 and word not in stopwords:
                bio.add(word)
    return bio

def update_occurrences(word_occ, unique_words,cat):
    for word in unique_words:
        if word not in word_occ:
            word_occ[word] = {}
        if cat not in word_occ[word]:
            word_occ[word][cat] = 0
        word_occ[word][cat] += 1
    
def train(file,stopwords,N,e):
    n_bios = 0
    n_categories = {}
    word_occ = {} #track category occurences of each word. word -> dict{category -> # occurences} it appears in 
    while n_bios < N:
        #block[0] is the person, block[1] is the category, block[2:] is the bio
        #do something here
        block = get_block(file)
        name,cat = block[0],block[1]
        n_categories[cat] = n_categories.get(cat,0.0) + 1
        unique_words = strip_stopwords(block[2:],stopwords)
        update_occurrences(word_occ,unique_words,cat)
        #update iterators 
        n_bios += 1

    #now calculate probas 
    probas = [{},{}] #probas[0] are the category likelihoods, probas[1] are the conditional likelihoods
    #probas[1] is structured as (word -> (cat -> likelihood))
    T = float(n_bios) #denominator of freq, # of bios
    n_cats = len(n_categories)
    for cat,occ in n_categories.items():
        freq_c = float(occ) / T 
        L_c = -np.log2((freq_c + e) / (1 + n_cats*e))  
        probas[0][cat] = L_c
    
    word_likelihoods = probas[1]
    for word,cat_occs in word_occ.items():
        for cat,cat_total_occurences in n_categories.items():
            if cat in cat_occs:
                word_cat_occs = cat_occs[cat]
            else:
                word_cat_occs = 0
            freq_w_c = float(word_cat_occs) / float(cat_total_occurences)
            L_w_c = -np.log2((freq_w_c + e) / (1 + 2*e))
            if word not in word_likelihoods:
                word_likelihoods[word] = {cat : float(L_w_c)}
            else:
                word_likelihoods[word][cat] = float(L_w_c)

    return probas,n_categories

def L(L_c, cat,lh,bio):
    #lh is a dict (word -> (cat -> likelihood))
    #corresponds to probas[1] from the training func
    L_c_b = L_c
    for word in bio:
        L_c_b += lh[word][cat] if word in lh and cat in lh[word] else 0.0
    return L_c_b

def evaluate_prediction(name,preds,target):
    predicted_category = max(preds,key = preds.get)
    correct = predicted_category == target
    result = "Right." if correct else "Wrong."
    print(f"{name}.  Prediction: {predicted_category}.  {result}")
    parts = [f"{cat}: {preds[cat]:.2f}" for cat in sorted(preds.keys())]
    print(" ".join(parts))
    print()

    return 1 if correct else 0

def test(file,stopwords,N,e,probas,n_categories):
    #the file pointer should be at the correct spot since this is the same iterator that was used in training
    #it should remain where the training stopped
    #probas corresponds directly to probas from train
    block = get_block(file)
    cats = list(n_categories.keys())
    num_correct = 0
    n_total = 0
    while block is not None:
        full_name = block[0]
        target = block[1] #target category i.e. correct answer
        unique_words = strip_stopwords(block[2:],stopwords)
        c_i = {cat : float(L(probas[0].get(cat,0.0),cat,probas[1],unique_words)) for cat in cats}
        m = min(list(c_i.values()))
        xi_per_category = {cat : float((np.exp2(m-c_i[cat]) if c_i[cat] - m < 7 else 0.0))for cat in cats}
        s = sum(list(xi_per_category.values()))
        preds = {cat : xi_per_category[cat]/s for cat in cats}
        num_correct += evaluate_prediction(full_name,preds,target)
        block = get_block(file)
        n_total += 1
    print(f"Overall accuracy: {num_correct} out of {n_total} = {float(num_correct)/float(n_total)}")

def run(filepath,stopwords,N,e = 0.1):
    if N == -1:
        N = np.inf
    try:
        with open(filepath,'r') as file:
           probas,n_categories = train(file,stopwords,N,e)
           test(file,stopwords,N,e,probas,n_categories)

    except Exception as e:
        print(f"Error: {e} occured during execution")

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Correct usage: python3 textClassifier.py <input_filepath> <training set partition>")
        sys.exit(1)
    input_filepath = sys.argv[1]
    training_set_size = int(sys.argv[2])
    stopwords = parse_stopwords()
    run(input_filepath,stopwords,training_set_size)