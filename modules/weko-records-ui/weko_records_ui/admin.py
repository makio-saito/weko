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

import sys
import unicodedata
from datetime import datetime

from flask import abort, current_app, flash, request
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import rules
from flask_babelex import gettext as _
from flask_login import current_user
from invenio_communities.models import Community
from invenio_db import db
from sqlalchemy.orm import load_only
from werkzeug.local import LocalProxy
from wtforms.fields import StringField
from wtforms.validators import ValidationError

from . import config
from .models import Identifier, InstitutionName, PDFCoverPageSettings

_app = LocalProxy(lambda: current_app.extensions['weko-admin'].app)


class ItemSettingView(BaseView):
    """Item setting view."""

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        """Index."""
        try:
            email_display_flg = '0'
            search_author_flg = 'name'
            if current_app.config['EMAIL_DISPLAY_FLG']:
                email_display_flg = '1'
            if 'ITEM_SEARCH_FLG' in current_app.config:
                search_author_flg = current_app.config['ITEM_SEARCH_FLG']

            if request.method == 'POST':
                # Process forms
                form = request.form.get('submit', None)
                if form == 'set_search_author_form':
                    search_author_flg = request.form.get(
                        'searchRadios', 'name')
                    _app.config['ITEM_SEARCH_FLG'] = search_author_flg
                    email_display_flg = request.form.get('displayRadios', '0')
                    if email_display_flg == '1':
                        _app.config['EMAIL_DISPLAY_FLG'] = True
                    else:
                        _app.config['EMAIL_DISPLAY_FLG'] = False
                    flash(_('Author flag was updated.'), category='success')

            return self.render(config.ADMIN_SET_ITEM_TEMPLATE,
                               search_author_flg=search_author_flg,
                               email_display_flg=email_display_flg)
        except BaseException:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
        return abort(400)


class PdfCoverPageSettingView(BaseView):
    """PdfCover Page settings."""

    @expose('/', methods=['GET'])
    def index(self):
        """Index."""
        db.create_all()
        record = PDFCoverPageSettings.find(1)
        try:
            return self.render(
                current_app.config["WEKO_ADMIN_PDFCOVERPAGE_TEMPLATE"],
                avail=record.avail,
                header_display_type=record.header_display_type,
                header_output_string=record.header_output_string,
                header_output_image=record.header_output_image,
                header_display_position=record.header_display_position
            )
        except AttributeError:
            makeshift = PDFCoverPageSettings(
                avail='disable',
                header_display_type=None,
                header_output_string=None,
                header_output_image=None,
                header_display_position=None)
            db.session.add(makeshift)
            db.session.commit()
            record = PDFCoverPageSettings.find(1)
            return self.render(
                current_app.config["WEKO_ADMIN_PDFCOVERPAGE_TEMPLATE"],
                avail=record.avail,
                header_display_type=record.header_display_type,
                header_output_string=record.header_output_string,
                header_output_image=record.header_output_image,
                header_display_position=record.header_display_position
            )


class InstitutionNameSettingView(BaseView):
    """Institution Names Setting."""

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        """Index."""
        if request.method == 'POST':
            rf = request.form.to_dict()
            InstitutionName.set_institution_name(rf['institution_name'])
        institution_name = InstitutionName.get_institution_name()
        return self.render(config.INSTITUTION_NAME_SETTING_TEMPLATE,
                           institution_name=institution_name)


institution_adminview = {
    'view_class': InstitutionNameSettingView,
    'kwargs': {
        'category': _('Setting'),
        'name': _('Others'),
        'endpoint': 'others'
    }
}

item_adminview = {
    'view_class': ItemSettingView,
    'kwargs': {
        'category': _('Setting'),
        'name': _('Items'),
        'endpoint': 'itemsetting'
    }
}

pdfcoverpage_adminview = {
    'view_class': PdfCoverPageSettingView,
    'kwargs': {
        'category': _('Setting'),
        'name': _('PDF Cover Page'),
        'endpoint': 'pdfcoverpage'
    }
}


