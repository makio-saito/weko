# coding:utf-8
"""Definition of publisher property."""
from .property_func import (
    get_property_schema,
    get_property_form,
    set_post_data,
    get_select_value,
    make_title_map,
)
from . import property_config as config

property_id = config.DCTERMS_EXTENT
multiple_flag = True
name_ja = "大きさ"
name_en = "Extent"
mapping = {
            "display_lang_type": "",
            "jpcoar_v1_mapping": {},
            "jpcoar_mapping": {
                "extent": {
                    "@value": "dcterms_extent",
                    "@attributes": {"xml:lang": "dcterms_extent_language"},
                }
            },
            "junii2_mapping": "",
            "lido_mapping": "",
            "lom_mapping": "",
            "oai_dc_mapping": "",
            "spase_mapping": "",
        }


def add(post_data, key, **kwargs):
    """Add to a item type."""
    option = kwargs.pop("option")
    set_post_data(post_data, property_id, name_ja, key, option, form, schema, **kwargs)

    if kwargs.pop("mapping", True):
        post_data["table_row_map"]["mapping"][key] = mapping
    else:
        post_data["table_row_map"]["mapping"][key] = config.DEFAULT_MAPPING


def schema(title="", multi_flag=multiple_flag):
    """Get schema text of item type."""

    def _schema():
        """Schema text."""
        _d = {
            "type": "object",
            "format": "object",
            "properties": {
                "dcterms_extent": {
                    "type": "string",
                    "format": "text",
                    "title": "大きさ",
                    "title_i18n": {"ja": "大きさ", "en": "Extent"},
                },
                "dcterms_extent_language": {
                    "type": "string",
                    "format": "select",
                    "enum": config.LANGUAGE_VAL2_1,
                    "currentEnum": config.LANGUAGE_VAL2_1,
                    "title": "Language",
                    "title_i18n": {"ja": "言語", "en": "Language"},
                },
            },
        }
        return _d

    return get_property_schema(title, _schema, multi_flag)


def form(
    key="", title="", title_ja=name_ja, title_en=name_en, multi_flag=multiple_flag
):
    """Get form text of item type."""

    def _form(key):
        """Form text."""
        _d = {
            "items": [
                {
                    "key": "{}.dcterms_extent".format(key),
                    "type": "text",
                    "title": "Extent",
                    "title_i18n": {"ja": "大きさ", "en": "Extent"},
                },
                {
                    "key": "{}.dcterms_extent_language".format(key),
                    "type": "select",
                    "title": "Language",
                    "title_i18n": {"ja": "言語", "en": "Language"},
                    "titleMap": get_select_value(config.LANGUAGE_VAL2_1),
                },
            ],
            "key": key.replace("[]", ""),
        }
        return _d

    return get_property_form(key, title, title_ja, title_en, multi_flag, _form)
