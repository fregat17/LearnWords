from typing import Generator, Any, Iterator, Mapping, List

from cachetools import TTLCache, cached
from pyairtable import Table

cache = TTLCache(maxsize=1, ttl=360)


class AirtableActions:
    def __init__(self, token, database, table):
        self._token = token
        self._database = database
        self._table = table

    @property
    def _auth(self) -> Table:
        return Table(self._token, self._database, self._table)

    #@cached(cache)
    def _data_generator(self, fields: List[str], **kwargs):
        return self._auth.all(fields=fields, **kwargs)

    def get_fields_gen(self, fields: List[str], **kwargs):
        for record in self._data_generator(fields, **kwargs):
            yield record["fields"]

    def get_fields(self, fields: List[str]):
        fields_list = [entry['fields'] for entry in self._data_generator(fields) if 'fields' in entry]
        return fields_list
