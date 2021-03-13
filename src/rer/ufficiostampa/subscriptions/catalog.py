# -*- coding: utf-8 -*-
# from collective.volto.formsupport.interfaces import IFormDataStore
from datetime import datetime
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer import json_body
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from souper.interfaces import ICatalogFactory
from souper.soup import get_soup
from souper.soup import NodeAttributeIndexer
from souper.soup import Record
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from repoze.catalog.indexes.text import CatalogTextIndex
from souper.soup import NodeTextIndexer
from repoze.catalog.indexes.keyword import CatalogKeywordIndex

import logging

logger = logging.getLogger(__name__)


@implementer(ICatalogFactory)
class SubscriptionsSoupCatalogFactory(object):
    def __call__(self, context):
        catalog = Catalog()
        fullname_indexer = NodeTextIndexer(["name", "surname"])
        catalog[u"fullname"] = CatalogTextIndex(fullname_indexer)
        mail_indexer = NodeAttributeIndexer("email")
        catalog[u"email"] = CatalogFieldIndex(mail_indexer)
        mail_indexer = NodeAttributeIndexer("email")
        catalog[u"email"] = CatalogFieldIndex(mail_indexer)
        channels_indexer = NodeAttributeIndexer("channels")
        catalog[u"channels"] = CatalogKeywordIndex(channels_indexer)
        return catalog