class IdentifierSettingView(ModelView):
    """Pidstore Identifier admin view."""

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    create_template = config.WEKO_PIDSTORE_IDENTIFIER_TEMPLATE_CREATOR
    edit_template = config.WEKO_PIDSTORE_IDENTIFIER_TEMPLATE_EDITOR

    column_list = (
        'repository', 'jalc_doi', 'jalc_crossref_doi', 'jalc_datacite_doi',
        'cnri',
        'suffix',
        'jalc_flag',
        'jalc_crossref_flag',
        'jalc_datacite_flag',
        'cnri_flag',)

    column_searchable_list = (
        'repository', 'jalc_doi', 'jalc_crossref_doi', 'jalc_datacite_doi',
        'cnri',
        'suffix')

    column_details_list = (
        'repository', 'jalc_doi', 'jalc_crossref_doi', 'jalc_datacite_doi',
        'cnri',
        'suffix', 'created_userId', 'created_date', 'updated_userId',
        'updated_date')

    form_extra_fields = {
        'repo_selected': StringField('Repository Selector'),
    }

    form_create_rules = [rules.Header(_('Prefix')),
                         'repository',
                         'jalc_doi',
                         'jalc_crossref_doi',
                         'jalc_datacite_doi',
                         'cnri',
                         rules.Header(_('Suffix')),
                         'suffix',
                         rules.Header(_('Enable/Disable')),
                         'jalc_flag',
                         'jalc_crossref_flag',
                         'jalc_datacite_flag',
                         'cnri_flag',
                         'repo_selected',
                         ]

    form_edit_rules = form_create_rules

    column_labels = dict(repository=_('Repository'), jalc_doi=_('JaLC DOI'),
                         jalc_crossref_doi=_('JaLC CrossRef DOI'),
                         jalc_datacite_doi=_('JaLC DataCite DOI'),
                         cnri=_('CNRI'),
                         suffix=_('Semi-automatic Suffix')
                         )

    def _validator_halfwidth_input(form, field):
        """
        Valid input character set.

        :param form: Form used to create/update model
        :param field: Template fields contain data need validator
        """
        if field.data is None:
            return
        else:
            try:
                for inchar in field.data:
                    if unicodedata.east_asian_width(inchar) in 'FWA':
                        raise ValidationError(
                            _('Only allow halfwith 1-bytes character in input'))
            except Exception as ex:
                raise ValidationError('{}'.format(ex))

    form_args = {
        'jalc_doi': {
            'validators': [_validator_halfwidth_input]
        },
        'jalc_crossref_doi': {
            'validators': [_validator_halfwidth_input]
        },
        'jalc_datacite_doi': {
            'validators': [_validator_halfwidth_input]
        },
        'cnri': {
            'validators': [_validator_halfwidth_input]
        },
        'suffix': {
            'validators': [_validator_halfwidth_input]
        }
    }

    form_widget_args = {
        'jalc_doi': {
            'maxlength': 100,
            'readonly': True,
        },
        'jalc_crossref_doi': {
            'maxlength': 100,
            'readonly': True,
        },
        'jalc_datacite_doi': {
            'maxlength': 100,
            'readonly': True,
        },
        'cnri': {
            'maxlength': 100,
            'readonly': True,
        },
        'suffix': {
            'maxlength': 100,
        }
    }

    form_overrides = {
        'repository': QuerySelectField,
    }

    def on_model_change(self, form, model, is_created):
        """
        Perform some actions before a model is created or updated.

        Called from create_model and update_model in the same transaction
        (if it has any meaning for a store backend).
        By default does nothing.

        :param form: Form used to create/update model
        :param model: Model that will be created/updated
        :param is_created: Will be set to True if model was created and to False if edited
        """
        # Update hidden data automation
        if is_created:
            model.created_userId = current_user.get_id()
            model.created_date = datetime.utcnow().replace(microsecond=0)
        model.updated_userId = current_user.get_id()
        model.updated_date = datetime.utcnow().replace(microsecond=0)
        model.repository = str(model.repository.id)
        pass

    def on_form_prefill(self, form, id):
        form.repo_selected.data = form.repository.data
        pass

    def create_form(self, obj=None):
        """
        Instantiate model delete form and return it.

        Override to implement custom behavior.
        The delete form originally used a GET request, so delete_form
        accepts both GET and POST request for backwards compatibility.

        :param obj: input object
        """
        return self._use_append_repository(
            super(IdentifierSettingView, self).create_form()
        )

    def edit_form(self, obj):
        """
        Instantiate model editing form and return it.

        Override to implement custom behavior.

        :param obj: input object
        """
        return self._use_append_repository(
            super(IdentifierSettingView, self).edit_form(obj)
        )

    def _use_append_repository(self, form):
        form.repository.query_factory = self._get_community_list
        form.repo_selected.data = 'Root Index'
        return form

    def _get_community_list(self):
        try:
            query_data = Community.query.all()
            query_data.insert(0, Community(id='Root Index'))
        except Exception as ex:
            current_app.logger.debug(ex)

        return query_data


identifier_adminview = dict(
    modelview=IdentifierSettingView,
    model=Identifier,
    category=_('Setting'),
    name=_('Identifier'),
)

__all__ = (
    'pdfcoverpage_adminview',
    'PdfCoverPageSettingView',
    'item_adminview',
    'ItemSettingView',
    'institution_adminview',
    'InstitutionNameSettingView'
)

