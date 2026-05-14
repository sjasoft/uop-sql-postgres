from psycopg.types.json import Json
from uop.sql.base import table as base


class Table(base.Table):
    def named_parameter(self, name):
        return f"%({name})s"

    def json_serialize(self, args):
        res = {}
        for k, v in args.items():
            if self._uop_types.get(k) == "json":
                res[k] = Json(v)
            else:
                res[k] = v
        return res

    def all_tables_string(self):
        return "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
