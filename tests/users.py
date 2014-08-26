# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from RestAuthClient.error import UserExists
from RestAuthClient.error import PropertyExists
from RestAuthClient.restauth_user import User
from RestAuthClient import group
from RestAuthCommon import error

from .base import RestAuthClientTestCase

rest_host = 'http://[::1]:8000'
rest_user = 'vowi'
rest_passwd = 'vowi'

username = "mati \u6110"
password = "mati \u6111"
propKey = "mati \u6112"
propVal = "mati \u6113"
propKey1 = "mati \u6112"
propVal1 = "mati \u6113"
propKey2 = "mati \u6114"
propVal2 = "mati \u6115"
propKey3 = "mati \u6116"
propVal3 = "mati \u6117"
propKey4 = "mati \u6118"
propVal4 = "mati \u6119"
propKey5 = "mati \u6120"
propVal5 = "mati \u6121"

groupname = "group \u6114"


class PropertyTestMixin(object):
    def assertProperties(self, user=None, **kwargs):
        if user is None:
            user = self.user

        actual = user.get_properties()

        # test and remove any auto-created properties
        self.assertTrue('date joined' in actual)
        actual.pop('date joined')

        self.assertEqual(kwargs, actual)
        for key, value in kwargs.items():
            self.assertEqual(value, user.get_property(key))


class BasicTests(RestAuthClientTestCase, PropertyTestMixin):
    def setUp(self):
        super(BasicTests, self).setUp()
        if User.get_all(self.conn):
            raise RuntimeError("Found leftover users.")

    def tearDown(self):
        for user in User.get_all(self.conn):
            user.remove()

    def test_createUser(self):
        user = User.create(self.conn, "mati", "password")

        self.assertEqual([user], User.get_all(self.conn))
        self.assertEqual(user, User.get(self.conn, "mati"))

    def test_createUserWithSpace(self):
        user = User.create(self.conn, "mati space", "password")

        self.assertEqual([user], User.get_all(self.conn))
        self.assertEqual(user, User.get(self.conn, "mati space"))

    def test_createUserUnicode(self):
        user = User.create(self.conn, username, "password")

        self.assertEqual([user], User.get_all(self.conn))
        self.assertEqual(user, User.get(self.conn, username))

    def test_createUserWithNoPassword(self):
        user1 = User.create(self.conn, username)
        self.assertEqual([user1], User.get_all(self.conn))
        self.assertEqual(user1, User.get(self.conn, username))
        # check that no password verifies as correct
        self.assertFalse(user1.verify_password(''))
        self.assertFalse(user1.verify_password(password))

        # use empty string instead:
        user2 = User.create(self.conn, username + '1', '')
        self.assertEqual([user1, user2], User.get_all(self.conn))
        self.assertEqual(user2, User.get(self.conn, username + '1'))
        # check that no password verifies as correct
        self.assertFalse(user2.verify_password(''))
        self.assertFalse(user2.verify_password(password))

    def test_createUserWithProperty(self):
        properties = {propKey: propVal}
        user = User.create(self.conn, username, password, properties)
        self.assertProperties(user=user, **properties)

    def test_createUserWithInvalidProperties(self):
        properties = {propKey: propVal, 'foo:bar': propVal2}
        args = [self.conn, username, password, properties]
        self.assertRaises(error.PreconditionFailed,
                          User.create, *args)
        self.assertEqual([], User.get_all(self.conn))

    def test_createInvalidUser(self):
        args = [self.conn, "foo/bar", "password"]
        self.assertRaises(error.PreconditionFailed,
                          User.create, *args)

        self.assertEqual([], User.get_all(self.conn))

    def test_createUserTwice(self):
        user = User.create(self.conn, "mati", "password")
        try:
            User.create(self.conn, "mati", "new password")
            self.fail()
        except UserExists:
            self.assertEqual([user], User.get_all(self.conn))
            self.assertTrue(user.verify_password("password"))
            self.assertFalse(user.verify_password("new password"))

    def test_verifyPassword(self):
        user = User.create(self.conn, username, password)
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password("whatever"))

    def test_verifyPasswordInvalidUser(self):
        user = User(self.conn, username)
        self.assertFalse(user.verify_password(password))

    def test_setPassword(self):
        newpass = "new " + password

        user = User.create(self.conn, username, password)
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password(newpass))

        user.set_password("new " + password)
        self.assertFalse(user.verify_password(password))
        self.assertTrue(user.verify_password(newpass))

    def test_disableUser(self):
        newpass = "new " + password
        user = User.create(self.conn, username, password)
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password(newpass))

        user.set_password()
        self.assertFalse(user.verify_password(password))
        self.assertFalse(user.verify_password(newpass))
        self.assertFalse(user.verify_password(''))

    def test_setPasswordInvalidUser(self):
        user = User(self.conn, username)
        try:
            user.set_password(password)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual(e.get_type(), "user")

    def test_setTooShortPassword(self):
        user = User.create(self.conn, username, password)
        try:
            user.set_password("x")
            self.fail()
        except error.PreconditionFailed:
            self.assertTrue(user.verify_password(password))
            self.assertFalse(user.verify_password("x"))

    def test_getInvalidUser(self):
        try:
            User.get(self.conn, "invalid")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_removeUser(self):
        user = User.create(self.conn, username, password)
        user.remove()

        self.assertEqual([], User.get_all(self.conn))
        try:
            User.get(self.conn, username)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_removeInvalidUser(self):
        user = User(self.conn, "invalid")
        try:
            user.remove()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())


