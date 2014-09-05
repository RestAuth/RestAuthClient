# -*- coding: utf-8 -*-
#
# This file is part of RestAuthClient (https://python.restauth.net).
#
# RestAuthClient is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# RestAuthClient is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with RestAuth. If not,
# see <http://www.gnu.org/licenses/>.

"""Module handling code relevant to group handling.

.. moduleauthor:: Mathias Ertl <mati@restauth.net>
"""

import sys

from RestAuthClient.error import GroupExists
from RestAuthClient.error import UnknownStatus

from RestAuthCommon import error

if sys.version_info > (3, 0):  # pragma: py3
    PY3 = True
    from http import client as http
else:  # pragma: py2
    PY3 = False
    import httplib as http


class RestAuthGroup(object):
    """An instance of this class represents a group in RestAuth.

    *Note:* The constructor *does not* verify that the group actually exists. This has the
    advantage of saving one request to the RestAuth service.  If you want to be sure that a user
    exists, use :py:func:`get` or :py:func:`get_all`.

    :param conn: The connection to the RestAuthServer.
    :type  conn: :py:class:`.RestAuthConnection`
    :param name: The name of this user.
    :type  name: str
    """

    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

    def get_members(self, flat=False):
        """Get all members of this group.

        .. versionadded:: 0.6.2
           The ``flat`` parameter.

        :param flat: If True, return a list group names as str instead of a list of
            :py:class:`.RestAuthGroup` instances.
        :type  flat: bool
        :return: A list of:py:class:`.RestAuthGroup` objects or a list of str if ``flat=True``.
        :rtype: [:py:class:`groups <.RestAuthGroup>` or str]

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group does not exist.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.get('/groups/%s/users/' % self.conn.quote(self.name))

        if resp.status == http.OK:
            # parse user-list:
            names = self.conn.content_handler.unmarshal_list(resp.read())
            if flat is True:
                return names
            else:
                return [self.conn._user(self.conn, name) for name in names]
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def add_user(self, user):
        """Add a user to this group.

        :param user: The user or the name of the user to add.
        :type  user: :py:class:`.RestAuthUser` or str

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group or user does not exist.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if hasattr(user, 'name'):
            user = user.name

        resp = self.conn.post('/groups/%s/users/' % self.conn.quote(self.name), {'user': user})
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def add_group(self, group):
        """Add a group to this group.

        :param group: The group or the name of the group to add.
        :type  group: :py:class:`.RestAuthGroup` or str

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group or user does not exist.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if hasattr(group, 'name'):
            group = group.name

        resp = self.conn.post('/groups/%s/groups/' % self.conn.quote(self.name), {'group': group})
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def get_groups(self, flat=False):
        """Get a list of sub-groups of this group.

        .. versionadded:: 0.6.2
           The ``flat`` parameter.

        :param flat: If True, return a list group names as str instead of a list of
            :py:class:`.RestAuthGroup` instances.
        :type  flat: bool
        :return: A list of :py:class:`.RestAuthGroup` objects or a list of str if ``flat=True``
        :rtype: [:py:class:`.RestAuthGroup` or str]

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the sub- or meta-group not exist.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.get('/groups/%s/groups/' % self.conn.quote(self.name))
        if resp.status == http.OK:
            names = self.conn.content_handler.unmarshal_list(resp.read())
            if flat is True:
                return names
            else:
                return [RestAuthGroup(self.conn, name) for name in names]
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def remove_group(self, group):
        """Remove a sub-group from this group.

        :param group: The group or the name of the group to remove.
        :type  group: :py:class:`.RestAuthGroup` or str

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the sub- or meta-group not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if hasattr(group, 'name'):
            group = group.name

        resp = self.conn.delete('/groups/%s/groups/%s/' % (self.conn.quote(self.name),
                                                           self.conn.quote(group)))
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def remove(self):
        """Delete this group.

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.delete('/groups/%s/' % self.conn.quote(self.name))
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def is_member(self, user):
        """Check if the named user is a member.

        :param user: The user or the name of a user in question.
        :type  user: :py:class:`.RestAuthUser` or str
        :return: True if the user is a member, False if not.
        :rtype: bool

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group or user does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if hasattr(user, 'name'):
            user = user.name

        resp = self.conn.get('/groups/%s/users/%s/' % (self.conn.quote(self.name),
                                                       self.conn.quote(user)))
        if resp.status == http.NO_CONTENT:
            return True
        elif resp.status == http.NOT_FOUND:
            if resp.getheader('Resource-Type') == 'user':
                return False
            else:
                raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def remove_user(self, user):
        """Remove the given user from the group.

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group or user does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if hasattr(user, 'name'):
            user = user.name

        resp = self.conn.delete('/groups/%s/users/%s/' % (self.conn.quote(self.name),
                                                          self.conn.quote(user)))
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def create(cls, conn, name):
        """Factory method that creates a *new* group in RestAuth.

        :param conn: A connection to a RestAuth service.
        :type  conn: :py:class:`.RestAuthConnection`
        :param name: The name of the group to create
        :type  name: str
        :return: The group object representing the group just created.
        :rtype: :py:class:`.RestAuthGroup`

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise GroupExists: When the user already exists.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = conn.post('/groups/', {'group': name})
        if resp.status == http.CREATED:
            return cls(conn, name)
        elif resp.status == http.CONFLICT:
            raise GroupExists("Conflict.")
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def create_test(cls, conn, name):
        """
        Do a test-run on creating a new group (i.e. to test user input against the RestAuth server
        configuration). This method throws the exact same Exceptions as :py:func:`create` but
        always returns None instead of a :py:class:`RestAuthGroup` instance if the group could be
        created that way.

        .. NOTE:: Invoking this method cannot guarantee that actually creating this group will work
           in the future, i.e. it may have been created by another client in the meantime.
        """
        resp = conn.post('/test/groups/', {'group': name})
        if resp.status == http.CREATED:
            return True
        elif resp.status == http.CONFLICT:
            raise GroupExists("Conflict.")
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def get_all(cls, conn, user=None, flat=False):
        """Factory method that gets all groups for this service known to RestAuth.

        .. versionadded:: 0.6.2
           The ``flat`` parameter.

        :param conn: A connection to a RestAuth service.
        :type  conn: :py:class:`.RestAuthConnection`
        :param user: Only return groups where the named user is a member
        :type  user: str
        :param flat: If True, return a list group names as str instead of a list of
            :py:class:`RestAuthGroup` instances.
        :type  flat: bool
        :return: A list of :py:class:`RestAuthGroup` objects or a list of str if ``flat=True``
        :rtype: [:py:class:`.RestAuthGroup` or str]

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: When the given user does not exist.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        params = {}
        if user:
            if hasattr(user, 'name'):
                user = user.name

            params['user'] = user

        resp = conn.get('/groups/', params)
        if resp.status == http.OK:
            names = conn.content_handler.unmarshal_list(resp.read())
            if flat is True:
                return names
            else:
                return [cls(conn, name) for name in names]
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def get(cls, conn, name):
        """
        Factory method that gets an *existing* user from RestAuth. This method verifies that the
        user exists in the RestAuth and throws :py:exc:`.ResourceNotFound` if not.

        :param conn: A connection to a RestAuth service.
        :type  conn: :py:class:`.RestAuthConnection`
        :param name: The name of the group to get
        :type  name: str
        :return: The group object representing the group in RestAuth.
        :rtype: :py:class:`.RestAuthGroup`

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the group does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = conn.get('/groups/%s/' % conn.quote(name))
        if resp.status == http.NO_CONTENT:
            return cls(conn, name)
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def __eq__(self, other):
        """Two instances evaluate as equal if their name and connection evaluate as equal."""
        return self.name == other.name and self.conn == other.conn

    def __repr__(self):  # pragma: no cover
        if PY3 is False and isinstance(self.name, unicode):
            return '<Group: {0}>'.format(self.name.encode('utf-8'))
        else:
            return '<Group: {0}>'.format(self.name)


# provide compatability with old paths:
warnings = None


class Group(RestAuthGroup):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        global warnings
        if warnings is None:
            import warnings

        warnings.warn("Group class is deprecated, use RestAuthGroup instead.")
        super(Group, self).__init__(*args, **kwargs)


def create(*args, **kwargs):  # pragma: no cover
    global warnings
    if warnings is None:
        import warnings
    warnings.warn("Deprecated function, use RestAuthGroup.create instead.")
    return RestAuthGroup.create(*args, **kwargs)


def create_test(*args, **kwargs):  # pragma: no cover
    global warnings
    if warnings is None:
        import warnings
    warnings.warn("Deprecated function, use RestAuthGroup.create_test instead.")
    return RestAuthGroup.create_test(*args, **kwargs)


def get(*args, **kwargs):  # pragma: no cover
    global warnings
    if warnings is None:
        import warnings
    warnings.warn("Deprecated function, use RestAuthGroup.get instead.")
    return RestAuthGroup.get(*args, **kwargs)


def get_all(*args, **kwargs):  # pragma: no cover
    global warnings
    if warnings is None:
        import warnings
    warnings.warn("Deprecated function, use RestAuthGroup.get_all instead.")
    return RestAuthGroup.get_all(*args, **kwargs)
