import numpy as np


class FirstOrderFilter:
  def __init__(self, x0, rc, dt, initialized=True):
    self.x = float(x0)
    self.dt = float(dt)
    self.update_alpha(rc)
    self.initialized = initialized

  def update_alpha(self, rc):
    denom = float(rc) + self.dt
    self.alpha = (self.dt / denom) if denom > 0 else 1.0

  def update(self, x):
    if not np.isfinite(x):
      return self.x
    if self.initialized:
      self.x = (1. - self.alpha) * self.x + self.alpha * float(x)
    else:
      self.initialized = True
      self.x = float(x)
    return self.x


class BounceFilter(FirstOrderFilter):
  def __init__(self, x0, rc, dt, initialized=True, bounce=2):
    self.velocity = FirstOrderFilter(0.0, 0.15, dt)
    self.bounce = bounce
    super().__init__(x0, rc, dt, initialized)

  def update(self, x):
    if not np.isfinite(x):
      return self.x
    super().update(x)
    scale = self.dt / (1.0 / 60.0)  # tuned at 60 fps
    self.velocity.x += (x - self.x) * self.bounce * scale * self.dt
    self.velocity.update(0.0)
    if abs(self.velocity.x) < 1e-3:
      self.velocity.x = 0.0
    self.x += self.velocity.x
    return self.x
