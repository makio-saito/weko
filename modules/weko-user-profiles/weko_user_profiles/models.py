# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""Database models for user profiles."""

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property

from .validators import validate_username


class AnonymousUserProfile:
    """Anonymous user profile."""

    @property
    def is_anonymous(self):
        """Return whether this UserProfile is anonymous."""
        return True


class UserProfile(db.Model):
    """User profile model.

    Stores a username, display name (case sensitive version of username) and a
    full name for a user.
    """

    __tablename__ = 'userprofiles_userprofile'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        primary_key=True
    )
    """Foreign key to :class:`~invenio_accounts.models.User`."""

    user = db.relationship(
        User, backref=db.backref(
            'profile', uselist=False, cascade='all, delete-orphan')
    )
    """User relationship."""

    _username = db.Column('username', db.String(255), unique=True)
    """Lower-case version of username to assert uniqueness."""

    _displayname = db.Column('displayname', db.String(255))
    """Case preserving version of username."""

    # full_name = db.Column(db.String(255), nullable=False, default='')
    # """Full name of person."""

    timezone = db.Column(db.String(255), nullable=False, default='')
    """Selected timezone."""

    language = db.Column(db.String(255), nullable=False, default='')
    """Selected language."""

    @hybrid_property
    def username(self):
        """Get username."""
        return self._displayname

    @hybrid_property
    def get_username(self):
        """Get username."""
        return self._username

    @username.setter
    def username(self, username):
        """Set username.

        .. note:: The username will be converted to lowercase. The display name
            will contain the original version.
        """
        validate_username(username)
        self._username = username.lower()
        self._displayname = username

    @classmethod
    def get_by_username(cls, username):
        """Get profile by username.

        :param username: A username to query for (case insensitive).
        """
        return cls.query.filter(
            UserProfile._username == username.lower()
        ).one()

    @classmethod
    def get_by_userid(cls, user_id):
        """Get profile by user identifier.

        :param user_id: Identifier of a :class:`~invenio_accounts.models.User`.
        :returns: A :class:`~invenio_userprofiles.models.UserProfile` instance
            or ``None``.
        """
        return cls.query.filter_by(user_id=user_id).one_or_none()

    @property
    def is_anonymous(self):
        """Return whether this UserProfile is anonymous."""
        return False


@event.listens_for(User, 'init')
def on_user_init(target, args, kwargs):
    """Provide hook on :class:`~invenio_accounts.models.User` initialization.

    Automatically convert a dict to a
    :class:`~.UserProfile` instance. This is needed
    during e.g. user registration where Flask-Security will initialize a
    user model with all the form data (which when Invenio-UserProfiles is
    enabled includes a ``profile`` key). This will make the user creation fail
    unless we convert the profile dict into a :class:`~.UserProfile` instance.
    """
    profile = kwargs.pop('profile', None)
    if profile is not None and not isinstance(profile, UserProfile):
        profile = UserProfile(**profile)
        if kwargs.get('id'):
            profile.user_id = kwargs['id']
        kwargs['profile'] = profile
