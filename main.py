from random import *
import math
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce

POPULATION = 30
INTRAPLAYER_SIGMA = 10
INTERPLAYER_SIGMA = 20
K = 16
INIT_ELO = 1500

ROUNDS = 100000

class Player(object):
    """docstring for Player"""
    def __init__(self, id, strength, initial_elo):
        self.id = id
        self.strength = strength
        self.elo = initial_elo
        self.win = 0
        self.lose = 0
        self.tie = 0
        self.elo_record = [initial_elo]


    def get_random_strength(self):
        return normalvariate(self.strength, INTRAPLAYER_SIGMA)

    def record_elo(self):
        self.elo_record.append(self.elo)

    def get_average_elo(self, last_n_percent):
        averaging_range = math.floor(last_n_percent * len(self.elo_record))
        return np.average(self.elo_record[averaging_range:]) 

    def get_max_elo(self):
        '''
        Return max elo ever achieved by player.
        '''
        return max(self.elo_record)

def update_elo(winner, loser, tie=False):
    Qa = pow(10, winner.elo/400)
    Qb = pow(10, loser.elo/400)

    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)

    if not tie:
        winner.elo = winner.elo + K*(1 - Ea)
        loser.elo = loser.elo + K*(0-Eb)

        winner.win += 1
        loser.lose += 1
    else:
        winner.elo = winner.elo + k*(0.5 - Ea)
        loser.elo = loser.elo + k*(0.5-Eb)

        winner.tie += 1
        loser.tie += 1


def find_match(player_list):
    """
    Returns two players.
    """
    population = len(player_list)

    player1 = player2 = player_list[math.floor(random() * population)]
    
    while player1 == player2:
        player2 = player_list[math.floor(random() * population)]

    return (player1, player2)

def get_expected_winrate_given_elo_diff(elo_diff):
    # elo_diff = p1_elo = p2_elo
    p1_winrate = (1 + 10**(-elo_diff/400))**-1
    p2_winrate = (1 + 10**(elo_diff/400))**-1
    return p1_winrate, p2_winrate

def calc_theoretical_win_rate(player1, player2):
    
    def normal_cdf(x, mean, sigma):
        return 0.5 * (1 + math.erf( (x-mean)/(sigma * math.sqrt(2)) ))
    
    # Z = X - Y
    # X : (random variable) player1 strength.
    # Y : (random variable) player2 strength.
    z_mean = player1.strength - player2.strength
    z_sigma = math.sqrt(2*INTRAPLAYER_SIGMA**2)
    
    # P(Z < 0)
    p2_winrate = normal_cdf(0, z_mean, z_sigma)
    # P(Z > 0) = 1 - P(Z < 0)
    p1_winrate = 1 - p2_winrate 

    return p1_winrate, p2_winrate

def calc_theoretical_elo_diff(player1, player2):
    """
    Returns player1_theoretical_elo - player2_theoretical_elo
    """
    p1_winrate, p2_winrate = calc_theoretical_win_rate(player1, player2)
    return (math.log(p1_winrate, 10) - math.log(p2_winrate, 10)) * 400

def get_theoretical_elo(player, player_list):
    N = len(player_list)

    # Calculate sum of player elo difference.
    elo_diff_sum = 0
    for opponent in player_list:
        if opponent == player:
            continue
        elo_diff_sum += calc_theoretical_elo_diff(player, opponent)

    average_elo_diff_with_player = float(elo_diff_sum)/(N-1) # subtract self
    average_elo = float(sum(p.elo for p in player_list) - player.elo)/(N-1)

    return average_elo + average_elo_diff_with_player

