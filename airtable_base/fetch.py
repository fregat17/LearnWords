from typing import Generator, Any, Iterator, Mapping, List

from pyairtable import Table
from pandas import DataFrame


class AirtableActions:
    def __init__(self, token, database, table):
        self._token = token
        self._database = database
        self._table = table

    @property
    def _auth(self) -> Table:
        return Table(self._token, self._database, self._table)

    def _data_generator(self, fields: List[str], **kwargs):
        return self._auth.all(fields=fields, **kwargs)

    def get_fields(self, fields: List[str], **kwargs):
        for record in self._data_generator(fields, **kwargs):
            yield record["fields"]

    def get_df(self, fields: List[str]) -> DataFrame:
        records = [r["fields"] for r in self._auth.all(fields=fields)]
        data = DataFrame.from_records(records)
        return data
