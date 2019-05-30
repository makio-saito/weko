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

"""WEKO3 module docstring."""

import csv
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime
from io import BytesIO, StringIO

from flask import abort, current_app, flash, jsonify, make_response, request
from flask_admin import BaseView, expose
from flask_babelex import gettext as _
from flask_login import current_user
from weko_items_ui.utils import get_user_information
from weko_records.api import ItemsMetadata

from .permissions import admin_permission_factory
from .utils import allowed_file


class StyleSettingView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        """Block style setting page."""
        wysiwyg_editor_default = [
            '<div class="ql-editor ql-blank" data-gramm="false" '
            'contenteditable="true"><p><br></p></div>']

        body_bg = '#fff'
        panel_bg = '#fff'
        footer_default_bg = 'rgba(13,95,137,0.8)'
        navbar_default_bg = '#f8f8f8'
        panel_default_border = '#ddd'
        scss_file = os.path.join(current_app.static_folder,
                                 'css/weko_theme/_variables.scss')
        try:
            with open(scss_file, 'r', encoding='utf-8') as fp:
                for line in fp.readlines():
                    line = line.strip()
                    if '$body-bg:' in line:
                        body_bg = line[line.find('#'):-1]
                    if '$panel-bg:' in line:
                        panel_bg = line[line.find('#'):-1]
                    if '$footer-default-bg:' in line:
                        footer_default_bg = line[line.find('#'):-1]
                    if '$navbar-default-bg:' in line:
                        navbar_default_bg = line[line.find('#'):-1]
                    if '$panel-default-border:' in line:
                        panel_default_border = line[line.find('#'):-1]

            from weko_theme.views import blueprint as theme_bp

            # Header
            f_path_header_wysiwyg = os.path.join(
                theme_bp.root_path,
                theme_bp.template_folder,
                current_app.config['THEME_HEADER_WYSIWYG_TEMPLATE'])
            header_array_wysiwyg = self.get_contents(f_path_header_wysiwyg)

            f_path_header_editor = os.path.join(
                theme_bp.root_path,
                theme_bp.template_folder,
                current_app.config['THEME_HEADER_EDITOR_TEMPLATE'])

            if self.cmp_files(f_path_header_wysiwyg, f_path_header_editor):
                header_array_wysiwyg = wysiwyg_editor_default

            # Footer
            f_path_footer_wysiwyg = os.path.join(
                theme_bp.root_path,
                theme_bp.template_folder,
                current_app.config['THEME_FOOTER_WYSIWYG_TEMPLATE'])
            footer_array_wysiwyg = self.get_contents(f_path_footer_wysiwyg)

            f_path_footer_editor = os.path.join(
                theme_bp.root_path,
                theme_bp.template_folder,
                current_app.config['THEME_FOOTER_EDITOR_TEMPLATE'])

            if self.cmp_files(f_path_footer_wysiwyg, f_path_footer_editor):
                footer_array_wysiwyg = wysiwyg_editor_default

            # Color
            if request.method == 'POST':
                if not admin_permission_factory('update-style-action').can():
                    current_app.logger.debug('deny access')
                    flash(_('deny access'))
                else:
                    form_lines = []
                    body_bg = request.form.get('body-bg', '#fff')
                    panel_bg = request.form.get('panel-bg', '#fff')
                    footer_default_bg = request.form.get(
                        'footer-default-bg', 'rgba(13,95,137,0.8)')
                    navbar_default_bg = request.form.get(
                        'navbar-default-bg', '#f8f8f8')
                    panel_default_border = request.form.get(
                        'panel-default-border', '#ddd')
                    form_lines.append(
                        '$body-bg: ' + body_bg + ';')
                    form_lines.append(
                        '$panel-bg: ' + panel_bg + ';')
                    form_lines.append(
                        '$footer-default-bg: ' + footer_default_bg + ';')
                    form_lines.append(
                        '$navbar-default-bg: ' + navbar_default_bg + ';')
                    form_lines.append(
                        '$panel-default-border: ' + panel_default_border + ';')
                    form_lines.append(
                        '$input-bg-transparent: rgba(255, 255, 255, 0);')

                    with open(scss_file, 'w', encoding='utf-8') as fp:
                        fp.writelines('\n'.join(form_lines))
        except BaseException:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
        return self.render(
            current_app.config["WEKO_ADMIN_BlOCK_STYLE_TEMPLATE"],
            body_bg=body_bg,
            panel_bg=panel_bg,
            footer_default_bg=footer_default_bg,
            navbar_default_bg=navbar_default_bg,
            panel_default_border=panel_default_border,
            header_innerHtml=''.join(header_array_wysiwyg),
            footer_innerHtml=''.join(footer_array_wysiwyg)
        )

    @expose('/upload_editor', methods=['POST'])
    def upload_editor(self):
        """Upload header/footer settings from wysiwyg editor."""
        try:
            from html import unescape
            from weko_theme.views import blueprint as theme_bp
            write_path = folder_path = os.path.join(
                theme_bp.root_path, theme_bp.template_folder)
            data = request.get_json()
            temp = data.get('temp')
            wysiwyg_html = unescape(data.get('content'))

            if 'footer' == temp:
                if 'True' == str(data.get('isEmpty')):
                    read_path = os.path.join(
                        folder_path, current_app.config['THEME_FOOTER_EDITOR_TEMPLATE'])
                    wysiwyg_html = self.get_contents(read_path)

                write_path = os.path.join(folder_path,
                                          current_app.config[
                                              'THEME_FOOTER_WYSIWYG_TEMPLATE'])
            elif 'header' == temp:
                if 'True' == str(data.get('isEmpty')):
                    read_path = os.path.join(
                        folder_path, current_app.config['THEME_HEADER_EDITOR_TEMPLATE'])
                    wysiwyg_html = self.get_contents(read_path)

                write_path = os.path.join(folder_path,
                                          current_app.config[
                                              'THEME_HEADER_WYSIWYG_TEMPLATE'])
            else:
                abort(400)

            with open(write_path, 'w+', encoding='utf-8') as fp:
                fp.writelines(wysiwyg_html)
        except Exception:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
            abort(500)
        return jsonify({'code': 0, 'msg': 'success'})

    def get_contents(self, f_path):
        """Get the contents of the file."""
        array = []
        try:
            with open(f_path, 'r', encoding='utf-8') as fp:
                for line in fp.readlines():
                    array.append(line)
        except Exception:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
            abort(500)
        return array

    def cmp_files(self, f_path1, f_path2):
        """Compare the contents of the file."""
        checksum1 = ''
        checksum2 = ''
        try:
            with open(f_path1, 'rb') as fp1:
                checksum1 = hashlib.md5(fp1.read()).hexdigest()
            with open(f_path2, 'rb') as fp2:
                checksum2 = hashlib.md5(fp2.read()).hexdigest()
        except Exception:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
            abort(500)
        return checksum1 == checksum2


