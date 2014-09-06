# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from operator import attrgetter

from RestAuthClient.error import GroupExists
from RestAuthClient.user import RestAuthUser
from RestAuthClient.group import RestAuthGroup

from RestAuthCommon import error

from .base import RestAuthClientTestCase

username_1 = "mati 1 \u6110"
username_2 = "mati 2 \u6111"
username_3 = "mati 3 \u6112"

groupname_1 = "group \u7110"
groupname_2 = "group \u7111"
groupname_3 = "group \u7112"


class BasicTests(RestAuthClientTestCase):
    def setUp(self):
        super(BasicTests, self).setUp()

        self.assertEqual([], RestAuthUser.get_all(self.conn, flat=True))
        self.assertEqual([], RestAuthGroup.get_all(self.conn, flat=True))

        self.users = [
            RestAuthUser.create(self.conn, username_1, "foobar"),
            RestAuthUser.create(self.conn, username_2, "foobar"),
            RestAuthUser.create(self.conn, username_3, "foobar"),
        ]

    def tearDown(self):
        """remove everything"""
        for user in RestAuthUser.get_all(self.conn):
            user.remove()
        for grp in RestAuthGroup.get_all(self.conn):
            grp.remove()

    def test_getall_user(self):
        user = self.users[0]

        self.assertEqual(RestAuthGroup.get_all(self.conn, user=user), [])
        self.assertEqual(RestAuthGroup.get_all(self.conn, user=user.name), [])

        grp = RestAuthGroup.create(self.conn, groupname_1)
        grp.add_user(user)

        self.assertEqual(RestAuthGroup.get_all(self.conn, user=user), [grp])
        self.assertEqual(RestAuthGroup.get_all(self.conn, user=user.name), [grp])

    def test_createGroup(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        self.assertEqual([grp], RestAuthGroup.get_all(self.conn))
        self.assertEqual(grp, RestAuthGroup.get(self.conn, groupname_1))

    def test_createGroupTwice(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)

        try:
            RestAuthGroup.create(self.conn, groupname_1)
            self.fail()
        except GroupExists:
            self.assertEqual([grp], RestAuthGroup.get_all(self.conn))
            self.assertEqual(grp, RestAuthGroup.get(self.conn, groupname_1))

    def test_createInvalidGroup(self):
        try:
            RestAuthGroup.create(self.conn, "foo/bar")
            self.fail()
        except error.PreconditionFailed:
            self.assertEqual([], RestAuthGroup.get_all(self.conn))

    def test_addUser(self):
        grp_0 = RestAuthGroup.create(self.conn, groupname_1)
        grp_1 = RestAuthGroup.create(self.conn, groupname_2)
        self.assertEqual([grp_0, grp_1], RestAuthGroup.get_all(self.conn))

        grp_0.add_user(self.users[0])
        grp_1.add_user(self.users[1])
        grp_1.add_user(self.users[2])

        self.assertEqual([self.users[0]], grp_0.get_members())
        self.assertEqual(self.users[1:3], grp_1.get_members())

        self.assertTrue(grp_0.is_member(self.users[0]))
        self.assertFalse(grp_0.is_member(self.users[1]))
        self.assertFalse(grp_0.is_member(self.users[2]))
        self.assertTrue(grp_1.is_member(self.users[1]))
        self.assertTrue(grp_1.is_member(self.users[2]))
        self.assertFalse(grp_1.is_member(self.users[0]))

    def test_addInvalidUser(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        user = RestAuthUser(self.conn, "foobar")

        try:
            grp.add_user(user)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())
            RestAuthUser.get_all(self.conn)
            self.assertEqual(self.users, RestAuthUser.get_all(self.conn))

    def test_addUserToInvalidGroup(self):
        grp = RestAuthGroup(self.conn, groupname_1)
        try:
            grp.add_user(self.users[0])
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())
            self.assertEqual([], RestAuthGroup.get_all(self.conn))

    def test_isMember(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        self.assertFalse(grp.is_member(username_1))

        grp.add_user(username_1)

        self.assertTrue(grp.is_member(username_1))

    def test_isMemberInvalidGroup(self):
        grp = RestAuthGroup(self.conn, groupname_1)

        try:
            grp.is_member(username_1)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())

    def test_getMembersFlat(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        self.assertEqual(grp.get_members(flat=True), [])

        grp.add_user(self.users[0])
        self.assertEqual(grp.get_members(flat=True), [self.users[0].name])

        grp.add_user(self.users[1])
        self.assertEqual(sorted(grp.get_members(flat=True)),
                         sorted([self.users[0].name, self.users[1].name]))

    def test_removeUser(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        grp.add_user(self.users[0])
        grp.add_user(self.users[1])
        self.assertEqual(sorted(self.users[0:2], key=lambda o: o.name),
                         sorted(grp.get_members(), key=lambda o: o.name))

        grp.remove_user(self.users[0])
        self.assertEqual([self.users[1]], grp.get_members())
        self.assertFalse(grp.is_member(self.users[0]))
        self.assertTrue(grp.is_member(self.users[1]))

        # verify that no actual users where removed:
        self.assertEqual(
            self.users[0], RestAuthUser.get(self.conn, username_1))
        self.assertEqual(self.users, RestAuthUser.get_all(self.conn))

    def test_removeUserNotMember(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        try:
            grp.remove_user(self.users[0])
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())
            self.assertEqual(
                self.users[0], RestAuthUser.get(self.conn, username_1))
            self.assertEqual(self.users, RestAuthUser.get_all(self.conn))

    def test_removeInvalidUser(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        user = RestAuthUser(self.conn, "foobar")
        try:
            grp.remove_user(user)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("user", e.get_type())
            self.assertEqual(
                self.users[0], RestAuthUser.get(self.conn, username_1))
            self.assertEqual(self.users, RestAuthUser.get_all(self.conn))

    def test_removeUserFromInvalidGroup(self):
        grp = RestAuthGroup(self.conn, groupname_1)

        try:
            grp.remove_user(self.users[0])
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())
            self.assertEqual(
                self.users[0], RestAuthUser.get(self.conn, username_1))
            self.assertEqual(self.users, RestAuthUser.get_all(self.conn))

    def test_removeInvalidUserFromInvalidGroup(self):
        grp = RestAuthGroup(self.conn, groupname_1)
        user = RestAuthUser(self.conn, "foobar")

        try:
            grp.remove_user(user)
            self.fail()
        except error.ResourceNotFound as e:
            # spec mandates that Resource-Type header must be the
            # first resource not found, in this case "group"
            self.assertEqual("group", e.get_type())

    def test_removeGroup(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)
        grp.remove()
        self.assertEqual([], RestAuthGroup.get_all(self.conn))
        try:
            RestAuthGroup.get(self.conn, groupname_1)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())

    def test_removeInvalidGroup(self):
        grp = RestAuthGroup(self.conn, groupname_1)

        try:
            grp.remove()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())
            self.assertEqual([], RestAuthGroup.get_all(self.conn))

        try:
            RestAuthGroup.get(self.conn, groupname_1)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())

    def test_getInvalidGroup(self):
        try:
            RestAuthGroup.get(self.conn, groupname_1)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())

    def test_getMembersInvalidGroup(self):
        grp = RestAuthGroup(self.conn, groupname_1)
        try:
            grp.get_members()
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())


