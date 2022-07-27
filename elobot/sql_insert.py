def statement(conn, sql_querry):
    """execute querry from sql_querry statement
    :param conn: Connection object
    :param sql_querry: a SQL statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_querry)
    except Error as e:
        print(e)

def set_properties(conn, properties):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = """ INSERT INTO properties(property_name,int_value,float_value,char_value,date_value)
              VALUES(?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, properties)
    conn.commit()
    return cur.lastrowid

def tournament_win(conn, game_result):
    """
    Submit a new game in the games table
    :param conn:
    :param win_result:
    :return: game id
    """
    sql = """ INSERT INTO games (winner_id,winner_score,winner_rating_diff,looser_id,looser_score,looser_rating_diff,tournament,game_date)
              VALUES(?,?,?,?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, game_result)
    conn.commit()
    return cur.lastrowid

def regular_win(conn, game_result):
    """
    Submit a new game in the games table
    :param conn:
    :param win_result:
    :return: game id
    """
    sql = """ INSERT INTO games (winner_id,winner_score,winner_rating_diff,looser_id,looser_score,looser_rating_diff,game_date)
              VALUES(?,?,?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, game_result)
    conn.commit()
    return cur.lastrowid