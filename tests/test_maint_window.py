"""
Unit tests for Maintenance Windows


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.maintenance_window import MaintenanceWindow, Weekdays
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class MaintTests(BaseTests):

    def test_00_test_object(self):
        data = {'dayOfWeek': 5, 'hourOfDay': 12, 'numberOfDeferrals': 1, 'startASAP': False}

        out = MaintenanceWindow(Weekdays.FRIDAY, 12, 1, False)
        self.assertEquals(out.dayOfWeek.value, 5)
        self.assertEquals(out.as_dict(), data)

        out2 = MaintenanceWindow.from_dict(data)

        self.assertEquals(out2.dayOfWeek, Weekdays.FRIDAY)

    test_00_test_object.basic = True

    def test_01_get_maint_window(self):
        # Test as Object
        output = self.a.MaintenanceWindows._get_maint_window()
        self.assertEquals(type(output), MaintenanceWindow)
        self.assertEquals(type(output.dayOfWeek), Weekdays)
        output2 = self.a.MaintenanceWindows._get_maint_window(as_obj=False)
        self.assertEquals(type(output2), dict)

        output = self.a.MaintenanceWindows.current_config
        self.assertEquals(type(output), MaintenanceWindow)
        self.assertEquals(type(output.dayOfWeek), Weekdays)

    test_01_get_maint_window.basic = True
