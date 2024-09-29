from datetime import datetime

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

def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_dates(value) for key, value in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj