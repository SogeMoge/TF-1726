def drop_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def drop_table(conn, drop_table_sql):
    """drop a table from the drop_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a DROP TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(drop_table_sql)
    except Error as e:
        print(e)