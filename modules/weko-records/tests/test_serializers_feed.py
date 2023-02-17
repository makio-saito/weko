import pytest
import dateutil.tz
from mock import patch, MagicMock
from copy import deepcopy
from datetime import datetime, timezone
import feedgen.version
from feedgen.compat import string_types
from feedgen.feed import FeedGenerator
from feedgen.util import ensure_format, formatRFC2822
from lxml import etree

from weko_records.serializers.feed import WekoFeedGenerator

# class WekoFeedEntry(FeedEntry):
#     def atom_entry(self, extensions=True):
#     def contributor(self, contributor=None, replace=False, **kwargs):
#     def pubDate(self, pubDate=None):
#     def pubdate(self, pubDate=None):
#     def rights(self, rights=None):
#     def comments(self, comments=None):
#     def source(self, url=None, title=None):
#     def enclosure(self, url=None, length=None, type=None):
#     def ttl(self, ttl=None):
# .tox/c1/bin/pytest --cov=weko_records tests/test_serializers_entry.py::test_weko_feed_entry -v -s -vv --cov-branch --cov-report=term --cov-config=tox.ini --basetemp=/code/modules/weko-records/.tox/c1/tmp
def test_weko_feed_entry():
    feed_entry = WekoFeedEntry()
    # pubDate
    with pytest.raises(Exception) as e:
        feed_entry.pubDate(datetime(2021, 10, 1))
    assert e.type==ValueError
    assert str(e.value)=='Datetime object has no timezone info'
    # pubdate
    assert feed_entry.pubdate(datetime(2021, 10, 1, tzinfo=timezone.utc))==datetime(2021, 10, 1, tzinfo=timezone.utc)
    # rights
    assert feed_entry.rights('test rights')=='test rights'
    # comments
    assert feed_entry.comments('test comments')=='test comments'
    # source
    assert feed_entry.source('http://nii.co.jp', 'test title')=={'url': 'http://nii.co.jp', 'title': 'test title'}
    # enclosure
    assert feed_entry.enclosure('http://nii.co.jp', 100, 'pdf')=={'length': 100, 'type': 'pdf', 'url': 'http://nii.co.jp'}
    # ttl
    assert feed_entry.ttl(100)==100


def atom_entry():
    feed = etree.Element(
        'feed',
        xmlns='http://www.w3.org/2005/Atom',
        nsmap={}
    )
    return feed

def rss_entry():
    feed = etree.Element(
        'feed',
        xmlns='http://www.w3.org/2005/Atom',
        nsmap={}
    )
    return feed

data = MagicMock()
data.atom_entry = atom_entry
data.rss_entry = rss_entry

sample = WekoFeedGenerator()
sample._WekoFeedGenerator__atom_id = "test"
sample._WekoFeedGenerator__atom_title = "test"
sample._WekoFeedGenerator__atom_updated = datetime.now(dateutil.tz.tzutc())
sample._WekoFeedGenerator__atom_author = [{
    "name": "test",
    "uri": "test",
    "email": "test",
}]
sample._WekoFeedGenerator__atom_link = [{
    "href": "test",
    "rel": "test",
    "type": "test",
    "hreflang": "test",
    "title": "test",
    "length": "test",
    "rel": "rel",
}]
sample._WekoFeedGenerator__atom_category = [{
    "term": "test",
    "scheme": "test",
    "label": "test",
}]
sample._WekoFeedGenerator__atom_contributor = [{
    "name": "test",
    "contributor": "test",
    "email": "test",
    "uri": "test",
}]
sample._WekoFeedGenerator__atom_feed_xml_lang = "test"
sample._WekoFeedGenerator__atom_generator = {
    'value': 'python-feedgen',
    'uri': 'http://lkiesow.github.io/python-feedgen',
    'version': feedgen.version.version_str
}
sample._WekoFeedGenerator__atom_icon = "test"
sample._WekoFeedGenerator__atom_logo = "test"
sample._WekoFeedGenerator__atom_rights = "test"
sample._WekoFeedGenerator__atom_subtitle = "test"
sample._WekoFeedGenerator__feed_entries = [data]
sample._WekoFeedGenerator__rss_category = [{
    "value": "value",
    "domain": "domain",
}]
sample._WekoFeedGenerator__rss_cloud = {
    "domain": "domain",
    "port": "port",
    "path": "path",
    "registerProcedure": "registerProcedure",
    "protocol": "protocol",
}
sample._WekoFeedGenerator__rss_copyright = "test"
sample._WekoFeedGenerator__rss_description = "test"
sample._WekoFeedGenerator__rss_docs = 'http://www.rssboard.org/rss-specification'
sample._WekoFeedGenerator__rss_generator = 'python-feedgen'
sample._WekoFeedGenerator__rss_image = {
    "url": "url",
    "title": "title",
    "link": "link",
    "width": "width",
    "height": "height",
    "description": "description",
}
sample._WekoFeedGenerator__rss_items = "test"
sample._WekoFeedGenerator__rss_language = "test"
sample._WekoFeedGenerator__rss_lastBuildDate = datetime.now(dateutil.tz.tzutc())
sample._WekoFeedGenerator__rss_link = "test"
sample._WekoFeedGenerator__rss_managingEditor = "test"
sample._WekoFeedGenerator__rss_pubDate = datetime.now(dateutil.tz.tzutc())
sample._WekoFeedGenerator__rss_rating = "test"
sample._WekoFeedGenerator__rss_request_url = "test"
sample._WekoFeedGenerator__rss_skipDays = "test"
sample._WekoFeedGenerator__rss_skipHours = "test"
sample._WekoFeedGenerator__rss_textInput = {
    "name": "url",
    "title": "title",
    "link": "link",
    "description": "description",
}
sample._WekoFeedGenerator__rss_title = "test"
sample._WekoFeedGenerator__rss_ttl = "test"
sample._WekoFeedGenerator__rss_webMaster = "test"
sample._WekoFeedGenerator__extensions = {
    "atom": {
        "atom": "atom",
        "inst": "inst",
        "rss": "rss",
    }
}


