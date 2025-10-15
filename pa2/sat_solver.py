import dpll
import re

dpll.debug = False
dpll.strategy = True

class SymTable():
    def __init__(self):
        self.sym_to_id = {}
        self.id_to_sym = ["<Placeholder>"]
    def atomize(self,sym):
        if sym in sym_to_id:
            return sym_to_id[sym] 
        new_idx = len(self.id_to_sym)
        self.sym_to_id[sym] = new_idx
        self.id_to_sym.append(sym)
        return new_idx
    def get_sym_from_id(self,id_):
        return id_to_sym[id_]

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
    node_map = mazeInfo.node_map
    treasure = mazeInfo.treasures
    treasure_map = mazeInfo.treasure_map
    treasure_source = mazeInfo.treasure_source
    K = mazeInfo.nSteps

    clauses.append({st.atomize(cnf_AT("START",0))})

    for T in treasures:
        clauses.append({-st.atomize(cnf_HAS(T,0))})
        clauses.append({st.atomize(cnf_HAS(T,K))})
    
    #cant be at two places at once
    for t in range(K+1):
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                n1,n2 = nodes[n1],nodes[n2]
                lit1 = -st.atomize(cnf_AT(n1,t))
                lit2 = -st.atomize(cnf_AT(n2,t))
                clauses.append({lit1,lit2})
    
    #if at treasure location then pick up treasure
    for t in range(K+1):
        for n in nodes:
            for T in treasure_map[n]:
                clauses.append({-st.atomize(cnf_AT(n,t)), st.atomize(st.atomize(cnf_HAS(T,t)))})
    
    #movement
    for t in range(K):
        for n in nodes:
            neighbors = node_map[n]
            clause = {-st.atomize(cnf_AT(n,t))}
            for N in neighbors:
                clause.add(st.atomize(cnf_AT(N,t+1)))
            clauses.append(clause)

    #treasure persists in posession
    for t in range(1,K+1):
        for T in treasure:
            clauses.append({-st.atomize(cnf_HAS(T,t-1)), st.atomize(cnf_HAS(T,t))})

    #if pickup T at t, then at T at t
    for t in range(1,K+1):
        for T in treasures:
            clause = {st.atomize(cnf_HAS(T,t-1)),-st.atomize(cnf_HAS(T,t))}
            for n in treasure_source[T]:
                clause.add(st.atomize(cnf_AT(n,t)))
            clauses.append(clause)
            
    return clauses, st
