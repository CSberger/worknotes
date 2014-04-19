from unittest import TestCase

__author__ = 'Chris'
from main import Config
import datetime


class TestConfig(TestCase):
    def setUp(self):
        self.config = Config()

    def test_append_to_log(self):
        self.fail()

    def test_get_log_filename_for_date(self):
        test_datetime = datetime.datetime(2014, 4, 17)
        result_filename = self.config.get_log_filename_for_date(test_datetime, 'c:/')
        self.assertEquals('c:/2014-04-17.log', result_filename)


    def test_get_last_log_line_for_today(self):
        self.fail()
    def test_get_last_log_line_for_file(self):
        last_line = self.config.get_last_log_line_for_file('2013_10_31.log')
        self.assertEquals(u'After timer implemented', last_line)



