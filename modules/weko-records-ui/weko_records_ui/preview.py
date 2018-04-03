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

"""Preview for weko-records-ui."""

import cchardet as chardet
from flask import abort, current_app, request, render_template
from invenio_previewer.api import PreviewFile
from invenio_previewer.extensions import default
from invenio_previewer.proxies import current_previewer
from invenio_previewer.extensions.zip import make_tree, children_to_list


def preview(pid, record, template=None, **kwargs):
    """Preview file for given record.

    Plug this method into your ``RECORDS_UI_ENDPOINTS`` configuration:

    .. code-block:: python

        RECORDS_UI_ENDPOINTS = dict(
            recid=dict(
                # ...
                route='/records/<pid_value/preview/<path:filename>',
                view_imp='invenio_previewer.views.preview',
                record_class='invenio_records_files.api:Record',
            )
        )
    """
    # Get file from record
    fileobj = current_previewer.record_file_factory(
        pid, record, request.view_args.get(
            'filename', request.args.get('filename', type=str))
    )
    if not fileobj:
        abort(404)

    # Try to see if specific previewer is requested?
    try:
        file_previewer = fileobj['previewer']
    except KeyError:
        file_previewer = None

    # Find a suitable previewer
    fileobj = PreviewFile(pid, record, fileobj)

    if fileobj.has_extensions('.zip'):
        return zip_preview(fileobj)
    else:
        for plugin in current_previewer.iter_previewers(
                previewers=[file_previewer] if file_previewer else None):
            if plugin.can_preview(fileobj):
                try:
                    return plugin.preview(fileobj)
                except Exception:
                    current_app.logger.warning(
                        ('Preview failed for {key}, in {pid_type}:{pid_value}'
                         .format(key=fileobj.file.key,
                                 pid_type=fileobj.pid.pid_type,
                                 pid_value=fileobj.pid.pid_value)),
                        exc_info=True)
        return default.preview(fileobj)


def zip_preview(file):
    """Return appropriate template and pass the file and an embed flag."""
    tree, limit_reached, error = make_tree(file)
    if isinstance(tree, dict):
        children = tree.pop('children', {})
        tree['children'] = {}
        for k, v in children.items():
            name = k.encode('utf-16be')
            encode = chardet.detect(name).get('encoding')
            if encode and '1252' in encode:
                name = k.encode('cp437').decode('cp932')
                v['name'] = name
                tree['children'][name] = v
            else:
                tree['children'].update({k: v})

    list = children_to_list(tree)['children']
    return render_template(
        "invenio_previewer/zip.html",
        file=file,
        tree=list,
        limit_reached=limit_reached,
        error=error,
        js_bundles=current_previewer.js_bundles + ['previewer_fullscreen_js'],
        css_bundles=current_previewer.css_bundles,
    )