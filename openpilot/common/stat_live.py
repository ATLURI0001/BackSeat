import numpy as np

class RunningStat:
  # tracks realtime mean and standard deviation without storing any data
  def __init__(self, priors=None, max_trackable=-1):
    self.max_trackable = max(1, int(max_trackable)) if max_trackable >= 0 else -1
    if priors is not None:
      # initialize from history
      self.M = float(priors[0]) if np.isfinite(priors[0]) else 0.
      self.S = max(0., float(priors[1])) if np.isfinite(priors[1]) else 0.
      self.n = max(0, int(priors[2]))
      self.M_last = self.M
      self.S_last = self.S
    else:
      self.reset()

  def reset(self):
    self.M = 0.
    self.S = 0.
    self.M_last = 0.
    self.S_last = 0.
    self.n = 0

  def push_data(self, new_data):
    if not np.isfinite(new_data):
      return
    # short term memory hack
    if self.max_trackable < 0 or self.n < self.max_trackable:
      self.n += 1
    if self.n == 0:
      self.M_last = float(new_data)
      self.M = self.M_last
      self.S_last = 0.
    else:
      self.M = self.M_last + (new_data - self.M_last) / self.n
      self.S = max(0., self.S_last + (new_data - self.M_last) * (new_data - self.M))
      self.M_last = self.M
      self.S_last = self.S

  def mean(self):
    return self.M

  def variance(self):
    if self.n >= 2:
      return max(0., self.S / (self.n - 1.))
    else:
      return 0.

  def std(self):
    return float(np.sqrt(self.variance()))

class RunningStatFilter:
  def __init__(self, raw_priors=None, filtered_priors=None, max_trackable=-1):
    self.raw_stat = RunningStat(raw_priors, -1)
    self.filtered_stat = RunningStat(filtered_priors, max_trackable)

  def reset(self):
    self.raw_stat.reset()
    self.filtered_stat.reset()

  def push_and_update(self, new_data):
    if not np.isfinite(new_data):
      return
    _std_last = self.raw_stat.std()
    self.raw_stat.push_data(new_data)
    _delta_std = self.raw_stat.std() - _std_last
    if _delta_std <= 0:
      self.filtered_stat.push_data(new_data)
    else:
      pass
      # self.filtered_stat.push_data(self.filtered_stat.mean())

# class SequentialBayesian():
