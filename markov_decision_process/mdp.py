'''
Author: Kaikai Du
Markov Decision Process in Python
'''

import random
import sys

#store program info
class Param:
    def __init__(self,N,n_term,n_actions,n_rounds,freq,M):
        self.n_terminal = n_term    #number of terminal states
        self.N = N                  #number of states
        self.n_actions = n_actions  #number of possible actions
        self.n_rounds = n_rounds    #number of rounds to simulate
        self.v = freq               #print frequency
        self.M = M                  #explore/explore coefficient
        self.rewards = {}           #rewards of each terminal state
        self.transitions = {}       #transitions is a map of states with the values as a dict of probabilities under each action
        self.terminal_states = []   #terminal states of the markov process
        self.states = []            #states not including terminal states
        self.costs = {}             #costs of each action

class Score():
    def __init__(self, S, A):
        self.counts = [[0 for _ in range(A)] for _ in range(S)]
        self.totals = [[0.0 for _ in range(A)] for _ in range(S)]

def parse_input():
    try:
        with open('input.txt','r') as file:
            line = file.readline().strip().split(' ')
            params = Param(int(line[0]),int(line[1]),int(line[2]),int(line[3]),int(line[4]),int(line[5]))

            #rewards at terminal states
            line = file.readline().strip().split(' ')
            for i in range(0,len(line),2):
                params.rewards[int(line[i])] = int(line[i+1])
                params.terminal_states.append(int(line[i]))
            
            for i in range(params.N):
                if i not in params.terminal_states:
                    params.states.append(i)
            
            #costs of each action
            line = file.readline().strip().split(' ')
            for i in range(0,len(line),2):
                params.costs[int(line[i])] = float(line[i+1])
            
            #transition probabilities
            for st in file:
                line = st.strip().split(' ')
                state_action = line[0].split(':')
                state = int(state_action[0])
                action = int(state_action[1])
                T = {}
                for i in range(1,len(line),2):
                    #maps state to probability i.e. (transition to state = line[i] with p = line[i+1])
                    T[int(line[i])] = float(line[i+1])
                if state not in params.transitions:
                    params.transitions[state] = {action: T}
                else:
                    params.transitions[state][action] = T
            file.close()
        return params
    except Exception as e:
        print(f"Error occured while parsing input file")
        sys.exit()


def choose_action(S,counts,totals,params):
    n = params.n_actions
    M = params.M
    #look for untried actions first
    for i in range(n):
        if counts[S][i] == 0:
            return i
    avg = [totals[S][i]/counts[S][i] for i in range(n)]
    top = max(params.rewards)
    bot = min(min(avg),min(params.rewards))
    if top != bot:
        s_avg = [0.25 + .75*(avg[i]-bot)/(top-bot) for i in range(n)]
    else:
        s_avg = [0.625 for _ in range(n)]
    c = sum(counts[S][i] for i in range(n))
    up = [s_avg[i] ** (float(c)/float(M)) for i in range(n)]
    norm = sum(up)
    p = [x/norm for x in up]
    assert(abs(1-sum(p)) < 0.00001)
    actions = list(range(n))
    return random.choices(actions,weights=p,k=1)[0]

def print_matrix(mat,label):
    float_fmt = '.3f'
    rows = len(mat)
    cols = len(mat[0])
    print(f"{label}:")

    def to_str(v):
        if isinstance(v, float):
            return format(v, float_fmt)
        return str(v)

    str_grid = [[to_str(mat[i][j]) for j in range(cols)] for i in range(rows)]
    val_widths = [max(len(str_grid[i][j]) for i in range(rows)) for j in range(cols)]
    idx_width = max(len(f"[{rows-1},{cols-1}]="), len("[0,0]="))
    for i in range(rows):
        parts = []
        for j in range(cols):
            idx = f"[{i},{j}]=".ljust(idx_width)
            val = str_grid[i][j].ljust(val_widths[j])
            parts.append(idx + val)
        print("  ".join(parts))
    print()

def print_state(S,n_states,n_actions,round_number):
    print(f"After {round_number} rounds")

    best_actions = {}
    for s in range(n_states):
        best_action = 0
        for a in range(n_actions):
            if S.counts[s][a] == 0:
                best_action = 'U'
                break
            if S.totals[s][a]/S.counts[s][a] > S.totals[s][best_action]/S.counts[s][best_action]:
                best_action = a 
        best_actions[str(s)] = str(best_action)
    
    print_matrix(S.counts,"Count")
    print_matrix(S.totals,"Total")
    print("Best action: ",end = "")
    for state,action in best_actions.items():
        print(f"{state}:{action}. ",end = '')
    print()
    print()

def train(params):
    S = Score(params.N, params.n_actions)
    states = params.states
    T = params.transitions
    n_states = params.N
    n_actions = params.n_actions
    for rd in range(params.n_rounds):
        #choose random starting state
        state = random.choice(states)
        cost = 0.0
        visited = set() #set of visited (state,action) pairs (list of tuples)
        while state not in params.terminal_states:
            action = choose_action(state,S.counts,S.totals,params)
            visited.add((state,action))
            cost += params.costs[action]
            possible_next_states = list(T[state][action].keys())
            W = list(T[state][action].values())
            state = random.choices(possible_next_states,weights=W,k=1)[0]

        reward = params.rewards[state]
        for state,action in visited:
            S.counts[state][action]+=1
            S.totals[state][action]+=(reward-cost)

        if rd % params.v == 0:
            #compute average
            print_state(S,n_states,n_actions,rd)
    if params.n_rounds % params.v == 0:
        print_state(S,n_states,n_actions,params.n_rounds)

if __name__ == "__main__":
    params = parse_input()

    train(params)

