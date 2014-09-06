# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from RestAuthClient.common import RestAuthConnection
from RestAuthClient.error import HttpException
from RestAuthClient.user import RestAuthUser
from RestAuthCommon import error

from RestAuthCommon.handlers import ContentHandler
from .base import RestAuthClientTestCase

rest_host = 'http://[:1]:8000'
rest_user = 'example.com'
rest_passwd = 'nopass'

# all paths in the restauth specification
paths = [
    '/users/', '/users/foo/', '/users/foo/props/', '/users/foo/props/bar/',
    '/groups/', '/groups/foo/', '/groups/foo/users/',
    '/groups/foo/users/bar/', '/groups/foo/groups/', '/groups/foo/groups/bar/',
    '/test/users/', '/test/users/foo/props/', '/test/groups/'
]


class wrongContentHandler(ContentHandler):
    mime = 'wrong/mime'


class BasicTests(RestAuthClientTestCase):
    """
    Make some tests directly using the connection. The point is that this
    way we can test some code that would otherwise never get tested.
    """

    def test_wrongCredentials(self):
        conn = RestAuthConnection(rest_host, 'wrong', 'credentials')
        for path in paths:
            try:
                conn.get(path)
                self.fail(msg="%s did not require authorization!" % path)
            except error.Unauthorized:
                pass

        conn = RestAuthConnection(rest_host, rest_user, 'credentials')
        for path in paths:
            try:
                conn.get(path)
                self.fail(msg="%s did not verify password!" % path)
            except error.Unauthorized:
                pass

        conn = RestAuthConnection(rest_host, 'wrong', rest_passwd)
        for path in paths:
            try:
                conn.get(path)
                self.fail(msg="%s did not verify service!" % path)
            except error.Unauthorized:
                pass

    def test_wrongHost(self):
        conn = RestAuthConnection('http://[:2]:8003', 'wrong', 'credentials', timeout=1.0)
        try:
            RestAuthUser.get(conn, 'foobar')
            self.fail()
        except HttpException as e:
            e.get_cause()

    def test_set_wrong_content_handler(self):
        try:
            self.conn.set_content_handler('foo/bar')
            self.fail()
        except error.RestAuthRuntimeException:
            pass

        try:
            # set a bullshit-object:
            self.conn.set_content_handler(self.conn)
            self.fail()
        except error.RestAuthRuntimeException:
            pass

    def test_badRequestPost(self):
        try:
            self.conn.post(str(paths[0]), {'bad': 'request'})
            self.fail()
        except error.BadRequest:
            pass

    def test_badRequestPut(self):
        # we need to create it first, otherwise we might get a 404 instead
        user = RestAuthUser.create(self.conn, 'testuser', 'password')
        try:
            self.conn.put(str('/users/testuser/'), {'bad': 'request'})
            self.fail()
        except error.BadRequest:
            pass

        user.remove()

    def test_NotAcceptable(self):
        old = self.conn.content_handler
        self.conn.set_content_handler(wrongContentHandler())

        try:
            self.conn.get('/users/')
            self.fail()
        except error.NotAcceptable:
            pass
        self.conn.set_content_handler(old)

    def test_UnsupportedMediaTypePost(self):
        old = self.conn.content_handler
        self.conn.set_content_handler(wrongContentHandler())

        try:
            self.conn.post('/users/', {'foo': 'bar'})
            self.fail()
        except error.UnsupportedMediaType:
            pass
        self.conn.set_content_handler(old)

    def test_UnsupportedMediaTypePut(self):
        # we need to create it first, otherwise we might get a 404 instead
        old = self.conn.content_handler
        user = RestAuthUser.create(self.conn, 'testuser', 'password')
        self.conn.set_content_handler(wrongContentHandler())

        try:
            self.conn.put('/users/testuser/', {'foo': 'bar'})
            self.fail()
        except error.UnsupportedMediaType:
            pass
        finally:
            user.remove()
        self.conn.set_content_handler(old)

    def test_source_address(self):
        # Real functionality is difficult to test, but at least we can verify that the arg works.
        address = '127.0.0.1'
        conn = RestAuthConnection(rest_host, 'wrong', 'credentials', source_address=address)
        self.assertEqual(address, conn._conn_kwargs['source_address'])

    def test_forbidden(self):
        conn = RestAuthConnection(rest_host, 'example.net', 'nopass')
        try:
            RestAuthUser.get_all(conn)
            self.fail()
        except error.Forbidden:
            pass

    def test_quote(self):
        self.assertEqual(self.conn.quote('foobar'), 'foobar')
        self.assertEqual(self.conn.quote('foo bar'), 'foo%20bar')
        self.assertEqual(self.conn.quote('foo/bar'), 'foo%2Fbar')
        self.assertEqual(self.conn.quote('\u6109'), '%E6%84%89')

        # casts to str in python2:
        self.assertEqual(self.conn.quote(str('foobar')), 'foobar')

    def test_qs(self):
        self.assertEqual(self.conn._sanitize_qs({'foo': 'bar'}), 'foo=bar')
        self.assertEqual(self.conn._sanitize_qs({'foo': 'foo bar'}), 'foo=foo%20bar')
        self.assertEqual(self.conn._sanitize_qs({'foo': 'foo/bar'}), 'foo=foo%2Fbar')
        self.assertEqual(self.conn._sanitize_qs({'foo': '\u6109'}), 'foo=%E6%84%89')

        # casts to str in python2:
        self.assertEqual(self.conn._sanitize_qs({str('foo'): str('bar')}), 'foo=bar')