# def _create_atom(self, extensions=True):
def test__create_atom(app):
    sample_copy = deepcopy(sample)
    data1 = MagicMock()

    def extend_ns():
        return {"test": "test"}

    data1.extend_ns = extend_ns

    sample_copy._WekoFeedGenerator__extensions["atom"]["inst"] = data1
    assert sample_copy._create_atom() != None

    sample_copy._WekoFeedGenerator__atom_contributor[0]["name"] = False
    assert sample_copy._create_atom() != None

    sample_copy._WekoFeedGenerator__atom_author[0]["name"] = False
    assert sample_copy._create_atom() != None

    # Exception coverage
    sample_copy._WekoFeedGenerator__atom_id = None
    sample_copy._WekoFeedGenerator__atom_title = None
    sample_copy._WekoFeedGenerator__atom_updated = None
    try:
        sample_copy._create_atom()
    except:
        pass


# def atom_file(self, filename, extensions=True, pretty=False, encoding='UTF-8', xml_declaration=True):
def test_atom_file(app):
    sample_copy = deepcopy(sample)
    data1 = MagicMock()
    
    def extend_ns():
        return {"test": "test"}

    data1.extend_ns = extend_ns

    sample_copy._WekoFeedGenerator__extensions["atom"]["inst"] = data1
    assert sample_copy.atom_file(filename="test") == None


# def _create_rss(self, extensions=True): 
def test__create_rss(app):
    sample_copy = deepcopy(sample)
    data1 = MagicMock()

    def extend_ns():
        return {"test": "test"}

    data1.extend_ns = extend_ns

    sample_copy._WekoFeedGenerator__extensions["atom"]["inst"] = data1
    assert sample_copy._create_rss() != None

    sample_copy._WekoFeedGenerator__atom_link[0]["rel"] = "self"
    assert sample_copy._create_rss() != None

    # Exception coverage
    sample_copy._WekoFeedGenerator__rss_title = None
    sample_copy._WekoFeedGenerator__rss_link = None
    try:
        sample_copy._create_rss()
    except:
        pass


# def rss_file(self, filename, extensions=True, pretty=False, encoding='UTF-8', xml_declaration=True): 
def test_rss_file(app):
    sample_copy = deepcopy(sample)
    data1 = MagicMock()
    
    def extend_ns():
        return {"test": "test"}

    data1.extend_ns = extend_ns

    sample_copy._WekoFeedGenerator__extensions["atom"]["inst"] = data1
    assert sample_copy.rss_file(filename="filename") == None


# def updated(self, updated=None):
def test_updated(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.updated(updated=str(sample_copy._WekoFeedGenerator__atom_updated)) != None

    # Exception coverage
    try:
        sample_copy.updated(updated=[1])
    except:
        pass
    
    # Exception coverage
    try:
        sample_copy.updated(updated=datetime(2023, 1, 1, tzinfo=None))
    except:
        pass


# def lastBuildDate(self, lastBuildDate=None): 
def test_lastBuildDate(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.lastBuildDate() != None


# def author(self, author=None, replace=False, **kwargs): 
def test_author(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.author(author=None, name='John Doe', email='jdoe@example.com', replace=True) != None
    assert sample_copy.author(author=None, name='', email='jdoe@example.com', replace=True) != None
    assert sample_copy.author() != None


# def category(self, category=None, replace=False, **kwargs):
def test_category(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.category(category=None, term="term") != None

    sample_copy._WekoFeedEntry__atom_category = None
    assert sample_copy.category(category={"term": "term", "scheme": "scheme", "label": "label"}, replace=True) != None


# def cloud(self, domain=None, port=None, path=None, registerProcedure=None, protocol=None):
def test_cloud(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.cloud(1, 2, 3, 4, 5) != None


# def contributor(self, contributor=None, replace=False, **kwargs): 
def test_contributor(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.contributor(contributor=None, name="name") != None
    assert sample_copy.contributor(contributor={"name": "name", "email": "email", "uri": "uri"}, replace=True) != None


# def generator(self, generator=None, version=None, uri=None): 
def test_generator(app):
    sample_copy = deepcopy(sample)

    assert sample_copy.generator(
        generator=sample_copy._WekoFeedGenerator__atom_generator["value"],
        version=sample_copy._WekoFeedGenerator__atom_generator["version"],
        uri=sample_copy._WekoFeedGenerator__atom_generator["uri"]
    ) != None


# def icon(self, icon=None): 
def test_icon(app):
    sample_copy = deepcopy(sample)
    
    assert sample_copy.icon(icon=True) != None


# def logo(self, logo=None):
def test_logo(app):
    sample_copy = deepcopy(sample)
    
    assert sample_copy.logo(logo=True) != None


# def image(self, url=None, title=None, link=None, width=None, height=None, description=None): 
def test_image(app):
    sample_copy = deepcopy(sample)
    
    assert sample_copy.image(
        url=True,
        title=True,
        link=True,
        width=True,
        height=True,
        description=True,
    ) != None