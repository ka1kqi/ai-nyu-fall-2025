"""
Author: Kaikai Du
Artificial Intelligence Programming Assignment 1
Iterative deepening
"""
import re 

verbose = False
target = 0

"""
Utility functions
"""
def parse_input_file():
    global verbose
    global target
    try:
        table = {}
        target = 0
        with open('input.txt','r',encoding = 'utf-8') as file:
            first_line = file.readline().strip().split(" ")
            target = int(first_line[0])
            verbose = True if first_line[1] == 'V' else False

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

def print_path_id(tasks:dict,path: list):
    print(*(t for t in path), end = " ")
    print(f"Value = {sum_path(tasks,path)}")

def can_schedule(tasks: dict, path: list):
    cur_time = 0
    for t in path:
        cur_time += tasks[t][1]
        if cur_time > tasks[t][2]:
            return False
    return True


"""
Iterative deepening search functions
"""
def dfs(tasks: dict, k: int, n: int, path: list):
    if verbose:
        print_path_id(tasks,path)
    if n == k:
        #if we have reached target depth then we stop recursion
        return path, sum_path(tasks,path)

    total_value, cur_time = parse_path(tasks,path)
    if total_value >= target:
        return path, total_value

    for t,t_info in tasks.items():
        if t not in path:
            new_path = path + [t]
            if can_schedule(tasks,new_path):
                child_path,value= dfs(tasks,k,n+1,new_path)
                if value >= target:
                    return child_path,value
            
    return [],-1

def iterative_deepening(tasks: dict):
    for max_depth in range(0,len(tasks)):
        if verbose:
            print(f"Depth = {max_depth}")
        for t in tasks:
            path, value = dfs(tasks,max_depth,0,[t])
            if value >= target:
                return path
        if verbose:
            print()
    
    return []


def main():
    tasks = parse_input_file()
    id_return_path = iterative_deepening(tasks)
    if id_return_path == []:
        print("No solution found")
    else:
        print("Found solution: ",end = "")
        print_path_id(tasks,id_return_path)
    
main()