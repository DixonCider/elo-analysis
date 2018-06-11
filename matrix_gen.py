from random import *
import math
import matplotlib.pyplot as plt
import numpy as np

GAME_NAME = 'random'
STORIES = 3
POPULATION = 6
K = 16
INIT_ELO = 1000

ROUNDS = 100000


def gen_win_rate(population):
  win_rate = np.random.random((population, population))  
  win_rate /= win_rate + win_rate.T
  return win_rate


class Player(object):
  """docstring for Player"""
  def __init__(self, id, initial_elo):
    self.id = id
    self.elo = initial_elo
    self.win = 0
    self.lose = 0
    self.tie = 0
    self.elo_record = [initial_elo]

  def get_description(self, id):
    return None;

  def record_elo(self):
    self.elo_record.append(self.elo)


class Rules(object):
  def __init__(self):
      self.game_name = GAME_NAME
      self.stories = STORIES
      self.population = POPULATION
      self.K = K
      self.init_elo = INIT_ELO
      self.rounds = ROUNDS


class Background(object):
  def __init__(self, gen_win_rate):
    try:
      self.rules = self.read_rules()
    except:
      self.rules = Rules()
    try:
      self.win_rate = self.read.win_rate()
    except:
      self.win_rate = gen_win_rate(self.rules.population)
    
  def read_rules(self):
    return np.load('rules')
    
  def read_win_rate(self):
    return np.load('win_rate_matrix')

  def write(self):
    return np.save('rules', self.rules) and np.save('win_rate_matrix', self.matrix) 


class Story(object):
  def __init__(self, id, bg):
    self.id = id
    try:
      self.player_list = self.read_player_list()
    except:
      self.player_list = np.array([Player(i, bg.rules.init_elo) for i in range(bg.rules.population)])

  def read(self):
    return np.load('player_list_'+str(self.id), self.player_list)

  def write(self):
    return np.save('player_list_'+str(self.id), self.player_list)

  def done_rounds(self, bg):
    return len(self.player_list[0].elo_record)



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


def battle(player1, player2, win_rate):
  if np.random.random() < win_rate[player1.id][player2.id]:
    return player1, player2
  else:
    return player2, player1

'''
def SMA(data, period=int(ROUNDS/100)):
  return np.convolve(data, np.ones(period)/period, mode='valid')
'''

def main():
  bg = Background(gen_win_rate)
  bg.write()
  for story_id in range(STORIES):
    story = Story(story_id, bg)
    for i in range(story.done_rounds(bg), ROUNDS):
        player1, player2 = find_match(story.player_list)
        
        winner, loser = battle(player1, player2, bg.win_rate)

        update_elo(winner, loser)

        for player in story.player_list:
            player.record_elo()
    story.write()

'''
    # print status of each player
    for player in story.player_list:
        print('elo={:4.2f}, win={:2d}, lose={:2d}'\
            .format(player.elo, player.win, player.lose))

    # plot data
    for player in story.player_list:
        plt.plot(player.elo_record)
        #plt.plot(SMA(player.elo_record))
        plt.annotate(np.mean(bg.win_rate[player.id]), xy=(ROUNDS, player.elo_record[-1]))

    # plot label & title.
    params = 'population:{}, game:{}'.format(bg.rules.population, bg.rules.game_name)
    plt.title(params)
    plt.xlabel('rounds')
    plt.ylabel('elo')
    plt.show()
'''


if __name__ == '__main__':
    main()
