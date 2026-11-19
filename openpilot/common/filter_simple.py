import numpy as np


class FirstOrderFilter:
  def __init__(self, x0, rc, dt, initialized=True):
    self.x = float(x0) if np.isfinite(x0) else 0.0
    self.dt = max(0.0, float(dt)) if np.isfinite(dt) else 0.0
    self.update_alpha(rc)
    self.initialized = bool(initialized) and np.isfinite(x0)

  def update_alpha(self, rc):
    if not np.isfinite(rc):
      self.alpha = 0.0
      return
    rc_clamped = max(0.0, float(rc))
    denom = rc_clamped + self.dt
    self.alpha = min(1.0, max(0.0, (self.dt / denom) if denom > 0 else 1.0))

  def update(self, x):
    if not np.isfinite(x):
      return self.x
    if self.initialized and np.isfinite(self.x):
      self.x = (1. - self.alpha) * self.x + self.alpha * float(x)
    else:
      self.initialized = True
      self.x = float(x)
    return self.x

  def reset(self, x0=0.0):
    self.x = float(x0) if np.isfinite(x0) else 0.0
    self.initialized = np.isfinite(x0)


class BounceFilter(FirstOrderFilter):
  def __init__(self, x0, rc, dt, initialized=True, bounce=2):
    self.velocity = FirstOrderFilter(0.0, 0.15, dt)
    self.bounce = float(bounce) if np.isfinite(bounce) else 2.0
    super().__init__(x0, rc, dt, initialized)

  def update(self, x):
    if not np.isfinite(x):
      return self.x
    super().update(x)
    scale = self.dt / (1.0 / 60.0) if self.dt > 0 else 1.0  # tuned at 60 fps
    self.velocity.x += (x - self.x) * self.bounce * scale * self.dt
    self.velocity.update(0.0)
    if not np.isfinite(self.velocity.x) or abs(self.velocity.x) < 1e-3:
      self.velocity.x = 0.0
    self.x += self.velocity.x
    if not np.isfinite(self.x):
      self.x = float(x)
    return self.x

  def reset(self, x0=0.0):
    super().reset(x0)
    self.velocity.reset(0.0)


class SlewRateLimiter:
  def __init__(self, x0=0.0, max_up_rate=float('inf'), max_down_rate=None, dt=0.01):
    self.x = float(x0) if np.isfinite(x0) else 0.0
    self.max_up_rate = max(0.0, float(max_up_rate)) if np.isfinite(max_up_rate) else float('inf')
    if max_down_rate is None:
      self.max_down_rate = self.max_up_rate
    else:
      self.max_down_rate = max(0.0, float(max_down_rate)) if np.isfinite(max_down_rate) else float('inf')
    self.dt = max(0.0, float(dt)) if np.isfinite(dt) else 0.01

  def update(self, target, dt=None):
    if not np.isfinite(target):
      return self.x
    delta_t = self.dt if dt is None or not np.isfinite(dt) or dt <= 0 else float(dt)
    delta = float(target) - self.x

    max_up = self.max_up_rate * delta_t
    max_down = self.max_down_rate * delta_t

    if delta > max_up:
      self.x += max_up
    elif delta < -max_down:
      self.x -= max_down
    else:
      self.x = float(target)
    return self.x

  def reset(self, x0=0.0):
    self.x = float(x0) if np.isfinite(x0) else 0.0


class JerkLimiter:
  def __init__(self, x0=0.0, max_accel=float('inf'), max_jerk=float('inf'), dt=0.01):
    self.x = float(x0) if np.isfinite(x0) else 0.0
    self.v = 0.0  # first derivative (velocity / rate of change)
    self.max_accel = max(0.0, float(max_accel)) if np.isfinite(max_accel) else float('inf')
    self.max_jerk = max(0.0, float(max_jerk)) if np.isfinite(max_jerk) else float('inf')
    self.dt = max(1e-4, float(dt)) if np.isfinite(dt) and dt > 0 else 0.01

  def update(self, target_x, dt=None):
    if not np.isfinite(target_x):
      return self.x
    delta_t = self.dt if dt is None or not np.isfinite(dt) or dt <= 0 else float(dt)

    target_v = (float(target_x) - self.x) / delta_t
    max_dv = self.max_accel * delta_t
    dv = target_v - self.v
    if dv > max_dv:
      self.v += max_dv
    elif dv < -max_dv:
      self.v -= max_dv
    else:
      self.v = target_v

    self.x += self.v * delta_t
    if not np.isfinite(self.x):
      self.x = float(target_x)
      self.v = 0.0
    return self.x

  def reset(self, x0=0.0, v0=0.0):
    self.x = float(x0) if np.isfinite(x0) else 0.0
    self.v = float(v0) if np.isfinite(v0) else 0.0

