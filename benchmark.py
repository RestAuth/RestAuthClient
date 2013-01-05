#!/usr/bin/python3

import time

from RestAuthClient.restauth_user import (
    User, get as user_get, create as user_create, get_all as user_get_all)
from RestAuthClient.group import (
    create as group_create, get as group_get, get_all as group_get_all)
from RestAuthClient.common import RestAuthConnection

count=100

usernames = ['user%s' % i for i in range(1, count)]
props = dict([('key%s' % i, 'val%s' % i) for i in range(1, int(count/10))])
groupnames = ['group%s' % i for i in range(1, count)]

users = []
groups = []
conn = RestAuthConnection('http://127.0.0.1', 'example.com', 'nopass')

total_start = time.time()

print('Create %s users...' % count, end=" ")
start = time.time()
for username in usernames:
    users.append(user_create(conn, username, 'foobar'))
print('%.3f seconds' % (time.time() - start))

print('Get %s users (three times each)...' % count, end=' ')
# additional GETs are done to give caches a chance to work
start = time.time()
for username in usernames:
    user_get(conn, username)
    user_get(conn, username)
    user_get(conn, username)
print('%.3f seconds' % (time.time() - start))

print('Verify passwords (three times each)...', end=' ')
# additional GETs are done to give caches a chance to work
start = time.time()
for user in users:
    user.verify_password('foobar')
    user.verify_password('foobar')
    user.verify_password('foobar')
print('%.3f seconds' % (time.time() - start))

print('Set password...', end=' ')
start = time.time()
for user in users:
    user.set_password('foobar')
print('%.3f seconds' % (time.time() - start))

print('Create %s properties for each user...' % int(count/10), end=' ')
start = time.time()
for user in users:
    for key, val in props.items():
        user.create_property(key, val)
print('%.3f seconds' % (time.time() - start))

print('Get all properties...', end=' ')
start = time.time()
for user in users:
    user.get_properties()
print('%.3f seconds' % (time.time() - start))

print('Get properties individually (3 times each)...', end=' ')
start = time.time()
for user in users:
    for key in list(props.keys())[:10]:
        user.get_property(key)
        user.get_property(key)
        user.get_property(key)
print('%.3f seconds' % (time.time() - start))

print('Set properties for each user again...', end=' ')
start = time.time()
for user in users:
    for key in props.keys():
        user.set_property(key, 'foobar')
print('%.3f seconds' % (time.time() - start))

print('Delete %s properties of each user...' % (count/10), end=' ')
start = time.time()
for user in users:
    for key in props.keys():
        user.remove_property(key)
print('%.3f seconds' % (time.time() - start))

print('Create %s groups...' % count, end=' ')
start = time.time()
for name in groupnames:
    groups.append(group_create(conn, name))
print('%.3f seconds' % (time.time() - start))

print('Adding users to groups...', end=' ')
start = time.time()
# we add 100 users to first group, 100 users to second group, ...
for i in range(0, int(count/100)):
    offset = i * 100
    for user in users[offset:offset + 100]:
        groups[i].add_user(user.name)
print('%.3f seconds' % (time.time() - start))

print('Getting all users of a group...', end=' ')
start = time.time()
for group in groups:
    group.get_members()
    group.get_members()
    group.get_members()
print('%.3f seconds' % (time.time() - start))

print('Checking individual memberships...', end=' ')
start = time.time()
for i in range(0, int(count/100)):
    for user in users[:100]:  # only use 100 users, as this multiplies!
        groups[i].is_member(user.name)
        groups[i].is_member(user.name)
        groups[i].is_member(user.name)
print('%.3f seconds' % (time.time() - start))

print('Remove memberships...', end=' ')
start = time.time()
for i in range(0, int(count/100)):
    offset = i * 100
    for user in users[offset:offset + 100]:
        groups[i].remove_user(user.name)
print('%.3f seconds' % (time.time() - start))

print('Delete users again...', end=' ')
start = time.time()
for user in users:
    user.remove()
print('%.3f seconds' % (time.time() - start))

print('Deleting groups again...', end=' ')
start = time.time()
for group in groups:
    group.remove()
print('%.3f seconds' % (time.time() - start))

print('Total: %.3f seconds' % (time.time() - total_start))
