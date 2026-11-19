import unittest
import numpy as np

from openpilot.common.pid import PIDController
from openpilot.common.filter_simple import FirstOrderFilter, BounceFilter, SlewRateLimiter, JerkLimiter
from openpilot.common.stat_live import RunningStat, RunningStatFilter
from openpilot.common.simple_kalman import KF1D, get_kalman_gain
from openpilot.common.utils import MovingAverage


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

    # NaN limits fallback safely
    pid.set_limits(float('nan'), float('nan'))
    self.assertTrue(np.isfinite(pid.pos_limit))
    self.assertTrue(np.isfinite(pid.neg_limit))

  def test_pid_speed_and_feedforward_nan_safety(self):
    pid = PIDController(k_p=1.0, k_i=0.5, rate=100)
    # NaN speed and feedforward must not poison calculation
    out = pid.update(error=1.0, speed=float('nan'), feedforward=float('nan'))
    self.assertTrue(np.isfinite(out))
    self.assertFalse(np.isnan(pid.control))


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

  def test_filter_reset(self):
    filt = FirstOrderFilter(x0=10.0, rc=0.1, dt=0.01)
    filt.update(20.0)
    filt.reset(0.0)
    self.assertEqual(filt.x, 0.0)
    self.assertTrue(filt.initialized)

    bf = BounceFilter(x0=5.0, rc=0.1, dt=0.01)
    bf.update(15.0)
    bf.reset(1.0)
    self.assertEqual(bf.x, 1.0)
    self.assertEqual(bf.velocity.x, 0.0)


class TestRunningStat(unittest.TestCase):
  def test_running_stat_welford_accuracy(self):
    stat = RunningStat()
    data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    for x in data:
      stat.push_data(x)
    self.assertAlmostEqual(stat.mean(), 5.0)
    self.assertAlmostEqual(stat.variance(), 4.57142857)
    self.assertAlmostEqual(stat.std(), np.sqrt(4.57142857))

  def test_running_stat_nan_and_inf_guards(self):
    stat = RunningStat()
    stat.push_data(10.0)
    stat.push_data(20.0)
    mean_before = stat.mean()
    var_before = stat.variance()

    # Pushing NaN or Inf should be ignored and not poison the stats
    stat.push_data(float('nan'))
    stat.push_data(float('inf'))
    stat.push_data(float('-inf'))
    self.assertEqual(stat.mean(), mean_before)
    self.assertEqual(stat.variance(), var_before)
    self.assertEqual(stat.n, 2)

  def test_running_stat_filter_nan_safety(self):
    rf = RunningStatFilter()
    rf.push_and_update(10.0)
    rf.push_and_update(float('nan'))
    self.assertEqual(rf.raw_stat.mean(), 10.0)
    self.assertEqual(rf.raw_stat.n, 1)

  def test_running_stat_extrema_and_count(self):
    stat = RunningStat()
    self.assertEqual(stat.count, 0)
    self.assertEqual(stat.min(), 0.0)
    self.assertEqual(stat.max(), 0.0)

    stat.push_data(5.0)
    stat.push_data(12.0)
    stat.push_data(-3.0)
    stat.push_data(8.0)
    self.assertEqual(stat.count, 4)
    self.assertEqual(stat.min(), -3.0)
    self.assertEqual(stat.max(), 12.0)

    stat.reset()
    self.assertEqual(stat.count, 0)
    self.assertEqual(stat.min(), 0.0)
    self.assertEqual(stat.max(), 0.0)


class TestKalmanFilter(unittest.TestCase):
  def test_kf1d_guards_and_reset(self):
    kf = KF1D(
      x0=[[0.0], [0.0]],
      A=[[1.0, 0.01], [0.0, 1.0]],
      C=[1.0, 0.0],
      K=[[0.1], [0.2]],
    )
    kf.update(10.0)
    self.assertNotEqual(kf.x, [[0.0], [0.0]])

    # Invalid set_x calls must not crash or poison state
    kf.set_x([[float('nan')], [float('inf')]])
    self.assertFalse(np.isnan(kf.x[0][0]))
    self.assertFalse(np.isinf(kf.x[1][0]))

    kf.set_x([])  # empty
    self.assertFalse(np.isnan(kf.x[0][0]))

    # Reset restores zero state
    kf.reset()
    self.assertEqual(kf.x, [[0.0], [0.0]])



