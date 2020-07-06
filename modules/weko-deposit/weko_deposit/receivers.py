# -*- coding: utf-8 -*-
#
# Deposit module receivers.

from .api import WekoDeposit
from .pidstore import get_record_without_version
from weko_records.models import ItemType

def append_file_content(sender, json=None, record=None, index=None, **kwargs):
    """Append file content to ES record."""
    dep = WekoDeposit.get_record(record.id)
    pid = get_record_without_version(dep.pid)
    im = dep.copy()
    im.pop('_deposit')
    im.pop('_buckets')
    holds = ['_created', '_updated']
    pops = []
    for key in json:
        if key not in holds:
            pops.append(key)
    for key in pops:
        json.pop(key)
    json['_item_metadata'] = im
    json['_oai'] = im.get('_oai')
    json['control_number'] = im.get('control_number')
    json['relation_version_is_last'] = True \
        if pid == get_record_without_version(pid) else False
    itemtype = ItemType.query.filter(ItemType.id==im.get('item_type_id')).first()
    if itemtype:
        json['itemtype'] = itemtype.item_type_name.name
    json['path'] = im.get('path')
    json['publish_date'] = im.get('publish_date')
    json['publish_status'] = im.get('publish_status')
    json['title'] = im.get('title')
    json['weko_shared_id'] = im.get('weko_shared_id')
    json['weko_creator_id'] = im.get('owner')
    files = [f for f in dep.files]
    contents = []
    for f in files:
        content = f.obj.file.json
        content.update({"file": f.obj.file.read_file(content)})
        if content['file']:
            contents.append(content)
    json['content'] = contents
    if contents:
        kwargs['arguments']['pipeline'] = 'item-file-pipeline'
    for i in im.values():
        if isinstance(i, dict):
            if i.get('attribute_type') == 'creator':
                values = i.get('attribute_value_mlt')[0]
                creator = {}
                cnames, fnames, gnames = [], [], []
                if 'creatorNames' in values:
                    creator['creatorName'] = [n['creatorName'] for n in values['creatorNames']]
                if 'familyNames' in values:
                    creator['familyName'] = [n['familyName'] for n in values['familyNames']]
                if 'givenNames' in values:
                    creator['givenName'] = [n['givenName'] for n in values['givenNames']]
                if 'creatorAlternative' in values:
                    creator['creatorAlternative'] = \
                        [n['creatorAlternative'] for n in values['creatorAlternatives']]
                json['creator'] = creator
            elif i.get('attribute_type') == 'file':
                values = i.get('attribute_value_mlt')
                files = {}
                date, extent, mimetype = [], [], []
                for v in values:
                    date.append(v.get('date')) if 'date' in v else None
                    extent.append(v.get('filesize')[0]['value']) if 'filesize' in v else None
                    mimetype.append(v.get('format')) if 'format' in v else None
                files['date'] = date if date else None
                files['extent'] = extent if extent else None
                files['mimetype'] = mimetype if mimetype else None
                json['file'] = files
            elif i.get('attribute_name') == 'Language':
                json['language'] = [list(it.values())[0] for it in i.get('attribute_value_mlt')]
            elif i.get('attribute_name') == 'Resource Type':
                json['type'] = [it.get('resourcetype') for it in i.get('attribute_value_mlt')]
            
