# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import unittest

from RestAuthClient.common import RestAuthConnection


mime_type = os.environ.get('MIME', 'application/json')

class RestAuthClientTestCase(unittest.TestCase):
    conn = RestAuthConnection('http://[::1]:8000', 'example.com', 'nopass',
                              content_handler=mime_type)
