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

"""Module handling code relevant to user authentication and property management."""

import sys

if sys.version_info > (3, 0):  # pragma: py3
    PY3 = True
    from http import client as http
else:  # pragma: py2
    PY3 = False
    import httplib as http

from RestAuthCommon import error
from RestAuthClient.error import PropertyExists
from RestAuthClient.error import UnknownStatus
from RestAuthClient.error import UserExists


class RestAuthUser(object):
    """An instance of this class is an object oriented abstraction of a user in a RestAuth server.

    .. Warning:: The constructor *does not* verify that the user actually exists.  This has the
       advantage of saving one request to the RestAuth service.  If you want to be sure that a user
       exists, use :py:meth:`~.get` or :py:meth:`~.get_all`.

    :param conn: The connection to the RestAuthServer.
    :type  conn: :py:class:`.RestAuthConnection`
    :param name: The name of this user.
    :type  name: str
    """
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

    def set_password(self, password=None):
        """Set the password of this user.

        :param password: The new password of the user. If None or an empty string, the user is
            effectively disabled.
        :type  password: str

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise UnknownStatus: If the response status is unknown.
        :raise PreconditionFailed: When the password is invalid.
        """
        params = {}
        if password:
            params['password'] = password
        resp = self.conn.put('/users/%s' % self.name, params)
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp.read())
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def verify_password(self, password):
        """Verify the given password.

        :param password: The password to verify.
        :type  password: str
        :return: True if the password is correct, False if the password is wrong or the user does
            not exist.
        :rtype: bool

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.post('/users/%s' % self.name, {'password': password})
        if resp.status == http.NO_CONTENT:
            return True
        elif resp.status == http.NOT_FOUND:
            return False
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def remove(self):
        """Remove this user.

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.delete('/users/%s' % self.name)
        if resp.status == http.NO_CONTENT:
            return
        if resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def get_properties(self):
        """Get all properties defined for this user.

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.get('/users/%s/props/' % self.name)
        if resp.status == http.OK:
            return self.conn.content_handler.unmarshal_dict(resp.read())
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def create_property(self, prop, value):
        """
        Create a new property for this user. This method fails if the property already exists. Use
        :py:meth:`set_property` if you do not care if the property already exists.

        :param prop: The property to set.
        :type  prop: str
        :param value: The new value of the property
        :type  value: str

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise PropertyExists: When the property already exists
        :raise PreconditionFailed: When the propertyname contains invalid characters
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        params = {'prop': prop, 'value': value}
        resp = self.conn.post('/users/%s/props/' % self.name, params=params)
        if resp.status == http.CREATED:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        elif resp.status == http.CONFLICT:
            raise PropertyExists(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def create_property_test(self, prop, value):
        """
        Do a test-run on creating a property (i.e. to test user input against the RestAuth server
        configuration). This method throws the exact same Exceptions as :py:func:`create_property`
        and also returns None if creating the property would succeed.

        .. NOTE:: Invoking this method cannot guarantee that actually creating this property will
           work in the future, i.e. it may have been created by another client in the meantime.
        """
        params = {'prop': prop, 'value': value}
        resp = self.conn.post('/test/users/%s/props/' % self.name, params=params)

        if resp.status == http.CREATED:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        elif resp.status == http.CONFLICT:
            raise PropertyExists(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def set_property(self, prop, value):
        """Set a property for this user. This method overwrites any previous entry.

        :param prop: The property to set.
        :type  prop: str
        :param value: The new value of the property
        :type  value: str

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise PreconditionFailed: When the property name is invalid.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.put('/users/%s/props/%s/' % (self.name, prop), params={'value': value})
        if resp.status == http.OK:
            return self.conn.content_handler.unmarshal_str(resp.read())
        if resp.status == http.CREATED:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def set_properties(self, props):
        """Set multiple properties at once. This method overwrites any previous settings.

        :param props: The new properties to set
        :type  props: dict

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise PreconditionFailed: When any of the given property names is invalid.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.put('/users/%s/props/' % self.name, params=props)
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def get_property(self, prop):
        """Get the given property for this user.

        :return: The value of the property.
        :rtype: str

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.

            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.get('/users/%s/props/%s' % (self.name, prop))
        if resp.status == http.OK:
            return self.conn.content_handler.unmarshal_str(resp.read())
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def remove_property(self, prop):
        """Delete the given property.

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user or property does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = self.conn.delete('/users/%s/props/%s' % (self.name, prop))
        if resp.status == http.NO_CONTENT:
            return
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def get_groups(self, flat=False):
        """Get all groups that this user is a member of.

        This method is just a shortcut for :py:meth:`.RestAuthGroup.get_all`.

        :return: All groups that the user is a member of.
        :rtype: [:py:class:`groups <.RestAuthGroup>` or str]

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        return self.conn._group.get_all(self.conn, self, flat=flat)

    def in_group(self, grp):
        """Check if the user is a member in the given group.

        This method is just a shortcut for :py:meth:`.RestAuthGroup.is_member`.

        :param grp: The group of interest.
        :type  grp: :py:class:`str` or :py:class:`.RestAuthGroup`
        :return: True if this user is a member, False otherwise.
        :rtype: bool

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user or group does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if not hasattr(grp, 'name'):
            grp = self.conn._group(self.conn, grp)
        return grp.is_member(self.name)

    def add_group(self, grp):
        """Make this user a member if the given group.

        This method is just a shortcut for :py:meth:`.RestAuthGroup.add_user`.

        :param grp: The group of interest.
        :type  grp: :py:class:`str` or :py:class:`.RestAuthGroup`

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user or group does not exist.
        :raise InternalServerError: When the RestAuth server returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if not hasattr(grp, 'name'):
            grp = self.conn._group(self.conn, grp)
        grp.add_user(self.name)

    def remove_group(self, grp):
        """Remove the users membership from the given group.

        This method is just a shortcut for :py:meth:`.RestAuthGroup.remove_user`.

        :param grp: The group of interest.
        :type  grp: :py:class:`str` or :py:class:`.RestAuthGroup`

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user or group does not exist.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        if not hasattr(grp, 'name'):
            grp = self.conn._group(self.conn, grp)
        grp.remove_user(self.name)

    @classmethod
    def create(cls, conn, name, password=None, properties=None):
        """Factory method that creates a *new* user in the RestAuth database.

        :param conn: A connection to a RestAuth service.
        :type  conn: :py:class:`.RestAuthConnection`
        :param name: Name of the user to get
        :type  name: str
        :param password: Password for the new user. If None or an empty string, the user is
            effectively disabled.
        :type  password: str
        :return: The user object representing the user just created.
        :rtype: :py:class:`~.user.RestAuthUser`

        :raise BadRequest: If the server was unable to parse the request body.
        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise UserExists: If the user already exists.
        :raise PreconditionFailed: When username or password is invalid.
        :raise UnsupportedMediaType: The server does not support the content type used by this
            connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        params = {'user': name}
        if password:
            params['password'] = password
        if properties:
            params['properties'] = properties

        resp = conn.post('/users/', params)
        if resp.status == http.CREATED:
            return cls(conn, name)
        elif resp.status == http.CONFLICT:
            raise UserExists(name)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp.read())
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def create_test(cls, conn, name, password=None, properties=None):
        """
        Do a test-run on creating a new user (i.e. to test user input against the RestAuth server
        configuration). This method throws the exact same Exceptions as :py:func:`create` but
        always returns None instead of a :py:class:`RestAuthUser` instance if the user could be
        created that way.

        .. NOTE:: Invoking this method cannot guarantee that actually creating this user will work
           in the future, i.e. it may have been created by another client in the meantime.
        """
        params = {'user': name}
        if password:
            params['password'] = password
        if properties:
            params['properties'] = properties

        resp = conn.post('/test/users/', params)
        if resp.status == http.CREATED:
            return
        elif resp.status == http.CONFLICT:
            raise UserExists(name)
        elif resp.status == http.PRECONDITION_FAILED:
            raise error.PreconditionFailed(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def get(cls, conn, name):
        """
        Factory method that gets an *existing* user from RestAuth. This method verifies that the
        user exists in RestAuth and throws
        :py:exc:`~common:RestAuthCommon.error.ResourceNotFound` if not.

        :param conn: A connection to a RestAuth service.
        :type  conn: :py:class:`.RestAuthConnection`
        :param name: Name of the user to get
        :type  name: str
        :return: The user object representing the user just created.
        :rtype: :py:class:`~.user.RestAuthUser`

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise ResourceNotFound: If the user does not exist in RestAuth.
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        # this just verify that the user exists in RestAuth:
        resp = conn.get('/users/%s/' % (name))

        if resp.status == http.NO_CONTENT:
            return cls(conn, name)
        elif resp.status == http.NOT_FOUND:
            raise error.ResourceNotFound(resp)
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    @classmethod
    def get_all(cls, conn, flat=False):
        """Factory method that gets all users known to RestAuth.

        .. versionadded:: 0.6.2
           The ``flat`` parameter.

        :param conn: A connection to a RestAuth service.
        :type  conn: :py:class:`.RestAuthConnection`
        :param flat: If True, return a list group names as str instead of a list of
            :py:class:`.RestAuthGroup` instances.
        :type  flat: bool
        :return: A list of User objects or str, if ``flat=True``.
        :rtype: [:py:class:`~.user.RestAuthUser` or str]

        :raise Unauthorized: When the connection uses wrong credentials.
        :raise Forbidden: When the client is not allowed to perform this action.
        :raise NotAcceptable: When the server cannot generate a response in the content type used
            by this connection (see also: :py:meth:`~.RestAuthConnection.set_content_handler`).
        :raise InternalServerError: When the RestAuth service returns HTTP status code 500.
        :raise UnknownStatus: If the response status is unknown.
        """
        resp = conn.get('/users/')

        if resp.status == http.OK:
            usernames = conn.content_handler.unmarshal_list(resp.read())
            if flat is True:
                return usernames
            else:
                return [cls(conn, name) for name in usernames]
        else:  # pragma: no cover
            raise UnknownStatus(resp)

    def __eq__(self, other):
        """Two instances evaluate as equal if their name and connection evaluate as equal."""
        return self.name == other.name and self.conn == other.conn

    def __hash__(self):  # pragma: no cover
        return hash(self.name)

    def __repr__(self):  # pragma: no cover
        if PY3 is False and isinstance(self.name, unicode):
            return '<User: {0}>'.format(self.name.encode('utf-8'))
        else:
            return '<User: {0}>'.format(self.name)
