# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import unittest
from RestAuthClient.error import *
from RestAuthClient.common import RestAuthConnection
from RestAuthClient import restauth_user, group
from RestAuthCommon import error

rest_host = 'http://[::1]:8000'
rest_user = 'vowi'
rest_passwd = 'vowi'

username = "mati \u6110"
password = "mati \u6111"
propKey = "mati \u6112"
propVal = "mati \u6113"

groupname = "group \u6114"


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.conn = RestAuthConnection(rest_host, rest_user, rest_passwd)
        if restauth_user.get_all(self.conn):
            raise RuntimeError("Found leftover users.")

    def tearDown(self):
        for user in restauth_user.get_all(self.conn):
            user.remove()

    def test_createUser(self):
        user = restauth_user.create(self.conn, "mati", "password")

        self.assertEqual([user], restauth_user.get_all(self.conn))
        self.assertEqual(user, restauth_user.get(self.conn, "mati"))

    def test_createUserWithSpace(self):
        user = restauth_user.create(self.conn, "mati space", "password")

        self.assertEqual([user], restauth_user.get_all(self.conn))
        self.assertEqual(user, restauth_user.get(self.conn, "mati space"))

    def test_createUserUnicode(self):
        user = restauth_user.create(self.conn, username, "password")

        self.assertEqual([user], restauth_user.get_all(self.conn))
        self.assertEqual(user, restauth_user.get(self.conn, username))

    def test_createUserWithNoPassword(self):
        user1 = restauth_user.create(self.conn, username)
        self.assertEqual([user1], restauth_user.get_all(self.conn))
        self.assertEqual(user1, restauth_user.get(self.conn, username))
        # check that no password verifies as correct
        self.assertFalse(user1.verify_password(''))
        self.assertFalse(user1.verify_password(None))
        self.assertFalse(user1.verify_password(password))

        # use empty string instead:
        user2 = restauth_user.create(self.conn, username + '1', '')
        self.assertEqual([user1, user2], restauth_user.get_all(self.conn))
        self.assertEqual(user2, restauth_user.get(self.conn, username + '1'))
        # check that no password verifies as correct
        self.assertFalse(user2.verify_password(''))
        self.assertFalse(user2.verify_password(None))
        self.assertFalse(user2.verify_password(password))

    def test_createUserWithProperty(self):
        properties = {propKey: propVal}
        user = restauth_user.create(self.conn, username, password, properties)

        self.assertEqual(user, restauth_user.get(self.conn, username))
        self.assertEqual({propKey: propVal}, user.get_properties())

    def test_createInvalidUser(self):
        args = [self.conn, "foo/bar", "password"]
        self.assertRaises(error.PreconditionFailed,
                          restauth_user.create, *args)

        self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTwice(self):
        user = restauth_user.create(self.conn, "mati", "password")
        try:
            restauth_user.create(self.conn, "mati", "new password")
            self.fail()
        except restauth_user.UserExists as e:
            self.assertEqual([user], restauth_user.get_all(self.conn))
            self.assertTrue(user.verify_password("password"))
            self.assertFalse(user.verify_password("new password"))

    def test_verifyPassword(self):
        user = restauth_user.create(self.conn, username, password)
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password("whatever"))

    def test_verifyPasswordInvalidUser(self):
        user = restauth_user.User(self.conn, username)
        self.assertFalse(user.verify_password(password))

    def test_setPassword(self):
        newpass = "new " + password

        user = restauth_user.create(self.conn, username, password)
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password(newpass))

        user.set_password("new " + password)
        self.assertFalse(user.verify_password(password))
        self.assertTrue(user.verify_password(newpass))

    def test_disableUser(self):
        newpass = "new " + password
        user = restauth_user.create(self.conn, username, password)
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password(newpass))

        user.set_password()
        self.assertFalse(user.verify_password(password))
        self.assertFalse(user.verify_password(newpass))
        self.assertFalse(user.verify_password(''))
        self.assertFalse(user.verify_password(None))

    def test_setPasswordInvalidUser(self):
        user = restauth_user.User(self.conn, username)
        try:
            user.set_password(password)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual(e.get_type(), "user")

    def test_setTooShortPassword(self):
        user = restauth_user.create(self.conn, username, password)
        try:
            user.set_password("x")
            self.fail()
        except error.PreconditionFailed:
            self.assertTrue(user.verify_password(password))
            self.assertFalse(user.verify_password("x"))

    def test_getInvalidUser(self):
        try:
            restauth_user.get(self.conn, "invalid")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_removeUser(self):
        user = restauth_user.create(self.conn, username, password)
        user.remove()

        self.assertEqual([], restauth_user.get_all(self.conn))
        try:
            restauth_user.get(self.conn, username)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_removeInvalidUser(self):
        user = restauth_user.User(self.conn, "invalid")
        try:
            user.remove()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())


class CreateUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = RestAuthConnection(rest_host, rest_user, rest_passwd)

    def test_createUserTest(self):
        self.assertIsNone(restauth_user.create_test(self.conn, username))
        self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTestWithPassword(self):
        self.assertIsNone(restauth_user.create_test(
            self.conn, username, "password"))
        self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTestWithProperties(self):
        self.assertIsNone(restauth_user.create_test(
            self.conn, username, properties={'foo': 'bar'}))
        self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTestWithPasswordAndProperties(self):
        self.assertIsNone(restauth_user.create_test(
            self.conn, username, "password", properties={'foo': 'bar'}))
        self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTestWithTooShortUsername(self):
        try:
            restauth_user.create_test(self.conn, 'a')
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTestWithTooShortPassword(self):
        try:
            restauth_user.create_test(self.conn, username, 'x')
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], restauth_user.get_all(self.conn))

    def test_createUserTestWithInvalidUsername(self):
        try:
            restauth_user.create_test(self.conn, 'foo/bar')
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], restauth_user.get_all(self.conn))

    def test_existingUser(self):
        user = restauth_user.create(self.conn, username)

        try:
            restauth_user.create_test(self.conn, username)
            self.fail()
        except UserExists:
            self.assertEqual([user], restauth_user.get_all(self.conn))
        finally:
            user.remove()


class PropertyTests(unittest.TestCase):
    def setUp(self):
        self.conn = RestAuthConnection(rest_host, rest_user, rest_passwd)
        if restauth_user.get_all(self.conn):
            raise RuntimeError("Found leftover users.")

        self.user = restauth_user.create(self.conn, username, password)

    def tearDown(self):
        for user in restauth_user.get_all(self.conn):
            user.remove()

    def test_createProperty(self):
        self.user.create_property(propKey, propVal)
        self.assertEqual({propKey: propVal}, self.user.get_properties())
        self.assertEqual(propVal, self.user.get_property(propKey))

    def test_createPropertyTwice(self):
        self.user.create_property(propKey, propVal)
        self.assertEqual({propKey: propVal}, self.user.get_properties())
        self.assertEqual(propVal, self.user.get_property(propKey))

        try:
            self.user.create_property(propKey, propVal + "foo")
            self.fail()
        except restauth_user.PropertyExists as e:
            # verify that the prop hasn't changed:
            self.assertEqual({propKey: propVal}, self.user.get_properties())
            self.assertEqual(propVal, self.user.get_property(propKey))

    def test_createInvalidProperty(self):
        try:
            self.user.create_property("foo:bar", propVal + "foo")
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual({}, self.user.get_properties())

    def test_createPropertyWithInvalidUser(self):
        user = restauth_user.User(self.conn, username + " foo")
        try:
            user.create_property(propKey, propVal)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

            # verify that no user was created:
            self.assertNotEqual(user, self.user)
            self.assertEqual([self.user], restauth_user.get_all(self.conn))

    def test_setProperty(self):
        self.assertEqual(None, self.user.set_property(propKey, propVal))
        self.assertEqual({propKey: propVal}, self.user.get_properties())
        self.assertEqual(propVal, self.user.get_property(propKey))

    def test_setPropertyTwice(self):
        newpropVal = propVal + " new"

        self.assertEqual(None, self.user.set_property(propKey, propVal))
        self.assertEqual({propKey: propVal}, self.user.get_properties())
        self.assertEqual(propVal, self.user.get_property(propKey))

        self.assertEqual(propVal, self.user.set_property(propKey, newpropVal))
        self.assertEqual({propKey: newpropVal}, self.user.get_properties())
        self.assertEqual(newpropVal, self.user.get_property(propKey))

    def test_setPropertyWithInvalidUser(self):
        user = restauth_user.User(self.conn, username + " foo")
        try:
            user.set_property(propKey, propVal)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

            # verify that no user was created:
            self.assertNotEqual(user, self.user)
            self.assertEqual([self.user], restauth_user.get_all(self.conn))

    def test_removeProperty(self):
        self.assertEqual(None, self.user.create_property(propKey, propVal))

        self.user.remove_property(propKey)
        self.assertEqual({}, self.user.get_properties())
        try:
            self.user.get_property(propKey)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())

    def test_removeInvalidProperty(self):
        self.user.create_property(propKey, propVal)

        try:
            self.user.remove_property(propKey + " foo")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())
            self.assertEqual([self.user], restauth_user.get_all(self.conn))
            self.assertEqual({propKey: propVal}, self.user.get_properties())
            self.assertEqual(propVal, self.user.get_property(propKey))

    def test_removePropertyWithInvalidUser(self):
        user = restauth_user.User(self.conn, "new user")

        try:
            user.remove_property("foobar")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_removePropertyFromWrongUser(self):
        """
        Purpose of this test is to add a property to one user, and
        verify that deleting it from the *other* user does not delete it
        for the original user.
        """

        user_2 = restauth_user.create(self.conn, "new user", "password")
        self.user.create_property(propKey, propVal)

        try:
            user_2.remove_property(propKey)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())

        self.assertEqual({}, user_2.get_properties())

        self.assertEqual({propKey: propVal}, self.user.get_properties())
        self.assertEqual(propVal, self.user.get_property(propKey))

    def test_getInvalidProperty(self):
        try:
            self.user.get_property("foobar")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())

    def test_getPropertiesInvalidUser(self):
        user = restauth_user.User(self.conn, "foobar")

        try:
            user.get_properties()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())


