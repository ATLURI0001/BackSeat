import math
import signal


class TimeoutException(Exception):
  pass


class Timeout:
  """
  Timeout context manager.
  For example this code will raise a TimeoutException:
  with Timeout(seconds=5, error_msg="Sleep was too long"):
    time.sleep(10)
  """
  def __init__(self, seconds, error_msg=None):
    if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
      raise ValueError(f"seconds must be a positive finite number, got {seconds}")
    if error_msg is None:
      error_msg = f'Timed out after {seconds} seconds'
    self.seconds = float(seconds)
    self.error_msg = error_msg
    self._prev_handler = None
    self._armed = False

  def handle_timeout(self, signume, frame):
    raise TimeoutException(self.error_msg)

  def __enter__(self):
    if hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer"):
      self._prev_handler = signal.signal(signal.SIGALRM, self.handle_timeout)
      signal.setitimer(signal.ITIMER_REAL, self.seconds)
      self._armed = True
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    if self._armed:
      signal.setitimer(signal.ITIMER_REAL, 0.0)
      if self._prev_handler is not None:
        signal.signal(signal.SIGALRM, self._prev_handler)
      self._armed = False