class TestMovingAverage(unittest.TestCase):
  def test_moving_average_accuracy_and_window(self):
    ma = MovingAverage(window_size=3)
    ma.add_value(10.0)
    self.assertEqual(ma.get_average(), 10.0)
    ma.add_value(20.0)
    self.assertEqual(ma.get_average(), 15.0)
    ma.add_value(30.0)
    self.assertEqual(ma.get_average(), 20.0)
    ma.add_value(40.0)
    # window holds 20, 30, 40 -> avg 30
    self.assertEqual(ma.get_average(), 30.0)

  def test_moving_average_nan_and_bounds_guards(self):
    # Minimum window size clamped to >= 1
    ma_zero = MovingAverage(window_size=0)
    self.assertEqual(ma_zero.window_size, 1)
    ma_zero.add_value(5.0)
    self.assertEqual(ma_zero.get_average(), 5.0)

    # Adding NaN or Inf does not corrupt sum or average
    ma = MovingAverage(window_size=2)
    ma.add_value(10.0)
    ma.add_value(float('nan'))
    ma.add_value(float('inf'))
    self.assertEqual(ma.get_average(), 10.0)
    self.assertEqual(ma.count, 1)

  def test_filter_alpha_bounds_and_running_stat_trackable(self):
    # Alpha must be clamped strictly within [0.0, 1.0] even with negative rc
    filt = FirstOrderFilter(x0=10.0, rc=-0.05, dt=0.01)
    self.assertGreaterEqual(filt.alpha, 0.0)
    self.assertLessEqual(filt.alpha, 1.0)

    # RunningStat max_trackable >= 0 clamped to >= 1
    stat = RunningStat(max_trackable=0)
    self.assertEqual(stat.max_trackable, 1)
    stat.push_data(5.0)
    self.assertEqual(stat.mean(), 5.0)

  def test_bounce_filter_and_moving_average_reset(self):
    bf = BounceFilter(x0=0.0, rc=0.1, dt=0.01, bounce=float('nan'))
    self.assertEqual(bf.bounce, 2.0)
    out = bf.update(10.0)
    self.assertTrue(np.isfinite(out))

    ma = MovingAverage(window_size=3)
    ma.add_value(1.0)
    ma.add_value(2.0)
    self.assertEqual(ma.count, 2)
    ma.reset()
    self.assertEqual(ma.count, 0)
    self.assertTrue(np.isnan(ma.get_average()))

  def test_slew_rate_limiter_bounds_and_nan(self):
    # Slew rate max 10.0 units/sec, dt=0.1s -> max change 1.0 unit per step
    slew = SlewRateLimiter(x0=0.0, max_up_rate=10.0, max_down_rate=5.0, dt=0.1)

    # Step from 0 to 10 -> clamped to +1.0
    val = slew.update(10.0)
    self.assertAlmostEqual(val, 1.0)

    # Step down to -10 -> clamped to -0.5 (max_down = 5.0 * 0.1)
    val = slew.update(-10.0)
    self.assertAlmostEqual(val, 0.5)

    # NaN safety: maintains current value
    val = slew.update(float('nan'))
    self.assertAlmostEqual(val, 0.5)

    # Reset
    slew.reset(0.0)
    self.assertEqual(slew.x, 0.0)

  def test_jerk_limiter_acceleration_clamping(self):
    # Jerk limiter with max_accel = 5.0 units/s^2, dt = 0.1s
    jerk = JerkLimiter(x0=0.0, max_accel=5.0, dt=0.1)

    # Step to target 100
    val = jerk.update(100.0)
    self.assertTrue(np.isfinite(val))
    self.assertLess(val, 10.0)  # Acceleration prevents immediate jump

    # NaN safety
    val = jerk.update(float('inf'))
    self.assertTrue(np.isfinite(val))


if __name__ == "__main__":
  unittest.main()
