import telethon
import pickle
import math

import matplotlib.pyplot as plt
import chatwars_utils as utils

HISTORY_PATH = 'all_history.pickle'

def main():
  with open(HISTORY_PATH, 'rb') as f:
    messages = pickle.load(f)
  print('Messages loaded: %d' % len(messages) )
  datapoints = []
  for m in messages:
    parsed = utils.ChatWarsMessage(m)
    if parsed.msg_type == 'STATUS':
      datapoints.append({
          'date': parsed.date,
          'xp': parsed.params['xp'],
          'level': parsed.params['level'],
          'logxp': math.log(1+parsed.params['xp'])
      })
  print('Total datapoints: ', len(datapoints))
  levelups = []
  min_xp = min([dp['xp'] for dp in datapoints])
  max_xp = max([dp['xp'] for dp in datapoints])
  margin = (max_xp - min_xp) / 20
  min_xp -= margin
  max_xp += margin
  plt.ylim(min_xp, max_xp)
  for i in range(len(datapoints)-1):
    if datapoints[i]['level'] != datapoints[i+1]['level']:
      levelups.append(datapoints[i])
  def extr(arr, field):
    return list(map(lambda p: p[field], arr))
  plt.plot_date(
      extr(datapoints, 'date'),
      extr(datapoints, 'xp'),
      'r-',
      xdate=True)
  plt.plot_date(
      extr(levelups, 'date'),
      extr(levelups, 'xp'),
      'bo',
      xdate=True)
  for dp in levelups:
    plt.axvline(x=dp['date'], ymin=0, ymax=(dp['xp']-min_xp) / (max_xp-min_xp),
                color='black')
  plt.ylabel('XP')
  plt.xlabel('Date')
  plt.title('alctech progress')
  '''right = plt.twinx()
  right.plot_date(
      extr(datapoints, 'date'),
      extr(datapoints, 'logxp'),
      'c-',
      xdate=True)
  plt.ylabel('log XP')'''
  plt.show()

if __name__ == '__main__':
  main()