class CreateUserTest(RestAuthClientTestCase):
    def test_createUserTest(self):
        self.assertEquals(None, User.create_test(self.conn, username))
        self.assertEqual([], User.get_all(self.conn))

    def test_createUserTestWithPassword(self):
        self.assertEquals(None, User.create_test(
            self.conn, username, "password"))
        self.assertEqual([], User.get_all(self.conn))

    def test_createUserTestWithProperties(self):
        self.assertEquals(None, User.create_test(
            self.conn, username, properties={'foo': 'bar'}))
        self.assertEqual([], User.get_all(self.conn))

    def test_createUserTestWithPasswordAndProperties(self):
        self.assertEquals(None, User.create_test(
            self.conn, username, "password", properties={'foo': 'bar'}))
        self.assertEqual([], User.get_all(self.conn))

    def test_createUserWithInvalidProperties(self):
        properties = {propKey: propVal, 'foo:bar': propVal2}
        args = [self.conn, username, password, properties]
        self.assertRaises(error.PreconditionFailed,
                          User.create, *args)
        self.assertEqual([], User.get_all(self.conn))

    def test_createUserTestWithTooShortUsername(self):
        try:
            User.create_test(self.conn, 'a')
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], User.get_all(self.conn))

    def test_createUserTestWithTooShortPassword(self):
        try:
            User.create_test(self.conn, username, 'x')
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], User.get_all(self.conn))

    def test_createUserTestWithInvalidUsername(self):
        try:
            User.create_test(self.conn, 'foo/bar')
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], User.get_all(self.conn))

    def test_existingUser(self):
        user = User.create(self.conn, username)

        try:
            User.create_test(self.conn, username)
            self.fail()
        except UserExists:
            self.assertEqual([user], User.get_all(self.conn))
        finally:
            user.remove()


class PropertyBaseTests(RestAuthClientTestCase, PropertyTestMixin):
    def setUp(self):
        super(PropertyBaseTests, self).setUp()
        if User.get_all(self.conn):
            raise RuntimeError("Found leftover users.")

        self.user = User.create(self.conn, username, password)

    def tearDown(self):
        for user in User.get_all(self.conn):
            user.remove()


class PropertyTests(PropertyBaseTests):
    def test_createProperty(self):
        self.user.create_property(propKey, propVal)
        self.assertProperties(**{propKey: propVal})

    def test_createPropertyTwice(self):
        self.user.create_property(propKey, propVal)
        self.assertProperties(**{propKey: propVal})

        try:
            self.user.create_property(propKey, propVal + "foo")
            self.fail()
        except PropertyExists:
            # verify that the prop hasn't changed:
            self.assertProperties(**{propKey: propVal})

    def test_createInvalidProperty(self):
        try:
            self.user.create_property("foo:bar", propVal + "foo")
            self.fail()
        except error.PreconditionFailed:
            self.assertProperties(**{})

    def test_createPropertyWithInvalidUser(self):
        user = User(self.conn, username + " foo")
        try:
            user.create_property(propKey, propVal)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

            # verify that no user was created:
            self.assertNotEqual(user, self.user)
            self.assertEqual([self.user], User.get_all(self.conn))

    def test_setProperty(self):
        self.assertEqual(None, self.user.set_property(propKey, propVal))
        self.assertProperties(**{propKey: propVal})

    def test_setPropertyTwice(self):
        newpropVal = propVal + " new"

        self.assertEqual(None, self.user.set_property(propKey, propVal))
        self.assertProperties(**{propKey: propVal})

        self.assertEqual(propVal, self.user.set_property(propKey, newpropVal))
        self.assertProperties(**{propKey: newpropVal})

    def test_setPropertyWithInvalidUser(self):
        user = User(self.conn, username + " foo")
        try:
            user.set_property(propKey, propVal)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

            # verify that no user was created:
            self.assertNotEqual(user, self.user)
            self.assertEqual([self.user], User.get_all(self.conn))

    def test_removeProperty(self):
        self.assertEqual(None, self.user.create_property(propKey, propVal))

        self.user.remove_property(propKey)
        self.assertProperties()
        try:
            self.user.get_property(propKey)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())

    def test_removeInvalidProperty(self):
        self.assertEquals(None, self.user.create_property(propKey, propVal))

        try:
            self.user.remove_property(propKey + " foo")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())
            self.assertEqual([self.user], User.get_all(self.conn))
            self.assertProperties(**{propKey: propVal})

    def test_removePropertyWithInvalidUser(self):
        user = User(self.conn, "new user")

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

        user_2 = User.create(self.conn, "new user", "password")
        self.assertEquals(None, self.user.create_property(propKey, propVal))

        try:
            user_2.remove_property(propKey)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())

        self.assertProperties(user=user_2, **{})

    def test_getInvalidProperty(self):
        try:
            self.user.get_property("foobar")
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("property", e.get_type())

    def test_getPropertiesInvalidUser(self):
        user = User(self.conn, "foobar")

        try:
            user.get_properties()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())


