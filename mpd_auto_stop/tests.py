#!/usr/bin/env python

from __future__ import absolute_import
import threading
import datetime
import unittest
import time
import mpd_auto_stop as mas

class ArgparseTest(unittest.TestCase):
  def test_with_valid_host(self):
    args = ["--host", "localhost"]
    args = mas.parse_args(args)

    self.assertEqual(args.host, "localhost")

    args = ["-a", "localhost"]
    args = mas.parse_args(args)

    self.assertEqual(args.host, "localhost")
  
  def test_with_empty_host(self):
    args = ["--host"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

    args = ["-a"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

  def test_with_valid_port(self):
    args = ["--port", "9090"]
    args = mas.parse_args(args)

    self.assertEqual(args.port, 9090)

    args = ["-p", "9090"]
    args = mas.parse_args(args)

    self.assertEqual(args.port, 9090)

  def test_with_alpanumeric_port(self):
    args = ["--port", "a9090"]

    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

    args = ["-p", "a9090"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)
  
  def test_with_empty_port(self):
    args = ["--port"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

    args = ["-p"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

  def test_with_valid_mpd_host(self):
    args = ["--mpd-host", "localhost"]
    args = mas.parse_args(args)

    self.assertEqual(args.mpd_host, "localhost")

    args = ["-mh", "localhost"]
    args = mas.parse_args(args)

    self.assertEqual(args.mpd_host, "localhost")
  
  def test_with_empty_mpd_host(self):
    args = ["--mpd-host"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

    args = ["-mp"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

  def test_with_valid_mpd_port(self):
    args = ["--mpd-port", "9090"]
    args = mas.parse_args(args)

    self.assertEqual(args.mpd_port, 9090)

    args = ["-mp", "9090"]
    args = mas.parse_args(args)

    self.assertEqual(args.mpd_port, 9090)

  def test_with_alpanumeric_mpd_port(self):
    args = ["--mpd-port", "a9090"]

    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

    args = ["-mp", "a9090"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)
  
  def test_with_empty_mpd_port(self):
    args = ["--mpd-port"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

    args = ["-mp"]
    
    with self.assertRaises(SystemExit):
      args = mas.parse_args(args)

class UtilsTest(unittest.TestCase):
  def test_xstr_with_empty_text(self):
    self.assertEqual(mas.xstr(""), "")
  
  def test_xstr_with_non_empty_text(self):
    self.assertEqual(mas.xstr("mas"), "mas")

  def test_xstr_with_null(self):
    self.assertEqual(mas.xstr(None), "")

  def test_xstr_with_number(self):
    self.assertEqual(mas.xstr(100), "100")

  def test_xint_with_empty_text(self):
    self.assertEqual(mas.xint(""), 0)

  def test_xint_with_invalid_text(self):
    self.assertEqual(mas.xint("mas"), 0)
  
  def test_xint_with_non_empty_text(self):
    self.assertEqual(mas.xint("100"), 100)

  def test_xint_with_null(self):
    self.assertEqual(mas.xint(None), 0)

  def test_xint_with_number(self):
    self.assertEqual(mas.xint(100), 100)

  def test_xfloat_with_empty_text(self):
    self.assertEqual(mas.xfloat(""), 0.0)
  
  def test_xfloat_with_invalid_text(self):
    self.assertEqual(mas.xint("mas"), 0.0)
  
  def test_xfloat_with_non_empty_text(self):
    self.assertEqual(mas.xint("100"), 100.0)

  def test_xfloat_with_null(self):
    self.assertEqual(mas.xint(None), 0.0)

  def test_xfloat_with_number(self):
    self.assertEqual(mas.xint(100), 100.0)

class TestTimer(unittest.TestCase):
  def setUp(self):
    self.timer = mas.Timer()
    self.timer._worker = lambda *args: None
    self.timer.start("100s")

  def tearDown(self):
    self.timer.stop()

  def test_parse_duration_with_valid_second_duration(self):
    duration = "1000s"
    duration = self.timer._parse_duration(duration)
    
    self.assertEqual(duration, 1000.0)

  def test_parse_duration_with_valid_hour_duration(self):
    duration = "1.5h"
    duration = self.timer._parse_duration(duration)
    
    self.assertEqual(duration, 5400.0)

  def test_parse_duration_with_valid_minute_duration(self):
    duration = "30m"
    duration = self.timer._parse_duration(duration)

    self.assertEqual(duration, 1800.0)

  def test_parse_duration_with_invalid_duration(self):
    duration = "30ms"

    with self.assertRaises(ValueError):
      self.timer._parse_duration(duration)

  def test_stop_timer_with_non_empty_timer(self):
    self.timer._stop_timer()
    
    self.assertIsNone(self.timer._timer)

  def test_stop_timer_with_empty_timer(self):
    self.timer._stop_timer()
    
    self.assertIsNone(self.timer._timer)

  def test_get_remaining_time_with_valid_time(self):
    remaining_time = self.timer._get_remaining_time()

    self.assertTrue(99.0 < remaining_time < 101.0, "Expected value between 99.0 and 101.0, got {0}".format(remaining_time))

  def test_get_status_with_timer_started(self):
    result = self.timer.get_status()
    status = result["status"]
    remaining_time = result.get("remaining_time", None)

    self.assertEqual(status, "started")
    self.assertIsNotNone(remaining_time)

  def test_get_status_with_timer_stopped(self):
    self.timer.stop()

    result = self.timer.get_status()
    status = result["status"]
    remaining_time = result.get("remaining_time", None)

    self.assertEqual(status, "stopped")
    self.assertIsNone(remaining_time, "Expected null, got {0}".format(remaining_time))

  def test_restart_with_timer_started(self):
    time.sleep(2)

    self.timer.restart()

    status = self.timer.status
    remaining_time = self.timer._get_remaining_time()

    self.assertEqual(status, "started")
    self.assertTrue(99.0 < remaining_time < 101.0, "Expected value between 99.0 and 101.0, got {0}".format(remaining_time))

  def test_restart_with_timer_stopped(self):
    self.timer.stop()

    with self.assertRaises(mas.InvalidTimerStateError):
      self.timer.restart()

  def test_extend_with_timer_started(self):
    self.timer.extend("100s")

    status = self.timer.status
    remaining_time = self.timer._get_remaining_time()

    self.assertEqual(status, "started")
    self.assertTrue(199.0 < remaining_time < 201.0, "Expected value between 199.0 and 201.0, got {0}".format(remaining_time))

  def test_extend_with_timer_stopped(self):
    self.timer.stop()

    with self.assertRaises(mas.InvalidTimerStateError):
      self.timer.extend("100s")

if __name__ == "__main__":
  unittest.main()