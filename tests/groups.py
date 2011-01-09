# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from operator import attrgetter

import unittest
from RestAuthClient.errors import *
from RestAuthClient.common import RestAuthConnection
from RestAuthClient import restauth_user, group

host = 'http://localhost:8000'
user = 'vowi'
passwd = 'vowi'
conn = RestAuthConnection( host, user, passwd )

username_1 = "mati 1 \u6110"
username_2 = "mati 2 \u6111"
username_3 = "mati 3 \u6112"

groupname_1 = "group \u7110"
groupname_2 = "group \u7111"
groupname_3 = "group \u7111"

class BasicTests( unittest.TestCase ):
	def setUp( self ):
		self.assertEqual( [], restauth_user.get_all( conn ) )
		self.assertEqual( [], group.get_all( conn ) )

		self.users = [ 
			restauth_user.create( conn, username_1, "foobar" ),
			restauth_user.create( conn, username_2, "foobar" ),
			restauth_user.create( conn, username_3, "foobar" ),
			]

	def tearDown( self ):
		"""remove everything"""
		for user in restauth_user.get_all( conn ):
			user.remove()
		for grp in group.get_all( conn ):
			grp.remove()

	def test_createGroup( self ):
		grp = group.create( conn, groupname_1 )
		self.assertEqual( [grp], group.get_all( conn ) )
		self.assertEqual( grp, group.get( conn, groupname_1 ) )

	def test_createInvalidGroup( self ):
		try:
			group.create( conn, "foo/bar" )
			self.fail()
		except PreconditionFailed as e:
			self.assertEqual( [], group.get_all( conn ) )

	def test_addUser( self ):
		grp_0 = group.create( conn, groupname_1 )
		grp_1 = group.create( conn, groupname_2 )
		self.assertEqual( [ grp_0, grp_1 ], group.get_all( conn ) )

		grp_0.add_user( self.users[0] )
		grp_1.add_user( self.users[1] )
		grp_1.add_user( self.users[2] )

		self.assertEqual( [self.users[0]], grp_0.get_members() )
		self.assertEqual( self.users[1:3], grp_1.get_members() )

		self.assertTrue( grp_0.is_member( self.users[0] ) )
		self.assertFalse( grp_0.is_member( self.users[1] ) )
		self.assertFalse( grp_0.is_member( self.users[2] ) )
		self.assertTrue( grp_1.is_member( self.users[1] ) )
		self.assertTrue( grp_1.is_member( self.users[2] ) )
		self.assertFalse( grp_1.is_member( self.users[0] ) )

	def test_addInvalidUser( self ):
		grp = group.create( conn, groupname_1 )
		user = restauth_user.User( conn, "foobar" )

		try:
			grp.add_user( user )
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )
			users = restauth_user.get_all( conn )
			self.assertEqual( self.users, restauth_user.get_all( conn ) )
	
	def test_addUserToInvalidGroup( self ):
		grp = group.Group( conn, groupname_1 )
		try:
			grp.add_user( self.users[0] )
		except ResourceNotFound as e:
			self.assertEqual( "group", e.get_type() )
			self.assertEqual( [], group.get_all( conn ) )

	def test_removeUser( self ):
		grp = group.create( conn, groupname_1 )
		grp.add_user( self.users[0] )
		grp.add_user( self.users[1] )
		self.assertEqual( self.users[0:2], grp.get_members() )

		grp.remove_user( self.users[0] )
		self.assertEqual( [self.users[1]], grp.get_members() )
		self.assertFalse( grp.is_member( self.users[0] ) )
		self.assertTrue( grp.is_member( self.users[1] ) )
		
		# verify that no actual users where removed:
		self.assertEqual( self.users[0], restauth_user.get( conn, username_1 ) )
		self.assertEqual( self.users, restauth_user.get_all( conn ) )

		
	def test_removeUserNotMember( self ):
		grp = group.create( conn, groupname_1 )
		try:
			grp.remove_user( self.users[0] )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )
			self.assertEqual( self.users[0], restauth_user.get( conn, username_1 ) )
			self.assertEqual( self.users, restauth_user.get_all( conn ) )

	def test_removeInvalidUser( self ):
		grp = group.create( conn, groupname_1 )
		user = restauth_user.User( conn, "foobar" )
		try:
			grp.remove_user( user )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )
			self.assertEqual( self.users[0], restauth_user.get( conn, username_1 ) )
			self.assertEqual( self.users, restauth_user.get_all( conn ) )

	def test_removeUserFromInvalidGroup( self ):
		grp = group.Group( conn, groupname_1 )

		try:
			grp.remove_user( self.users[0] )
		except ResourceNotFound as e:
			self.assertEqual( "group", e.get_type() )
			self.assertEqual( self.users[0], restauth_user.get( conn, username_1 ) )
			self.assertEqual( self.users, restauth_user.get_all( conn ) )

	def test_removeInvalidUserFromInvalidGroup( self ):
		grp = group.Group( conn, groupname_1 )
		user = restauth_user.User( conn, "foobar" )
		
		try:
			grp.remove_user( user )
		except ResourceNotFound as e:
			# spec mandates that Resource-Type header must be the
			# first resource not found, in this case "group"
			self.assertEqual( "group", e.get_type() )