class SimpleUserGroupTests(unittest.TestCase):
    def setUp(self):
        self.conn = RestAuthConnection(rest_host, rest_user, rest_passwd)
        if restauth_user.get_all(self.conn):
            raise RuntimeError("Found leftover users.")
        if group.get_all(self.conn):
            raise RuntimeError("Found leftover groups.")

        self.user = restauth_user.create(self.conn, username, password)
        self.group = group.create(self.conn, groupname)

    def tearDown(self):
        for user in restauth_user.get_all(self.conn):
            user.remove()
        for grp in group.get_all(self.conn):
            grp.remove()

    def test_addGroup(self):
        self.user.add_group(groupname)
        self.assertEqual([self.group], self.user.get_groups())
        self.assertEqual([self.group], group.get_all(self.conn, self.user))

    def test_inGroup(self):
        self.assertFalse(self.user.in_group(groupname))
        self.user.add_group(groupname)
        self.assertTrue(self.user.in_group(groupname))

    def test_removeGroup(self):
        self.assertFalse(self.user.in_group(groupname))
        self.assertEqual([], self.user.get_groups())

        self.user.add_group(groupname)
        self.assertTrue(self.user.in_group(groupname))
        self.assertEqual([self.group], group.get_all(self.conn, self.user))

        self.user.remove_group(groupname)
        self.assertFalse(self.user.in_group(groupname))
        self.assertEqual([], self.user.get_groups())

    def test_getGroupsInvalidUser(self):
        user = restauth_user.User(self.conn, "foobar")
        try:
            user.get_groups()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())


class CreatePropertyTest(unittest.TestCase):
    def setUp(self):
        self.conn = RestAuthConnection(rest_host, rest_user, rest_passwd)
        self.user = restauth_user.create(self.conn, username, password)

    def tearDown(self):
        self.user.remove()

    def test_createProperty(self):
        self.assertIsNone(self.user.create_property_test(propKey, propVal))
        self.assertEqual({}, self.user.get_properties())

    def test_createExistingProperty(self):
        self.user.create_property(propKey, propVal)

        try:
            self.user.create_property_test(propKey, "bar")
            self.fail()
        except PropertyExists:
            self.assertEqual({propKey: propVal}, self.user.get_properties())
            self.assertEqual(propVal, self.user.get_property(propKey))

    def test_createInvalidProperty(self):
        try:
            self.user.create_property_test("foo:bar", "bar")
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual({}, self.user.get_properties())

    def test_createPropertyForNonExistingUser(self):
        user = restauth_user.User(self.conn, 'foobar')
        try:
            user.create_property_test(propKey, propVal)
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_createPropertyForInvalidUser(self):
        user = restauth_user.User(self.conn, 'foo:bar')
        try:
            user.create_property_test(propKey, propVal)
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())
