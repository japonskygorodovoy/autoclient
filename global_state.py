import datetime
from collections import defaultdict

class GlobalState(object):
  def __init__(self):
    self._start = datetime.datetime.now()
    self._metrics = defaultdict(int)
    self._paused = False

  def pause(self):
    self._paused = True

  def resume(self):
    self._paused = False

  def is_paused(self):
    return self._paused

  def inc_metric(self, metric, delta=1):
    self._metrics[metric] += delta

  def format_stats(self):
    result = ['Chatwars Autoclient stats:']
    secs = (datetime.datetime.now() - self._start).total_seconds()
    if secs < 3600:
      uptime_str = '%f mins' % (secs / 60.0)
    elif secs < 3600 * 24:
      uptime_str = '%f hours' % (secs / 3600.0)
    else:
      uptime_str = '%f days' % (secs / 3600.0 / 24.0)
    result.append('Uptime: ' + uptime_str)
    result.append('Paused: ' + str(self._paused))
    for k, v in self._metrics.items():
      result.append('%s = %d' % (k, v))
    return '\n'.join(result)
    
