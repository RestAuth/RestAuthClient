# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import unittest

from RestAuthClient.common import RestAuthConnection

if sys.version_info >= (3, ):
    PY3 = True
else:
    PY3 = False

mime_type = os.environ.get('MIME', 'application/json')


class RestAuthClientTestCase(unittest.TestCase):
    conn = RestAuthConnection('http://[::1]:8000', 'example.com', 'nopass',
                              content_handler=mime_type)

    if PY3 is False:
        assertCountEqual = unittest.TestCase.assertItemsEqual
