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

"""Blueprint for Weko index tree rest."""

import json

from functools import wraps
from flask import (
    Blueprint, abort, current_app, json, jsonify, request,
    make_response, url_for)
from invenio_records_rest.utils import obj_or_import_string
from invenio_rest import ContentNegotiatedMethodView
from weko_deposit.api import WekoDeposit

from .api import Indexes
from .errors import InvalidDataRESTError, \
    IndexMoveRESTError, IndexDeletedRESTError, \
    IndexNotFoundRESTError, IndexUpdatedRESTError


def need_record_permission(factory_name):
    """Decorator checking that the user has the required permissions on record.

    :param factory_name: name of the factory to retrieve.
    """
    def need_record_permission_builder(f):
        @wraps(f)
        def need_record_permission_decorator(self, *args,
                                             **kwargs):
            permission_factory = (getattr(self, factory_name))

            if permission_factory:
                if not permission_factory.can():
                    from flask_login import current_user
                    if not current_user.is_authenticated:
                        abort(401)
                    abort(403)

            return f(self, *args, **kwargs)
        return need_record_permission_decorator
    return need_record_permission_builder


def create_blueprint(app, endpoints):
    """Create Weko-Index-Tree-REST blueprint.

    See: :data:`weko_index_tree.config.WEKO_INDEX_TREE_REST_ENDPOINTS`.

    :param endpoints: List of endpoints configuration.
    :returns: The configured blueprint.
    """
    blueprint = Blueprint(
        'weko_index_tree_rest',
        __name__,
        url_prefix='',
    )

    for endpoint, options in (endpoints or {}).items():

        if 'record_serializers' in options:
            record_serializers = options.get('record_serializers')
            record_serializers = {mime: obj_or_import_string(func)
                                  for mime, func in record_serializers.items()}
        else:
            record_serializers = {}

        record_class = obj_or_import_string(options.get('record_class'), default=Indexes)

        ctx = dict(
            read_permission_factory=obj_or_import_string(
                options.get('read_permission_factory_imp')
            ),
            create_permission_factory=obj_or_import_string(
                options.get('create_permission_factory_imp')
            ),
            update_permission_factory=obj_or_import_string(
                options.get('update_permission_factory_imp')
            ),
            delete_permission_factory=obj_or_import_string(
                options.get('delete_permission_factory_imp')
            ),
            record_class=record_class,
            loaders={
                options.get('default_media_type'): lambda: request.get_json()},
        )

        iar = IndexActionResource.as_view(
            IndexActionResource.view_name.format(endpoint),
            ctx=ctx,
            record_serializers=record_serializers,
            default_media_type=options.get('default_media_type'),
        )

        ita = IndexTreeActionResource.as_view(
            IndexTreeActionResource.view_name.format(endpoint),
            ctx=ctx,
            record_serializers=record_serializers,
            default_media_type=options.get('default_media_type'),
        )

        blueprint.add_url_rule(
            options.pop('index_route'),
            view_func=iar,
            methods=['GET', 'PUT', 'POST', 'DELETE'],
        )

        blueprint.add_url_rule(
            options.pop('tree_route'),
            view_func=ita,
            methods=['GET'],
        )

    return blueprint


class IndexActionResource(ContentNegotiatedMethodView):
    """redirect to next page(index select) """
    view_name = '{0}_index_action'

    def __init__(self, ctx, record_serializers=None,
                 default_media_type=None, **kwargs):
        """Constructor."""
        super(IndexActionResource, self).__init__(
            method_serializers={
                'GET': record_serializers,
                'PUT': record_serializers,
                'POST': record_serializers,
                'DELETE': record_serializers,
            },
            default_method_media_type={
                'GET': default_media_type,
                'PUT': default_media_type,
                'POST': default_media_type,
                'DELETE': record_serializers,
            },
            default_media_type=default_media_type,
            **kwargs
        )
        for key, value in ctx.items():
            setattr(self, key, value)

    @need_record_permission('read_permission_factory')
    def get(self, index_id):
        """Get a tree index record"""
        try:
            index = self.record_class.get_index(index_id)
            return make_response(jsonify(index), 200)
        except:
            raise InvalidDataRESTError()

    # @pass_record
    @need_record_permission('create_permission_factory')
    def post(self, index_id, **kwargs):
        """Create a index"""
        data = self.loaders[request.mimetype]()
        if not data:
            raise InvalidDataRESTError()

    @need_record_permission('update_permission_factory')
    def put(self, index_id, **kwargs):
        """Update a new index """
        data = self.loaders[request.mimetype]()
        if not data:
            raise InvalidDataRESTError()
        if not self.record_class.update(index_id, **data):
            raise IndexUpdatedRESTError()

    @need_record_permission('delete_permission_factory')
    def delete(self, index_id, **kwargs):
        """Delete a index """

        if not index_id or index_id <= 0:
            raise IndexNotFoundRESTError()

        data = self.loaders[request.mimetype]()

        res = self.record_class.get_self_path(index_id)
        result = self.record_class.delete_tree_by_id(index_id)
        if result:
            status = 200
            msg = 'Index deleted Successfully.'

            # delete index with move items
            if data and data.get("move"):
                pat = res.path.replace(index_id, "")
                if pat:
                    WekoDeposit.update_by_index_tree_id(index_id, pat[:-1])
                else:
                    raise IndexMoveRESTError()
            else:
                # delete indexes only
                WekoDeposit.delete_by_index_tree_id(index_id)
        else:
            raise IndexDeletedRESTError()

        return make_response(jsonify({'status': status, 'message': msg}), status)


class IndexTreeActionResource(ContentNegotiatedMethodView):
    """redirect to next page(index select) """
    view_name = '{0}_tree_action'

    def __init__(self, ctx, record_serializers=None,
                 default_media_type=None, **kwargs):
        """Constructor."""
        super(IndexTreeActionResource, self).__init__(
            method_serializers={
                'GET': record_serializers,
                'PUT': record_serializers,
                'POST': record_serializers,
            },
            default_method_media_type={
                'GET': default_media_type,
                'PUT': default_media_type,
                'POST': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs
        )
        for key, value in ctx.items():
            setattr(self, key, value)

    @need_record_permission('read_permission_factory')
    def get(self):
        """Get tree json"""
        try:
            tree = self.record_class.get_index_tree()
            return make_response(jsonify(tree), 200)
        except:
            raise InvalidDataRESTError()