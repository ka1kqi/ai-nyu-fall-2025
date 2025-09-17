"""
Author: Kaikai Du
Artificial Intelligence Programming Assignment 1
Hill climbing
"""
import re 
import sys
import numpy as np
import random as rand

verbose = False
target = 0
num_random_restarts = -1

"""
Utility functions
"""
def parse_input_file():
    global verbose
    global target
    global num_random_restarts
    try:
        table = {}
        target = 0
        with open('input.txt','r',encoding = 'utf-8') as file:
            first_line = file.readline().strip().split(" ")
            target = int(first_line[0])
            verbose = True if first_line[1] == 'V' else False
            if len(first_line) == 3:
                num_random_restarts = int(first_line[2])
            else:
                print("Incorrect input, please specify number of random restarts")
                sys.exit(0)

            for line in file:
                line = re.sub(r'\s\s+', ' ',line.strip()).split(' ')
                table[line[0]] = (int(line[1]),int(line[2]),int(line[3]))

    except Exception as e:
        print(f"encountered exception {e} while parsing input file")
    
    return table

def sum_path(tasks: dict, path: list):
    total = 0
    for t in path:
        total += tasks[t][0]
    return total

def sum_timestamp(tasks: dict, path: list):
    total = 0
    for t in path:
        total += tasks[t][1]
    return total

def parse_path(tasks: dict, path: list):
    total_value = sum_path(tasks,path)
    timestamp = sum_timestamp(tasks,path)
    return total_value, timestamp

#error function for hill climbing
def error(tasks : dict, path: list):
    e = max(24-sum_path(tasks,path),0)
    cur_time = 0
    for t in path:
        length = tasks[t][1]
        deadline = tasks[t][2]
        cur_time += length
        if cur_time > deadline:
            e += cur_time - deadline
    return e

def print_path(tasks:dict,path: list):
    print(*(t for t in path), end = " ")
    print(f"Value = {sum_path(tasks,path)}")

def print_path_hc(tasks:dict,path: list):
    print(*(t for t in path), end = " ")
    print(f"Value = {sum_path(tasks,path)}",end = " ")
    print(f"Error = {error(tasks,path)}")

def can_schedule(tasks: dict, path: list):
    cur_time = 0
    for t in path:
        cur_time += tasks[t][1]
        if cur_time > tasks[t][2]:
            return False
    return True

"""
Hill climbing search functions
"""
def generate_starting_state(tasks: dict):
    starting_nodes = []
    for t in tasks:
        n = rand.choice([0,1])
        if n:
            starting_nodes.append(t)
    starting_nodes = np.random.permutation(starting_nodes)
    return list(starting_nodes), sum_path(tasks,starting_nodes), error(tasks,starting_nodes)

def generate_neighbors(tasks: dict, path: list):
    neighbors = []
    #add tasks not in 
    for t in tasks:
        if t not in path:
            new_path = path + [t]
            neighbors.append(new_path)

    #remove task
    for i in range(len(path)):
        new_path = path[:i] + path[i+1:]
        if len(new_path) > 0:
            neighbors.append(new_path)

    #swap every pair
    for i in range(len(path)-1):
        new_path = path[:]
        new_path[i],new_path[i+1] = new_path[i+1],new_path[i]
        neighbors.append(new_path)

    return neighbors

def hill_climbing(tasks: dict):
    path, _, err = generate_starting_state(tasks)
    print(f"Randomly chosen start state: ", end = "")
    print_path_hc(tasks,path)
    if err == 0:
        return path, err
    while True:
        neighbors = generate_neighbors(tasks,path)
        cur_error = err
        if verbose:
            print("Move to ",end = "")
            print_path_hc(tasks,path)
            print("Neighbors")
        for nb in neighbors:
            if verbose:
                print_path_hc(tasks,nb)
            e = error(tasks, nb)
            if e == 0:
                return nb, e
            if e < err:
                path = nb
                err = e
        if err == cur_error:
            #search failed, reached local max with no solution
            return [],sys.maxsize
        if verbose:
            print()

    return path, err

def rr_hill_climbing(tasks: dict,n: int):
    #n: number of random restarts
    best_path = []
    best_error = sys.maxsize
    for i in range(n):
        path, error = hill_climbing(tasks)
        if error == 0:
            if verbose:
                print()
            return path, error
        if error < best_error:
            best_error = error
            best_path = path
        if verbose:
            print()
    return best_path, best_error

def main():
    tasks = parse_input_file()
    hc_path, _ = rr_hill_climbing(tasks,num_random_restarts)

    if len(hc_path) == 0:
        print("No solution found")
    else:
        print("Found solution ",end="")
        print_path(tasks,hc_path)

main()