from typing import Generator, Any, Iterator, Mapping, List

from pyairtable.airtable import Record
from airtable import Airtable
from pandas import DataFrame


class AirtableActions:
    def __init__(self, token, database):
        self._token = token
        self._database = database

    @property
    def _auth(self) -> Airtable:
        return Airtable(self._database, self._token)

    def _data_generator(self, table_name: str, fields: List[str], **kwargs) -> Iterator[Record[Mapping[str, Any]]]:
        return self._auth.iterate(table_name, fields=fields, **kwargs)

    def get_fields(self, table_name: str, fields: List[str], **kwargs) -> Generator[Mapping[str, Any], None, None]:
        for record in self._data_generator(table_name, fields, **kwargs):
            yield record["fields"]

    def get_df(self, table_name: str, fields: List[str]) -> DataFrame:
        records = [r["fields"] for r in self._auth.iterate(table_name, fields=fields)]
        data = DataFrame.from_records(records)
        return