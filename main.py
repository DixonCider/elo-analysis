from random import *
import math
import matplotlib.pyplot as plt

POPULATION = 50
INTRAPLAYER_SIGMA = 10
INTERPLAYER_SIGMA = 30
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


def main():
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
    plt.show()


if __name__ == '__main__':
    main()