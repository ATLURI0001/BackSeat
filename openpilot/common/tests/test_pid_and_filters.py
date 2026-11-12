import unittest
import numpy as np

from openpilot.common.pid import PIDController
from openpilot.common.filter_simple import FirstOrderFilter, BounceFilter


class TestPIDController(unittest.TestCase):
  def test_proportional_control(self):
    pid = PIDController(k_p=2.0, k_i=0.0, k_d=0.0, rate=100)
    out = pid.update(error=1.5)
    self.assertAlmostEqual(out, 3.0)

  def test_integral_control_and_windup(self):
    pid = PIDController(k_p=0.0, k_i=10.0, k_d=0.0, pos_limit=5.0, neg_limit=-5.0, rate=100)
    # 100 steps of error=1.0 at rate=100 -> dt=0.01s -> integral would be 10.0 without limit
    for _ in range(100):
      out = pid.update(error=1.0)
    self.assertLessEqual(out, 5.0)
    self.assertAlmostEqual(out, 5.0)

  def test_derivative_control(self):
    pid = PIDController(k_p=0.0, k_i=0.0, k_d=0.5, rate=100)
    out = pid.update(error=0.0, error_rate=4.0)
    self.assertAlmostEqual(out, 2.0)

  def test_nan_and_inf_safety(self):
    pid = PIDController(k_p=1.0, k_i=1.0, rate=100)
    initial_out = pid.update(error=1.0)
    # Feeding NaN should not poison control output
    out_nan = pid.update(error=float('nan'))
    self.assertEqual(out_nan, initial_out)
    self.assertFalse(np.isnan(pid.i))

    # Feeding Inf should not poison control output
    out_inf = pid.update(error=float('inf'))
    self.assertEqual(out_inf, initial_out)
    self.assertFalse(np.isinf(pid.i))

  def test_reversed_limits(self):
    # Pass pos_limit=-10, neg_limit=10, controller should auto-normalize
    pid = PIDController(k_p=1.0, k_i=0.0, pos_limit=-10.0, neg_limit=10.0)
    self.assertEqual(pid.pos_limit, 10.0)
    self.assertEqual(pid.neg_limit, -10.0)


class TestFilters(unittest.TestCase):
  def test_first_order_filter_convergence(self):
    filt = FirstOrderFilter(x0=0.0, rc=0.1, dt=0.01)
    for _ in range(100):
      val = filt.update(10.0)
    self.assertGreater(val, 9.9)

  def test_first_order_filter_nan_safety(self):
    filt = FirstOrderFilter(x0=5.0, rc=0.1, dt=0.01)
    val = filt.update(float('nan'))
    self.assertEqual(val, 5.0)

  def test_bounce_filter_nan_safety(self):
    bfilt = BounceFilter(x0=1.0, rc=0.1, dt=0.01)
    val = bfilt.update(float('nan'))
    self.assertEqual(val, 1.0)

  def test_first_order_filter_recovers_from_nonfinite_initial_state(self):
    filt = FirstOrderFilter(x0=float('nan'), rc=0.1, dt=0.01)
    self.assertFalse(filt.initialized)
    self.assertEqual(filt.update(4.5), 4.5)
    self.assertTrue(filt.initialized)

    neg_dt = FirstOrderFilter(x0=0.0, rc=0.1, dt=-0.05)
    self.assertEqual(neg_dt.dt, 0.0)


if __name__ == "__main__":
  unittest.main()