class MetaGroupTests( unittest.TestCase ):
	def setUp( self ):
		self.assertEqual( [], restauth_user.get_all( conn ) )
		self.assertEqual( [], group.get_all( conn ) )

		self.usr1 = restauth_user.create( conn, username_1, "foobar" )
		self.usr2 = restauth_user.create( conn, username_2, "foobar" )
		self.usr3 = restauth_user.create( conn, username_3, "foobar" )

		self.grp1 = group.create( conn, groupname_1 )
		self.grp2 = group.create( conn, groupname_2 )

	def tearDown( self ):
		"""remove everything"""
		for user in restauth_user.get_all( conn ):
			user.remove()
		for grp in group.get_all( conn ):
			grp.remove()

	def test_simpleInheritanceTest( self ):
		self.grp1.add_user( self.usr1 )
		self.grp2.add_user( self.usr2 )

		self.assertEqual( [self.usr1], self.grp1.get_members() )
		self.assertEqual( [self.usr2], self.grp2.get_members() )
		self.assertTrue( self.grp1.is_member( self.usr1 ) )
		self.assertTrue( self.grp2.is_member( self.usr2 ) )

		# make grp2 a subgroup of grp1:
		self.grp1.add_group( self.grp2 )

		# grp1 hasn't changed:
		self.assertEqual( [self.usr1], self.grp1.get_members() )
		self.assertTrue( self.grp1.is_member( self.usr1 ) )

		# grp2 now has two members:
		self.assertEqual( sorted([self.usr1, self.usr2], key=attrgetter('name') ), 
			sorted(self.grp2.get_members(), key=attrgetter('name')) )
		self.assertTrue( self.grp2.is_member( self.usr1 ) )
		self.assertTrue( self.grp2.is_member( self.usr2 ) )

		# see if grp2 is really a subgroup of grp1:
		self.assertEqual( [self.grp2], self.grp1.get_groups() )
		self.assertEqual( [], self.grp2.get_groups() )

	def test_addInvalidGroup( self ):
		grp3 = group.Group( conn, groupname_3 + "foo" )
		try:
			self.grp1.add_group( grp3 )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "group", e.get_type() )
		self.assertEqual( [], self.grp1.get_groups() )

	def test_addGroupToInvalidGroup( self ):
		grp3 = group.Group( conn, groupname_3 + "foo" )
		try:
			grp3.add_group( self.grp1 )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "group", e.get_type() )
		self.assertEqual( [], self.grp1.get_groups() )

	def test_removeGroup( self ):
		self.grp1.add_group( self.grp2 )
		self.assertEqual( [self.grp2], self.grp1.get_groups() )
		self.assertEqual( [], self.grp2.get_groups() )

		self.grp1.remove_group( self.grp2 )
		self.assertEqual( [], self.grp1.get_groups() )
		self.assertEqual( [], self.grp2.get_groups() )

	def test_removeGroupNotMember( self ):
		try:
			self.grp1.remove_group( self.grp2 )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "group", e.get_type() )

	def test_removeInvalidGroup( self ):
		grp3 = group.Group( conn, groupname_3 )

		try:
			self.grp1.remove_group( grp3 )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "group", e.get_type() )
