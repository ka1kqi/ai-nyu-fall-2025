'''
Author: Kaikai Du
No special instructions for running this, just place the maze in the input.txt file to run.
'''

import dpll
import re 
import sys

dpll.debug = False
dpll.strategy = True

class SymTable:
    def __init__(self):
        self.str_to_id = {}
        self.id_to_str = ['<Placeholder>']
    def atomize(self,sym):
        if sym in self.str_to_id:
            return self.str_to_id[sym]
        symbol_id = len(self.id_to_str)
        self.str_to_id[sym] = symbol_id
        self.id_to_str.append(sym)
        return symbol_id
    def get_sym_from_id(self,id_):
        return self.id_to_str[id_]
    def size(self):
        return len(self.id_to_str)-1

class MazeInfo():
    def __init__(self,n,t,ns,nm,tm,ts):
        self.nodes = n
        self.treasures = t
        self.nSteps = ns
        self.node_map = nm
        self.treasure_map = tm
        self.treasure_source = ts

def cnf_AT(N,t):
    return f"At({N},{t})"
def cnf_HAS(T,t):
    return f"Has({T},{t})"

def parse_maze(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() != ""]

    nodes = lines[0].split()
    node_map = {n:[] for n in nodes}
    treasures = lines[1].split()
    treasure_map = {n:set() for n in nodes}

    nSteps = int(lines[2].strip())

    for line in lines[3:]:
        ln = line.split()
        N = ln[0]
        index_next = ln.index('NEXT')
        for t in ln[2:index_next]:
            treasure_map[N].add(t)

        node_map[N] = ln[index_next+1:]

    treasure_source = {t:[] for t in treasures}
    for n in nodes:
        for t in treasure_map[n]:
            treasure_source[t].append(n)
        
    return MazeInfo(nodes,treasures,nSteps,node_map,treasure_map,treasure_source)

def conjunctivize(mazeInfo):
    st = SymTable()
    clauses = []

    nodes = mazeInfo.nodes
    treasures = mazeInfo.treasures
    node_map = mazeInfo.node_map
    N = mazeInfo.nSteps
    treasure_map = mazeInfo.treasure_map
    treasure_source = mazeInfo.treasure_source

    #at start at t = 0
    clauses.append({st.atomize(cnf_AT('START',0))})

    #no treasures at t = 0
    for t in treasures:
        clauses.append({-st.atomize(cnf_HAS(t,0))})

    #all treasure at t = N
    for t in treasures:
        clauses.append({st.atomize(cnf_HAS(t,N))})

    #no two nodes at same time
    for t in range(N+1):
        for i in range(len(nodes)):
            for j in range(i+1,len(nodes)):
                n1,n2 = nodes[i], nodes[j]
                lit1 = -st.atomize(cnf_AT(n1,t))
                lit2 = -st.atomize(cnf_AT(n2,t))
                clauses.append({lit1,lit2})

    #pickup treasure
    for t in range(N+1):
        for n in nodes:
            for T in treasure_map[n]:
                clauses.append({-st.atomize(cnf_AT(n,t)),st.atomize(cnf_HAS(T,t))})

    #move to neighbor
    for t in range(N):
        for n in nodes:
            neighbors = node_map[n]
            clause = {-st.atomize(cnf_AT(n,t))}
            for node in neighbors:
                clause.add(st.atomize(cnf_AT(node,t+1)))
            clauses.append(clause)

    #if pickup T at time t then at T at time t
    for t in range(1,N+1):
        for T in treasures:
            clause = {st.atomize(cnf_HAS(T,t-1)), -st.atomize(cnf_HAS(T,t))}
            for source in treasure_source[T]:
                clause.add(st.atomize(cnf_AT(source,t)))
            clauses.append(clause)

     #persistence of treasures
    for t in range(1,N+1):
        for T in treasures:
            clauses.append({-st.atomize(cnf_HAS(T,t-1)),st.atomize(cnf_HAS(T,t))})
    
    return clauses, st

def solve(mazeInfo):
    print()

def decode_path(bindings,mazeInfo, st):
    path = []
    N = mazeInfo.nSteps
    for t in range(N+1):
        here = '_'
        for n in mazeInfo.nodes:
            if bindings[st.atomize(cnf_AT(n,t))] == 1:
                here = n
        path.append(here)
    return " ".join(path)

def main():
    with open('input.txt','r') as f:
        text = f.read()
    
    mazeInfo = parse_maze(text)
    clauses, st = conjunctivize(mazeInfo)
    found,bindings = dpll.DPLLTop(clauses)
    if not found:
        print("No solution found")
        return
    print(decode_path(bindings,mazeInfo,st))

if __name__ == "__main__":
    main()