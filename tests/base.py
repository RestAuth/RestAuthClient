# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import unittest

from RestAuthClient.common import RestAuthConnection


class RestAuthClientTestCase(unittest.TestCase):
    def setUp(self):
        mime_type = os.environ.get('MIME', 'application/json')
        self.conn = RestAuthConnection('http://[::1]:8000', 'example.com', 'nopass',
                                       content_handler=mime_type)