class MetaGroupTests(RestAuthClientTestCase):
    def setUp(self):
        super(MetaGroupTests, self).setUp()

        self.assertEqual([], RestAuthUser.get_all(self.conn))
        self.assertEqual([], RestAuthGroup.get_all(self.conn))

        self.usr1 = RestAuthUser.create(self.conn, username_1, "foobar")
        self.usr2 = RestAuthUser.create(self.conn, username_2, "foobar")
        self.usr3 = RestAuthUser.create(self.conn, username_3, "foobar")

        self.grp1 = RestAuthGroup.create(self.conn, groupname_1)
        self.grp2 = RestAuthGroup.create(self.conn, groupname_2)

    def tearDown(self):
        """remove everything"""
        for user in RestAuthUser.get_all(self.conn):
            user.remove()
        for grp in RestAuthGroup.get_all(self.conn):
            grp.remove()

    def test_simpleInheritanceTest(self):
        self.grp1.add_user(self.usr1)
        self.grp2.add_user(self.usr2)

        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertEqual([self.usr2], self.grp2.get_members())
        self.assertTrue(self.grp1.is_member(self.usr1))
        self.assertTrue(self.grp2.is_member(self.usr2))

        # make grp2 a subgroup of grp1:
        self.grp1.add_group(self.grp2)

        # grp1 hasn't changed:
        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertTrue(self.grp1.is_member(self.usr1))

        # grp2 now has two members:
        self.assertEqual(
            sorted([self.usr1, self.usr2], key=attrgetter('name')),
            sorted(self.grp2.get_members(), key=attrgetter('name'))
        )
        self.assertTrue(self.grp2.is_member(self.usr1))
        self.assertTrue(self.grp2.is_member(self.usr2))

        # see if grp2 is really a subgroup of grp1:
        self.assertEqual([self.grp2], self.grp1.get_groups())
        self.assertEqual([], self.grp2.get_groups())

    def test_simpleInheritanceClass(self):
        # test passing group instances to add/remove_group:
        self.grp1.add_user(self.usr1)
        self.grp2.add_user(self.usr2)

        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertEqual([self.usr2], self.grp2.get_members())
        self.assertTrue(self.grp1.is_member(self.usr1))
        self.assertTrue(self.grp2.is_member(self.usr2))

        # make grp2 a subgroup of grp1:
        self.grp1.add_group(self.grp2.name)

        # grp1 hasn't changed:
        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertTrue(self.grp1.is_member(self.usr1))

        # grp2 now has two members:
        self.assertEqual(
            sorted([self.usr1, self.usr2], key=attrgetter('name')),
            sorted(self.grp2.get_members(), key=attrgetter('name'))
        )
        self.assertTrue(self.grp2.is_member(self.usr1))
        self.assertTrue(self.grp2.is_member(self.usr2))

        # see if grp2 is really a subgroup of grp1:
        self.assertEqual([self.grp2], self.grp1.get_groups())

        self.assertEqual([], self.grp2.get_groups())
        # remove again:
        self.grp1.remove_group(self.grp2.name)
        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertEqual([self.usr2], self.grp2.get_members())
        self.assertTrue(self.grp1.is_member(self.usr1))
        self.assertTrue(self.grp2.is_member(self.usr2))

    def test_getGroupsFlat(self):
        self.assertEqual(self.grp1.get_groups(flat=True), [])

        self.grp1.add_group(self.grp2)
        self.assertEqual(self.grp1.get_groups(flat=True), [self.grp2.name])

    def test_addInvalidGroup(self):
        grp3 = RestAuthGroup(self.conn, groupname_3 + "foo")
        try:
            self.grp1.add_group(grp3)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())
        self.assertEqual([], self.grp1.get_groups())

    def test_addGroupToInvalidGroup(self):
        grp3 = RestAuthGroup(self.conn, groupname_3 + "foo")
        try:
            grp3.add_group(self.grp1)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())
        self.assertEqual([], self.grp1.get_groups())

    def test_removeGroup(self):
        self.grp1.add_user(self.usr1)
        self.grp1.add_group(self.grp2)

        self.assertEqual([self.grp2], self.grp1.get_groups())
        self.assertEqual([], self.grp2.get_groups())
        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertEqual([self.usr1], self.grp2.get_members())

        self.grp1.remove_group(self.grp2)
        self.assertEqual([], self.grp1.get_groups())
        self.assertEqual([], self.grp2.get_groups())
        self.assertEqual([self.usr1], self.grp1.get_members())
        self.assertEqual([], self.grp2.get_members())

    def test_removeGroupNotMember(self):
        try:
            self.grp1.remove_group(self.grp2)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())

    def test_removeInvalidGroup(self):
        grp3 = RestAuthGroup(self.conn, groupname_3)

        try:
            self.grp1.remove_group(grp3)
            self.fail()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())

    def test_getGroupsInvalidGroup(self):
        grp3 = RestAuthGroup(self.conn, groupname_3)
        try:
            grp3.get_groups()
        except error.ResourceNotFound as e:
            self.assertEqual("group", e.get_type())


class CreateTest(RestAuthClientTestCase):
    def test_createGroup(self):
        self.assertTrue(RestAuthGroup.create_test(self.conn, groupname_1))
        self.assertEquals([], RestAuthGroup.get_all(self.conn))

    def test_createExistingGroup(self):
        grp = RestAuthGroup.create(self.conn, groupname_1)

        try:
            RestAuthGroup.create_test(self.conn, groupname_1)
            self.fail()
        except GroupExists:
            self.assertEquals([grp], RestAuthGroup.get_all(self.conn))
        finally:
            grp.remove()

    def test_createInvalidGroup(self):
        try:
            self.assertFalse(RestAuthGroup.create_test(self.conn, "foo:bar"))
            self.fail()
        except error.PreconditionFailed:
            self.assertEquals([], RestAuthGroup.get_all(self.conn))
