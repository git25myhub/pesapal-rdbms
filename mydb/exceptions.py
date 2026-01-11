class DBError(Exception):
    pass

class TableExistsError(DBError):
    pass

class TableNotFoundError(DBError):
    pass

class SchemaError(DBError):
    pass
