from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer
from souper.soup import NodeTextIndexer
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


@implementer(ICatalogFactory)
class SubscriptionsSoupCatalogFactory:
    def __call__(self, context):
        catalog = Catalog()
        text_indexer = NodeTextIndexer(["name", "surname", "email"])
        catalog["text"] = CatalogTextIndex(text_indexer)
        email_indexer = NodeAttributeIndexer("email")
        catalog["email"] = CatalogFieldIndex(email_indexer)
        name_indexer = NodeAttributeIndexer("name")
        catalog["name"] = CatalogFieldIndex(name_indexer)
        surname_indexer = NodeAttributeIndexer("surname")
        catalog["surname"] = CatalogFieldIndex(surname_indexer)
        channels_indexer = NodeAttributeIndexer("channels")
        catalog["channels"] = CatalogKeywordIndex(channels_indexer)
        date_indexer = NodeAttributeIndexer("date")
        catalog["date"] = CatalogFieldIndex(date_indexer)
        newspaper_indexer = NodeAttributeIndexer("newspaper")
        catalog["newspaper"] = CatalogFieldIndex(newspaper_indexer)
        return catalog


@implementer(ICatalogFactory)
class SendHistorySoupCatalogFactory:
    def __call__(self, context):
        catalog = Catalog()
        channels_indexer = NodeAttributeIndexer("channels")
        catalog["channels"] = CatalogKeywordIndex(channels_indexer)
        date_indexer = NodeAttributeIndexer("date")
        catalog["date"] = CatalogFieldIndex(date_indexer)
        title_indexer = NodeAttributeIndexer("title")
        catalog["title"] = CatalogTextIndex(title_indexer)
        type_indexer = NodeAttributeIndexer("type")
        catalog["type"] = CatalogFieldIndex(type_indexer)
        return catalog
