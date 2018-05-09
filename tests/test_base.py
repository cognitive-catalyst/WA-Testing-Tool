from unittest import TestCase
import os
import time


class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up the test out location
    """
    @classmethod
    def setUpClass(cls):
        cls.test_dir = \
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data1', 'test_{}'.format(time.strftime('%Y%m%d-%H%M%S')))

        if not os.path.exists(cls.test_dir):
            os.makedirs(cls.test_dir)
