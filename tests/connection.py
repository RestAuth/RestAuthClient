# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import unittest
from RestAuthClient.common import RestAuthConnection
from RestAuthClient.error import *
from RestAuthClient import restauth_user
from RestAuthCommon import error

from RestAuthCommon.handlers import ContentHandler

rest_host = 'http://[:1]:8000'
rest_user = 'vowi'
rest_passwd = 'vowi'

# all paths in the restauth specification
paths = [
    '/users/', '/users/foo/', '/users/foo/props/', '/users/foo/props/bar',
    '/groups/', '/groups/foo/', '/groups/foo/users/',
    '/groups/foo/users/bar/', '/groups/foo/groups/', '/groups/foo/groups/bar',
    '/test/users/', '/test/users/foo/props/', '/test/groups/'
]


class wrongContentHandler(ContentHandler):
    mime = 'wrong/mime'


class BasicTests(unittest.TestCase):
    """
    Make some tests directly using the connection. The point is that this
    way we can test some code that would otherwise never get tested.
    """

    def setUp(self):
        self.conn = RestAuthConnection(rest_host, rest_user, rest_passwd)

    def tearDown(self):
        pass

    def test_wrongCredentials(self):
        conn = RestAuthConnection(rest_host, 'wrong', 'credentials')
        for path in paths:
            try:
                conn.get(path)
                self.fail(msg="%s did not require authorization!" % path)
            except error.Unauthorized as e:
                pass

        conn = RestAuthConnection(rest_host, rest_user, 'credentials')
        for path in paths:
            try:
                conn.get(path)
                self.fail(msg="%s did not verify password!" % path)
            except error.Unauthorized as e:
                pass

        conn = RestAuthConnection(rest_host, 'wrong', rest_passwd)
        for path in paths:
            try:
                conn.get(path)
                self.fail(msg="%s did not verify service!" % path)
            except error.Unauthorized as e:
                pass

    def test_wrongHost(self):
        conn = RestAuthConnection('http://[:2]:8003', 'wrong', 'credentials')
        try:
            restauth_user.get(conn, 'foobar')
            self.fail()
        except HttpException as e:
            e.get_cause()

    def test_set_wrong_content_handler(self):
        try:
            self.conn.set_content_handler('foo/bar')
            self.fail()
        except RuntimeError:
            pass

    def test_badRequestPost(self):
        try:
            self.conn.post(paths[0], {'bad': 'request'})
            self.fail()
        except error.BadRequest:
            pass

    def test_badRequestPut(self):
        # we need to create it first, otherwise we might get a 404 instead
        user = restauth_user.create(self.conn, 'testuser', 'password')
        try:
            self.conn.put('/users/testuser/', {'bad': 'request'})
            self.fail()
        except error.BadRequest:
            pass

        user.remove()

    def test_NotAcceptable(self):
        self.conn.set_content_handler(wrongContentHandler())

        try:
            self.conn.get('/users/')
            self.fail()
        except error.NotAcceptable:
            pass

    def test_UnsupportedMediaTypePost(self):
        self.conn.set_content_handler(wrongContentHandler())

        try:
            self.conn.post('/users/', {'foo': 'bar'})
            self.fail()
        except error.UnsupportedMediaType:
            pass

    def test_UnsupportedMediaTypePut(self):
        # we need to create it first, otherwise we might get a 404 instead
        user = restauth_user.create(self.conn, 'testuser', 'password')
        self.conn.set_content_handler(wrongContentHandler())

        try:
            self.conn.put('/users/testuser/', {'foo': 'bar'})
            self.fail()
        except error.UnsupportedMediaType:
            pass
        finally:
            user.remove()
