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

"""Views for weko-authors."""


from elasticsearch_dsl import Q, Search
from flask import Blueprint, current_app, json, jsonify, render_template, \
    request
from flask_babelex import gettext as _
from flask_login import login_required
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from .permissions import author_permission

blueprint = Blueprint(
    'weko_authors',
    __name__,
    url_prefix='/authors',
    template_folder='templates',
    static_folder='static',
)

blueprint_api = Blueprint(
    'weko_authors',
    __name__,
    url_prefix='/authors',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/")
@login_required
@author_permission.require(http_exception=403)
def index():
    """Render a basic view."""
    return render_template(
        current_app.config['WEKO_AUTHORS_LIST_TEMPLATE'])


@blueprint.route("/add", methods=['GET'])
@login_required
@author_permission.require(http_exception=403)
def add():
    """Render an adding author view."""
    return render_template(
        current_app.config['WEKO_AUTHORS_EDIT_TEMPLATE'])


@blueprint_api.route("/add", methods=['POST'])
@login_required
@author_permission.require(http_exception=403)
def create():
    """Add an author."""
    if request.headers['Content-Type'] != 'application/json':
        current_app.logger.debug(request.headers['Content-Type'])
        return jsonify(msg=_('Header Error'))

    data = request.get_json()
    current_app.logger.debug(data)
    current_app.logger.debug(type(data))
    current_app.logger.debug(type(json.dumps(data)))
    current_app.logger.debug(json.dumps(data))
    indexer = RecordIndexer()
    indexer.client.index(index="author",
                         doc_type="author",
                         body=data,)
    return jsonify(msg=_('Success'))


@blueprint_api.route("/search", methods=['POST'])
@login_required
@author_permission.require(http_exception=403)
def get():
    """Get all authors."""
    data = request.get_json()
    current_app.logger.debug(data)

    search = data.get('searchKey') or ''
    query = {"match_all": {}}
    if search:
        query = {"match": {"_all": search}}

    size = data.get('numOfPage') or current_app.config['WEKO_AUTHORS_NUM_OF_PAGE']
    num = data.get('pageNumber') or 1
    offset = (int(num) - 1) * size if int(num) > 1 else 0

    sort_key = data.get('sortKey') or ''
    sort_order = data.get('sortOrder') or ''
    sort = {}
    if sort_key and sort_order:
        sort = {sort_key: {"order": sort_order}}

    body = {
        "query": query,
        "from": offset,
        "size": size,
        "sort": sort
    }
    current_app.logger.debug(body)
    indexer = RecordIndexer()
    result = indexer.client.search(index="author", body=body)
    return json.dumps(result)