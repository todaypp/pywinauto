"""Tests for CalendarWrapper"""
import time
import datetime
import ctypes
import locale
import re
import sys
import os
import unittest
sys.path.append(".")
from pywinauto import win32structures
from pywinauto import win32defines
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python
from pywinauto.sysinfo import is_x64_OS

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

class CalendarWrapperTests(unittest.TestCase):

    """Unit tests for the CalendarWrapperTests class"""
    NO_HOLIDAYS_IN_MONTH = 0

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select(4)
        self.calendar = self.app.Common_Controls_Sample.CalendarWrapper

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.type_keys("%{F4}")

    def test_can_get_current_date_from_calendar(self):
        date = self.calendar.get_current_date()
        self.assert_system_time_is_equal_to_current_date_time(date,datetime.date.today())

    def test_should_throw_runtime_error_when_try_to_get_current_date_from_calendar_if_calendar_state_is_multiselect(self):
        self._set_calendar_state_into_multiselect()
        self.assertRaises(RuntimeError, self.calendar.get_current_date)

    def test_can_set_current_date_in_calendar(self):
        self.calendar.set_current_date(2016, 4, 3, 13)
        self.assert_system_time_is_equal_to_current_date_time(self.calendar.get_current_date(), datetime.date(2016, 4, 13)) 

    def test_should_throw_runtime_error_when_try_to_set_invalid_date(self):
        self.assertRaises(RuntimeError, self.calendar.set_current_date, -2016, -4, -3, -13)

    def test_can_get_calendar_border(self):
        width = self.calendar.get_border()
        self.assertEqual(width, 4)

    def test_can_set_calendar_border(self):
        self.calendar.set_border(6)
        self.assertEqual(self.calendar.get_border(), 6)

    def test_can_get_calendars_count(self):
        count = self.calendar.count()
        self.assertEqual(count, 1)

    def test_can_get_calendars_view(self):
        view = self.calendar.get_view()
        self.assertEqual(view, 0)

    def test_should_throw_runtime_error_when_try_to_set_invalid_view(self):
        self.assertRaises(RuntimeError, self.calendar.set_view, -1)

    def test_can_set_calendars_view_into_month(self):
        self.calendar.set_view(win32defines.MCMV_MONTH)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_MONTH)

    def test_can_set_calendars_view_into_years(self):
        self.calendar.set_view(win32defines.MCMV_YEAR)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_YEAR)

    def test_can_set_calendars_view_into_decade(self):
        self.calendar.set_view(win32defines.MCMV_DECADE)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_DECADE)

    def test_can_set_calendars_view_into_century(self):
        self.calendar.set_view(win32defines.MCMV_CENTURY)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_CENTURY)

    def test_can_set_day_state(self):
        month_states = [self.NO_HOLIDAYS_IN_MONTH, self.NO_HOLIDAYS_IN_MONTH, self.NO_HOLIDAYS_IN_MONTH]
        self._set_calendar_state_to_display_day_states()

        res = self.calendar.set_day_states(month_states)

        self.assertNotEquals(0, res)

    def test_cant_set_day_state_passing_one_month_state(self):
        month_states = [self.NO_HOLIDAYS_IN_MONTH]
        self._set_calendar_state_to_display_day_states()
        self.assertRaises(RuntimeError, self.calendar.set_day_states, month_states)

    def test_can_minimize_rectangle(self):
        expected_rect = self._get_expected_minimized_rectangle()
        rect = self.calendar.calc_min_rectangle(expected_rect.left + 100, expected_rect.top + 100,
                                                expected_rect.right + 100, expected_rect.bottom + 100)
        self.assertEquals(expected_rect, rect)

    def test_can_minimize_rectangle_handle_less_than_zero_values(self):
        expected_rect = self._get_expected_minimized_rectangle()
        rect = self.calendar.calc_min_rectangle(-1, -1, -1, -1)
        self.assertEquals(expected_rect, rect)

    def test_can_determine_calendar_is_hit(self):
        res = self.calendar.do_hit_test(4, 48)
        self.assertEquals(win32defines.MCHT_CALENDAR, res)

    def test_can_determine_calendar_background_is_hit(self):
        res = self.calendar.do_hit_test(4, 48)
        self.assertEquals(win32defines.MCHT_CALENDARBK, res)

    def test_can_determine_date_is_hit(self):
        res = self.calendar.do_hit_test(140, 120)
        self.assertEquals(win32defines.MCHT_CALENDARDATE, res)

    def test_can_determine_next_month_date_is_hit(self):
        res = self.calendar.do_hit_test(140, 130)
        self.assertEquals(win32defines.MCHT_CALENDARDATENEXT, res)

    def test_can_determine_prev_month_date_is_hit(self):
        res = self.calendar.do_hit_test(10, 60)
        self.assertEquals(win32defines.MCHT_CALENDARDATEPREV, res)

    def test_can_determine_nothing_is_hit(self):
        res = self.calendar.do_hit_test(0, 0)
        self.assertEquals(win32defines.MCHT_NOWHERE, res)

    def test_can_determine_top_left_title_corner_is_hit(self):
        res = self.calendar.do_hit_test(10, 10)
        self.assertEquals(win32defines.MCHT_TITLEBTNPREV, res)

    def test_can_determine_title_is_hit(self):
        res = self.calendar.do_hit_test(20, 15)
        self.assertEquals(win32defines.MCHT_TITLE, res)

    def test_can_determine_title_background_is_hit(self):
        res = self.calendar.do_hit_test(20, 15)
        self.assertEquals(win32defines.MCHT_TITLEBK, res)

    def test_can_determine_top_right_title_corner_is_hit(self):
        res = self.calendar.do_hit_test(150, 20)
        self.assertEquals(win32defines.MCHT_TITLEBTNNEXT, res)

    def test_can_determine_today_link_is_hit(self):
        res = self.calendar.do_hit_test(130, 140)
        self.assertEquals(win32defines.MCHT_TODAYLINK, res)

    def test_can_determine_day_abbreviation_is_hit(self):
        res = self.calendar.do_hit_test(30, 40)
        self.assertEquals(win32defines.MCHT_CALENDARDAY, res)

    def test_can_determine_week_number_is_hit(self):
        rect = self.app['Common Controls Sample']['Calendar'].WrapperObject().Rectangle()
        print(rect, rect.width(), rect.height())
        self._set_calendar_state_to_display_week_numbers()
        res = self.calendar.do_hit_test(4, 50)
        self.assertEquals(win32defines.MCHT_CALENDARWEEKNUM, res)

    def assert_system_time_is_equal_to_current_date_time(self,systemTime, now):
        self.assertEqual(systemTime.wYear, now.year)
        self.assertEqual(systemTime.wMonth, now.month)
        self.assertEqual(systemTime.wDay, now.day)

    def _get_expected_minimized_rectangle(self):
        expected_rect = win32structures.RECT()
        expected_rect.left = 0
        expected_rect.top = 0
        expected_rect.right = 162
        expected_rect.bottom = 160
        return expected_rect

    def _set_calendar_state_to_display_day_states(self):
        self.app['Common Controls Sample']['MCS_DAYSTATE'].WrapperObject().Click()

    def _set_calendar_state_to_display_week_numbers(self):
        self.app['Common Controls Sample']['MCS_WEEKNUMBERS'].WrapperObject().Click()

    def _set_calendar_state_into_multiselect(self):
        self.app['Common Controls Sample']['MCS_MULTISELECT'].WrapperObject().Click()         

if __name__ == "__main__":
    unittest.main()
