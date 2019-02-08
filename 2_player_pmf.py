from random import *
import math
import matplotlib.pyplot as plt
import numpy as np
from itertools import groupby

K = 800 / np.log(10)
INIT_ELO = 1000
REAL_ELO = 1030

ROUNDS = 100

MAX_ENTRIES = 100000
RESOLUTION = 0.1

TOTAL_WIN = 10**(2*INIT_ELO/400)
def win_prob(elo):
  elo = 10**(elo/400)
  return elo/(elo+TOTAL_WIN/elo)
REAL_WIN = win_prob(REAL_ELO)

def get_next_entries(entry):
  elo, p = entry
  t = win_prob(elo)
  win = (elo+K*(1-t), p*REAL_WIN)
  lose = (elo+K*(0-t), p*(1-REAL_WIN))
  return win, lose

def get_update_pmf(entries):
  return [next_entry for entry in entries for next_entry in get_next_entries(entry)]

def merge_entries(entries):
  x, p = zip(*entries)
  return (np.average(x, weights=p), np.sum(p))

def merge_close(entries):
  entries.sort()
  re = []
  for k, g in groupby(entries, lambda x: int(x[0]/RESOLUTION)):
    re.append(merge_entries(g))
  return re

def weighted_avg_var(values, weights):
  average = np.average(values, weights=weights)
  variance = np.average((values-average)**2, weights=weights)
  return (average, variance)

def main():
    elo_pmf = [(INIT_ELO, 1)]
    avg_var = []
    for i in range(ROUNDS):
      elo_pmf = get_update_pmf(elo_pmf)
      if len(elo_pmf) > MAX_ENTRIES:
        elo_pmf = merge_close(elo_pmf)
      avg_var.append(weighted_avg_var(*zip(*elo_pmf)))
      # print("round {} done; {} entries left; (avg, var)={}".format(i+1, len(elo_pmf), avg_var[-1]))

    print("plotting...")

    # plot pmf
    x, y = zip(*elo_pmf)
    plt.figure(1)
    params = 'pmf after {} rounds; real_elo:{}, K:{}'.format(ROUNDS, REAL_ELO, K)
    plt.title(params)
    plt.hist(x, weights=y, bins=range(int(min(x)), int(max(x))+1))
    plt.show()

    # plot history of average and variance
    '''
    plt.figure(2)
    avg, var = zip(*avg_var)
    plt.errorbar(range(ROUNDS), avg, np.sqrt(var))
    plt.title('average elo over rounds')
    plt.show()
    '''



if __name__ == '__main__':
    main()
