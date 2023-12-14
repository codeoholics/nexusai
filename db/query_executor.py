from enum import Enum

import psycopg2

from db import db_client
from db.db_client import get_conn


class RowColumnType(Enum):
    ONE_ROW_ONE_COLUMN = "ONE_ROW_ONE_COLUMN"
    ONE_ROW_MULTIPLE_COLUMN = "ONE_ROW_MULTIPLE_COLUMN"
    MULTIPLE_ROWS_ONE_COLUMN = "MULTIPLE_ROWS_ONE_COLUMN"
    MULTIPLE_ROWS_MULTIPLE_COLUMN = "MULTIPLE_ROWS_MULTIPLE_COLUMN"
    NO_DATA = "NO_DATA"

def execute_fetch_query(query):

    cursor = db_client.get_conn().cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    rows = cursor.fetchall()

    result = [{key: value for key, value in row.items()} for row in rows]

    # Close the cursor and db_client.get_conn()ection
    cursor.close()

    return result

def analyze_rows(rows):
    """
    Analyzes the structure of the provided rows and returns the corresponding enum value.

    Args:
        rows (List[Dict[str, Any]]): Rows returned from the database.

    Returns:
        RowColumnType: An enum indicating the structure of the rows.
    """

    # Check if there are no rows or rows is None
    if not rows:
        return RowColumnType.NO_DATA

    # Check if there's only one row
    if len(rows) == 1:
        # Check if the single row has only one column
        if len(rows[0]) == 1:
            return RowColumnType.ONE_ROW_ONE_COLUMN
        # Else, it has multiple columns
        else:
            return RowColumnType.ONE_ROW_MULTIPLE_COLUMN

    # Check if there are multiple rows but only one column
    if all(len(row) == 1 for row in rows):
        return RowColumnType.MULTIPLE_ROWS_ONE_COLUMN

    # If none of the above, then it's multiple rows with multiple columns
    return RowColumnType.MULTIPLE_ROWS_MULTIPLE_COLUMN


def fetch_one(query):
    cursor = get_conn().cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    count = cursor.fetchone()[0]

    # Close the cursor and db_client.get_conn()ection
    cursor.close()

    return count

