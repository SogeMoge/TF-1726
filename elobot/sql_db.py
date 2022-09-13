"""drop tables queries"""

def create_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    db_connect = conn.cursor()
    db_connect.execute(create_table_sql)

def drop_table(conn, drop_table_sql):
    """drop a table from the drop_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a DROP TABLE statement
    :return:
    """
    db_connect = conn.cursor()
    db_connect.execute(drop_table_sql)
