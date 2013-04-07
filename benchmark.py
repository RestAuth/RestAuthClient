#!/usr/bin/python3

import argparse
import sys
import time

from queue import Queue
from threading import Thread

from RestAuthClient.restauth_user import (
    User, get as user_get, create as user_create, get_all as user_get_all)
from RestAuthClient.group import (
    create as group_create, get as group_get, get_all as group_get_all)
from RestAuthClient.common import RestAuthConnection

parser = argparse.ArgumentParser(description="Benchmark a RestAuth service.")
parser.add_argument('-c', '--count', type=int, metavar='N', default=100,
                    help="Create N users (default: %(default)s).")
parser.add_argument('--host', default="http://[::1]:8000",
                    help="Use HOST as RestAuth host (default: %(default)s).")
parser.add_argument('--user', default="example.com",
                    help="Use USER as RestAuth user (default: %(default)s).")
parser.add_argument(
    '--password', default="nopass",
    help="Use PASSWORD as RestAuth password (default: %(default)s)."
)
parser.add_argument('-t', '--threads', type=int, metavar='N', default=50,
                    help="Start N threads at once (default: %(default)s).")
args = parser.parse_args()

count = args.count

usernames = ['user%s' % i for i in range(1, count)]
props = dict([('key%s' % i, 'val%s' % i) for i in range(1, int(count / 10))])
groupnames = ['group%s' % i for i in range(1, count)]

users = []
groups = []
conn = RestAuthConnection(args.host, args.user, args.password)

# threading stuff
def execute(target):
    q = Queue()
    for i in range(args.threads):
        t = Thread(target=worker, kwargs={'queue': q})
        t.daemon = True
        t.start()
    return q

total_start = time.time()

print('Create %s users...' % count, end=" ")
sys.stdout.flush()
def worker(queue):
    while True:
        username = queue.get()
        try:
            users.append(user_create(conn, username, 'foobar'))
        except Exception as e:
            print(e.args[0].read())
        queue.task_done()

q = execute(worker)
start = time.time()
for username in usernames:
    q.put(username)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Get %s users (three times each)...' % count, end=' ')
sys.stdout.flush()
# additional GETs are done to give caches a chance to work
def worker(queue):
    while True:
        username = queue.get()
        user_get(conn, username)
        user_get(conn, username)
        user_get(conn, username)
        queue.task_done()
q = execute(worker)
start = time.time()
for username in usernames:
    q.put(username)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Verify passwords (three times each)...', end=' ')
sys.stdout.flush()
# additional GETs are done to give caches a chance to work
def worker(queue):
    while True:
        user = queue.get()
        user.verify_password('foobar')
        user.verify_password('foobar')
        user.verify_password('foobar')
        queue.task_done()

q = execute(worker)
start = time.time()
for user in users:
    q.put(user)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Set password...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user = queue.get()
        user.set_password('new password')
        queue.task_done()
q = execute(worker)
start = time.time()
for user in users:
    q.put(user)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Create %s properties for each user...' % int(count / 10), end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user, key, val = queue.get()
        user.create_property(key, val)
        queue.task_done()

q = execute(worker)
start = time.time()
for user in users:
    for key, val in props.items():
        q.put((user, key, val))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Get all properties...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user = queue.get()
        user.get_properties()
        user.get_properties()
        user.get_properties()
        queue.task_done()
q = execute(worker)
start = time.time()
for user in users:
    q.put(user)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Get properties individually (3 times each)...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user, key = queue.get()
        user.get_property(key)
        user.get_property(key)
        user.get_property(key)
        queue.task_done()
q = execute(worker)
start = time.time()
for user in users:
    for key in list(props.keys())[:10]:
        q.put((user, key))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Set properties for each user again...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user, key = queue.get()
        user.set_property(key, 'foobar')
        queue.task_done()
q = execute(worker)
start = time.time()
for user in users:
    for key in props.keys():
        q.put((user, key))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Delete %s properties of each user...' % (count / 10), end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user, key = queue.get()
        user.remove_property(key)
        queue.task_done()
q = execute(worker)
start = time.time()
for user in users:
    for key in props.keys():
        q.put((user, key))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Create %s groups...' % count, end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        name = queue.get()
        groups.append(group_create(conn, name))
        queue.task_done()
q = execute(worker)
start = time.time()
for name in groupnames:
    q.put(name)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Adding users to groups...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        group, username = queue.get()
        group.add_user(username)
        queue.task_done()

q = execute(worker)
start = time.time()
# we add 100 users to first group, 100 users to second group, ...
for i in range(0, int(count / 100)):
    offset = i * 100
    for user in users[offset:offset + 100]:
        q.put((groups[i], user.name))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Getting all users of a group...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        group = queue.get()
        group.get_members()
        queue.task_done()
q = execute(worker)
start = time.time()
for group in groups:
    q.put(group)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Checking individual memberships...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        group, username = queue.get()
        group.is_member(username)
        group.is_member(username)
        group.is_member(username)
        queue.task_done()

q = execute(worker)
start = time.time()
for i in range(0, int(count / 100)):
    for user in users[:100]:  # only use 100 users, as this multiplies!
        q.put((groups[i], user.name))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Remove memberships...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        group, username = queue.get()
        group.remove_user(username)
        queue.task_done()

q = execute(worker)
start = time.time()
for i in range(0, int(count / 100)):
    offset = i * 100
    for user in users[offset:offset + 100]:
        q.put((groups[i], user.name))
q.join()
print('%.3f seconds' % (time.time() - start))

print('Deleting groups again...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        group = queue.get()
        group.remove()
        queue.task_done()

q = execute(worker)
start = time.time()
for group in groups:
    q.put(group)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Delete users again...', end=' ')
sys.stdout.flush()
def worker(queue):
    while True:
        user = queue.get()
        user.remove()
        queue.task_done()

q = execute(worker)
start = time.time()
for user in users:
    q.put(user)
q.join()
print('%.3f seconds' % (time.time() - start))

print('Total: %.3f seconds' % (time.time() - total_start))
sys.stdout.flush()