class ReportView(BaseView):

    @expose('/', methods=['GET'])
    def index(self):
        try:
            aggs_query = {
                "size": 0,
                "aggs": {
                    "aggs_term": {
                        "terms": {
                            "field": "publish_status",
                            "order": {"_count": "desc"}
                        }
                    }
                }
            }

            from invenio_stats.utils import get_aggregations
            aggs_results = get_aggregations('weko', aggs_query)

            total = 0
            result = {}
            if aggs_results and 'aggs_term' in aggs_results:
                for bucket in aggs_results['aggs_term']['buckets']:
                    bkt = {
                        'open': bucket['doc_count']} if bucket['key'] == '0' else {
                        'private': bucket['doc_count']}
                    result.update(bkt)
                    total = total + bucket['doc_count']

            result.update({'total': total})

            return self.render(
                current_app.config['WEKO_ADMIN_REPORT_TEMPLATE'],
                result=result,
                now=datetime.utcnow())
        except Exception:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
        return abort(400)

    @expose('/stats_file_tsv', methods=['POST'])
    def get_file_stats_tsv(self):
        """Get file download/preview stats report."""
        stats_json = json.loads(request.form.get('report'))
        file_type = request.form.get('type')
        year = request.form.get('year')
        month = request.form.get('month').zfill(2)

        # File Format: logReport_File[Download, Preview]_YYYY-MM.tsv
        tsv_files = []
        for stats_type, stats in stats_json.items():
            tsv_files.append({
                'file_name': self.make_tsv_file_name(stats_type, year, month),
                'stream': self.make_stats_tsv(stats, stats_type, year, month)})

        zip_name = 'logReport_' + year + '-' + month
        zip_stream = BytesIO()

        try:
            # Dynamically create zip from StringIO data into BytesIO
            report_zip = zipfile.ZipFile(zip_stream, 'w')
            for tsv_file in tsv_files:
                report_zip.writestr(tsv_file['file_name'],
                                    tsv_file['stream'].getvalue())
            report_zip.close()

            resp = make_response()
            resp.data = zip_stream.getvalue()
            resp.headers['Content-Type'] = 'application/x-zip-compressed'
            resp.headers['Content-Disposition'] = 'attachment; filename=' + \
                zip_name + '.zip'
        except Exception:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
            abort(500)
        return resp

    def make_stats_tsv(self, raw_stats, file_type, year, month):
        """Make TSV report file for downloads and previews."""
        sub_header_row = None
        if file_type == 'file_download':
            header_row = _('No. Of File Downloads')
            sub_header_row = _('Open-Access No. Of File Downloads')
        elif file_type == 'file_preview':
            header_row = _('No. Of File Previews')
            sub_header_row = _('Open-Access No. Of File Previews')
        elif file_type == 'index_access':
            header_row = _('Detail Views Per Index')
        elif file_type == 'detail_view':
            header_row = _('Detail screen view count')
        else:
            header_row = _('Usage count by user')

        tsv_output = StringIO()
        try:
            writer = csv.writer(tsv_output, delimiter='\t',
                                lineterminator="\n")
            writer.writerows([[header_row], [_('Aggregation Month'), year + '-' + month],
                              [''], [header_row]])

            cols = []
            if file_type == 'file_download' or file_type == 'file_preview':
                cols = [_('File Name'), _('Registered Index Name'),
                        _('No. Of Times Downloaded/Viewed'), _('Non-Logged In User'),
                        _('Logged In User'), _('Site License'), _('Admin'),
                        _('Registrar')]
            elif file_type == 'index_access':
                cols = [_('Index'), _('No. Of Views')]
            elif file_type == 'detail_view':
                cols = [_('Title'),
                        _('Registered index name'),
                        _('View count'),
                        _('Not-login user')]
            elif file_type == 'file_using_per_user':
                cols = [_('Mail address'),
                        _('Username'),
                        _('File download count'),
                        _('File playing count')]
            # All stats
            writer.writerow(cols)

            if file_type == 'index_access':  # Write total for per index views
                writer.writerow([_('Total Detail Views'), raw_stats['total']])

            self.write_report_tsv_rows(writer, raw_stats['all'], file_type)

            # Open access stats
            if sub_header_row is not None:
                writer.writerows([[''], [sub_header_row]])
                writer.writerow(cols)
                self.write_report_tsv_rows(writer, raw_stats['open_access'])
        except Exception:
            current_app.logger.error('Unexpected error: ',
                                     sys.exc_info()[0])
            abort(500)
        return tsv_output

    def write_report_tsv_rows(self, writer, records, file_type=None):
        """Write tsv rows for stats."""
        if isinstance(records, dict):
            records = list(records.values())
        for record in records:
            try:
                if file_type is None or \
                        file_type == 'file_download' or file_type == 'file_preview':
                    writer.writerow([record['file_key'], record['index_list'],
                                     record['total'], record['no_login'],
                                     record['login'], record['site_license'],
                                     record['admin'], record['reg']])
                elif file_type == 'index_access':
                    writer.writerow([record['index_name'], record['view_count']])
                elif file_type == 'detail_view':
                    item_metadata_json = ItemsMetadata.\
                        get_record(record['record_id'])
                    writer.writerow([
                        item_metadata_json['title'], record['index_names'],
                        record['total_all'], record['total_not_login']])
                elif file_type == 'file_using_per_user':
                    user_email = ''
                    user_name = 'Guest'
                    user_id = int(record['cur_user_id'])
                    if user_id > 0:
                        user_info = get_user_information(user_id)
                        user_email = user_info['email']
                        user_name = user_info['username']
                    writer.writerow([
                        user_email, user_name,
                        record['total_download'], record['total_preview']])
            except Exception:
                current_app.logger.error('Unexpected error: ',
                                         sys.exc_info()[0])
                abort(500)

    def make_tsv_file_name(self, file_type, year, month):
        """Make tsv filenames."""
        if file_type == 'file_download':
            file_type = 'FileDownload'
        elif file_type == 'file_preview':
            file_type = 'FilePreview'
        elif file_type == 'detail_view':
            file_type = 'DetailView_'
        elif file_type == 'index_access':
            file_type = 'IndexAccess_'
        else:
            file_type = 'FileUsingPerUser_'
        return 'logReport_' + file_type + year + '-' + month + '.tsv'


class LanguageSettingView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        return self.render(
            current_app.config["WEKO_ADMIN_LANG_SETTINGS"]
        )


class WebApiAccount(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        return self.render(
            current_app.config["WEKO_ADMIN_WEB_API_ACCOUNT"]
        )


style_adminview = {
    'view_class': StyleSettingView,
    'kwargs': {
        'category': _('Setting'),
        'name': _('Style'),
        'endpoint': 'stylesetting'
    }
}

report_adminview = {
    'view_class': ReportView,
    'kwargs': {
        'category': _('Statistics'),
        'name': _('Report'),
        'endpoint': 'report'
    }
}

language_adminview = {
    'view_class': LanguageSettingView,
    'kwargs': {
        'category': _('Setting'),
        'name': _('Language'),
        'endpoint': 'language'
    }
}

web_api_account_adminview = {
    'view_class': WebApiAccount,
    'kwargs': {
        'category': _('Setting'),
        'name': _('WebAPI Account'),
        'endpoint': 'webapiaccount'
    }
}

__all__ = (
    'style_adminview',
    'report_adminview',
    'language_adminview',
    'web_api_account_adminview'
)

