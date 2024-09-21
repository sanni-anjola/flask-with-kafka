
def dict_fetchone(cursor):
    """Return a single row from the cursor as a dictionary."""
    row = cursor.fetchone()
    if row is None:
        return None
    colnames = [desc[0] for desc in cursor.description]
    return dict(zip(colnames, row))

def dict_fetchall(cursor):
    """Return all rows from the cursor as a list of dictionaries."""
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in rows]