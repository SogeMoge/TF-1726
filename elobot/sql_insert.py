"""sql queries with db manipulation (insert)"""

def statement(conn, sql_querry):
    """execute querry from sql_querry statement
    :param conn: Connection object
    :param sql_querry: a SQL statement
    :return:
    """
    db_cursor = conn.cursor()
    db_cursor.execute(sql_querry)

def set_properties(conn, properties):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = """ INSERT INTO properties\
              (property_name,\
              int_value,\
              float_value,\
              char_value,\
              date_value)
              VALUES(?,?,?,?,?) """
    db_cursor = conn.cursor()
    db_cursor.execute(sql, properties)
    conn.commit()
    return db_cursor.lastrowid

def tournament_win(conn, game_result):
    """
    Submit a new game in the games table
    :param conn:
    :param win_result:
    :return: game id
    """
    sql = """ INSERT INTO games \
              (winner_id,\
              winner_score,\
              winner_rating_diff,\
              looser_id,\
              looser_score,\
              looser_rating_diff,\
              tournament,\
              game_date)
              VALUES(?,?,?,?,?,?,?,?) """
    db_cursor = conn.cursor()
    db_cursor.execute(sql, game_result)
    conn.commit()
    return db_cursor.lastrowid

def regular_win(conn, game_result):
    """
    Submit a new game in the games table
    :param conn:
    :param win_result:
    :return: game id
    """
    sql = """ INSERT INTO games \
              (winner_id,\
              winner_score,\
              winner_rating_diff,\
              looser_id,looser_score,\
              looser_rating_diff,\
              game_date)
              VALUES(?,?,?,?,?,?,?) """
    db_cursor = conn.cursor()
    db_cursor.execute(sql, game_result)
    conn.commit()
    return db_cursor.lastrowid