def get_two_players_elo_diff_pmf(p1_strength, p2_strength):
    '''
    Returns pmf of p1_elo - p2_elo
    '''
    player1 = Player(0, p1_strength, p1_strength)
    player2 = Player(1, p2_strength, p2_strength)

    upper = 500
    transfer_matrix = np.zeros((2 * upper, 2 * upper))
    p1_theoretical_win_rate, p2_theoretical_win_rate = calc_theoretical_win_rate(player1, player2) 
    print(p1_theoretical_win_rate, p2_theoretical_win_rate)
    # Build transfer matrix.
    for i in range(-upper, upper):
        p1_expected_win_rate, p2_expected_win_rate = get_expected_winrate_given_elo_diff(i)
        print(p1_expected_win_rate, p2_expected_win_rate)
        # Win case.
        p1_win_elo_diff = math.floor(i + 2 * K * p2_expected_win_rate)
        if p1_win_elo_diff >= upper:
            transfer_matrix[2 * upper-1][i] = p1_theoretical_win_rate
        else:
            transfer_matrix[upper + p1_win_elo_diff][i] = p1_theoretical_win_rate
        # Lose case.
        p1_lose_elo_diff = math.floor(i - 2 * K * p1_expected_win_rate)
        if p1_lose_elo_diff < -upper:
            transfer_matrix[0][i] = p2_theoretical_win_rate
        else:
            transfer_matrix[upper + p1_lose_elo_diff][i] = p2_theoretical_win_rate
    # Find pmf of elo_diff.
    elo_diff_pmf = np.zeros(2 * upper)
    elo_diff_pmf[upper] = 1 # intialize by giving elo_diff = 0 have probability 1
    # Iterate for N rounds.
    N = 10000
    for i in range(N):
        elo_diff_pmf = transfer_matrix.dot(elo_diff_pmf)
    '''
    print(sum(elo_diff_pmf))
    elo_diff_mean = 0
    for i in range(len(elo_diff_pmf)):
        elo_diff_mean += i * elo_diff_pmf[i]
    print(elo_diff_mean)
    print(get_theoretical_elo(player1, [player1, player2]))
    '''
    return elo_diff_pmf

def main():
    '''
    player_list = [Player(i, normalvariate(1000, INTERPLAYER_SIGMA), INIT_ELO) for i in range(POPULATION)]


    for i in range(ROUNDS):
        player1, player2 = find_match(player_list)

        if player1.get_random_strength() >= player2.get_random_strength():
            update_elo(winner=player1, loser=player2)
        else:
            update_elo(winner=player2, loser=player1)

        for player in player_list:
            player.record_elo()

    # print status of each player
    for player in player_list:
        print('strength={:4.2f}, elo={:4.2f}, win={:2d}, lose={:2d}'\
            .format(player.strength, player.elo, player.win, player.lose))

    # plot data
    for player in player_list:
        plt.plot(player.elo_record)
        plt.annotate(round(player.strength), xy=(ROUNDS, player.elo_record[-1]))

    # plot label & title.
    params = 'population:{}, σ-inter:{}, σ-intra:{}'.format(POPULATION, INTERPLAYER_SIGMA, INTRAPLAYER_SIGMA)
    plt.title(params)
    plt.xlabel('rounds')
    plt.ylabel('elo')


    ## test diff
    print('#' * 20)
    print('player0-player1={}, theoretical={}'.format(player_list[0].get_average_elo(0.1) - player_list[1].get_average_elo(0.1),\
     calc_theoretical_elo_diff(player_list[0], player_list[1])))
    print('player0.elo={}, theoretical={}'.format(player_list[0].get_average_elo(0.05),\
     get_theoretical_elo(player_list[0], player_list)))

    plt.show()
    '''
    p1_strength = 110
    p2_strength = 100
    pmf = get_two_players_elo_diff_pmf(p1_strength, p2_strength)
    # print(len(pmf))
    x_values = np.linspace(-len(pmf)/2, len(pmf)/2, len(pmf))
    plt.plot(x_values, pmf)
    plt.axis([min(x_values), max(x_values), 0, max(pmf)])
    plt.xlabel('elo_diff')
    plt.ylabel('probabiltiy')
    plt.show()

if __name__ == '__main__':
    main()
