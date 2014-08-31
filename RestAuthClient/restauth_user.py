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

"""Provide import paths used in RestAuthClient 0.6.1."""

import warnings

from RestAuthClient.user import RestAuthUser


class User(RestAuthUser):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        warnings.warn("This class is deprecated. Use RestAuthClient.user.RestAuthUser instead.")
        super(User, self).__init__(*args, **kwargs)


def create(*args, **kwargs):  # pragma: no cover
    warnings.warn("Deprecated function, use RestAuthClient.user.RestAuthUser.create instead.")
    return RestAuthUser.create(*args, **kwargs)


def create_test(*args, **kwargs):  # pragma: no cover
    warnings.warn("Deprecated function, use RestAuthClient.user.RestAuthUser.create_test instead.")
    return RestAuthUser.create_test(*args, **kwargs)


def get(*args, **kwargs):  # pragma: no cover
    warnings.warn("Deprecated function, use RestAuthClient.user.RestAuthUser.get instead.")
    return RestAuthUser.get(*args, **kwargs)


def get_all(*args, **kwargs):  # pragma: no cover
    warnings.warn("Deprecated function, use RestAuthClient.user.RestAuthUser.get_all instead.")
    return RestAuthUser.get_all(*args, **kwargs)
