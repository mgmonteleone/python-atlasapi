"""
Events NoseTests


"""

from atlasapi.atlas import Atlas
from pprint import pprint
from os import environ, getenv
from atlasapi import events
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from json import dumps
from tests import BaseTests
import logging
from time import sleep
from datetime import datetime, timedelta, timezone

USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)


if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))


verbose_logger = logging.getLogger('verbose_logger')


class EventsTests(BaseTests):

    def test_00_All_Events(self):
        out = self.a.Events.all
        self.assertIsInstance(out, list)
        self.assertIsInstance(out[0], events._AtlasBaseEvent)
        self.assertIsInstance(out[10], events._AtlasBaseEvent)
        verbose_logger.warning(f'The count of all events is {len(out)}')
    test_00_All_Events.basic = False

    def test_01_get_project_events_since(self):
        test_datetime = datetime.utcnow() - timedelta(hours=12)
        verbose_logger.info(f'Events Since {test_datetime.isoformat()}')
        out = self.a.Events._get_all_project_events(iterable=True,since_datetime=test_datetime)
        verbose_logger.warning(f'The count of since events is {len(out)}')
        self.assertIsInstance(out, list)
        for each in out:
            self.assertIsInstance(each, events._AtlasBaseEvent)

    test_01_get_project_events_since.basic = False

    def test_02_since(self):
        test_datetime = datetime.utcnow() - timedelta(hours=12)
        verbose_logger.info(f'Events Since (public) {test_datetime.isoformat()}')
        out = self.a.Events.since(test_datetime)
        verbose_logger.warning(f'The count of since events is {len(out)}')
        self.assertIsInstance(out, list)
        for each in out:
            self.assertIsInstance(each, events._AtlasBaseEvent)

    test_02_since.basic = False

    def test_03_atlas(self):
        self.assertIsInstance(self.a,Atlas)


