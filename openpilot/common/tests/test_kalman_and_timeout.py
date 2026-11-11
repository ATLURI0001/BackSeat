import math
import numpy as np
import pytest
from openpilot.common.simple_kalman import KF1D, get_kalman_gain
from openpilot.common.timeout import Timeout


def test_kf1d_nan_inf_state_preservation():
  kf = KF1D(
    x0=[[2.0], [0.5]],
    A=[[1.0, 0.01], [0.0, 1.0]],
    C=[1.0, 0.0],
    K=[[0.1], [0.2]],
  )
  # Normal update converges cleanly
  state_ok = kf.update(5.0)
  assert all(math.isfinite(v) for v in state_ok)

  # NaN and Inf measurements must not corrupt filter state
  assert kf.update(float("nan")) == state_ok
  assert kf.update(float("inf")) == state_ok
  assert kf.update(float("-inf")) == state_ok
  assert kf.update("invalid") == state_ok


def test_get_kalman_gain_singular_and_invalid_iterations():
  A = np.eye(2)
  C = np.array([[1.0, 0.0]])
  Q = np.zeros((2, 2))
  R = np.zeros((1, 1))  # singular S = 0

  # Falls back to pseudoinverse without raising LinAlgError
  gain = get_kalman_gain(0.01, A, C, Q, R, iterations=5)
  assert gain.shape == (2, 1)

  with pytest.raises(ValueError, match="non-negative"):
    get_kalman_gain(0.01, A, C, Q, R, iterations=-1)


def test_timeout_validation_and_context_safety():
  with pytest.raises(ValueError, match="positive finite number"):
    Timeout(0)
  with pytest.raises(ValueError, match="positive finite number"):
    Timeout(-1.5)
  with pytest.raises(ValueError, match="positive finite number"):
    Timeout(float("nan"))

  # Entering/exiting Timeout safely executes body across Windows and POSIX
  with Timeout(0.25) as t:
    assert t.seconds == 0.25