class SetMultiplePropertyTests(PropertyBaseTests):
    def test_setNoProperties(self):
        self.user.set_properties({})
        self.assertProperties(**{})

    def test_setOneProperty(self):
        properties = {propKey1: propVal1}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

        properties = {propKey1: propVal2}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

    def test_setTwoProperties(self):
        properties = {propKey1: propVal1, propKey2: propVal2}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

        properties = {propKey1: propVal2, propKey2: propVal1}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

    def test_setThreeProperties(self):
        properties = {propKey1: propVal1, propKey2: propKey2, propKey3: propKey3}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

        properties = {propKey1: propVal2, propKey2: propKey3, propKey3: propVal1}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

    def test_setInvalidProperty(self):
        properties = {'foo:bar': propVal1}

        try:
            self.user.set_properties(properties)
            self.fail()
        except error.PreconditionFailed:
            self.assertProperties(**{})

        properties = {'foo:bar': propVal1, propKey2: propVal2}

        try:
            self.user.set_properties(properties)
            self.fail()
        except error.PreconditionFailed:
            self.assertProperties(**{})

        good_props = {propKey2: propVal3}
        self.user.set_properties(good_props)

        try:
            self.user.set_properties(properties)
            self.fail()
        except error.PreconditionFailed:
            self.assertProperties(**good_props)

    def test_mixedSetAndCreate(self):
        properties = {propKey1: propVal1}
        self.user.set_properties(properties)
        self.assertProperties(**properties)

        properties[propKey1] = propVal5
        properties[propKey2] = propVal2
        properties[propKey3] = propVal3

        self.user.set_properties(properties)
        self.assertProperties(**properties)


class SimpleUserGroupTests(RestAuthClientTestCase):
    def setUp(self):
        super(SimpleUserGroupTests, self).setUp()
        if User.get_all(self.conn):
            raise RuntimeError("Found leftover users.")
        if group.get_all(self.conn):
            raise RuntimeError("Found leftover groups.")

        self.user = User.create(self.conn, username, password)
        self.group = group.create(self.conn, groupname)

    def tearDown(self):
        for user in User.get_all(self.conn):
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
        user = User(self.conn, "foobar")
        try:
            user.get_groups()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())


class CreatePropertyTest(PropertyBaseTests):
    def test_createProperty(self):
        self.assertEquals(None,
                          self.user.create_property_test(propKey, propVal))
        self.assertProperties(**{})

    def test_createExistingProperty(self):
        self.user.create_property(propKey, propVal)

        try:
            self.user.create_property_test(propKey, "bar")
            self.fail()
        except PropertyExists:
            self.assertProperties(**{propKey: propVal})

    def test_createInvalidProperty(self):
        try:
            self.user.create_property_test("foo:bar", "bar")
            self.fail()
        except error.PreconditionFailed:
            self.assertProperties(**{})

    def test_createPropertyForNonExistingUser(self):
        user = User(self.conn, 'foobar')
        try:
            user.create_property_test(propKey, propVal)
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())

    def test_createPropertyForInvalidUser(self):
        user = User(self.conn, 'foo:bar')
        try:
            user.create_property_test(propKey, propVal)
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())
