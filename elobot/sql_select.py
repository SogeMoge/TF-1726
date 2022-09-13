"""select queries"""

def rating_position(conn, member_id):
    """
    Select current rating position for author
    :param member_id: author of the command
    """
    cur = conn.cursor()
    sql = f""" SELECT COUNT(member_id)
              FROM members
              WHERE rating >= (SELECT rating
                               FROM members
                               WHERE member_id = {member_id})
              """
    cur.execute(sql)
    return cur.fetchone()[0]

def rating(conn, member_id):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param member_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT rating FROM members WHERE member_id=?", (member_id,)
    )

    return cur.fetchone()[0]

def k_regular(conn):
    """
    Query date
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT int_value FROM properties WHERE property_name = 'k_regular'"
    )

    return cur.fetchone()[0]

def k_tournament(conn):
    """
    Query date
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT int_value FROM properties WHERE property_name = 'k_tournament'"
    )

    return cur.fetchone()[0]

def mutual_games_property(conn):
    """
    Query mutual games
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT int_value FROM properties WHERE property_name = 'mutual_games'"
    )

    return cur.fetchone()[0]

def minimal_games_property(conn):
    """
    Query minimal number of games
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT int_value FROM properties WHERE property_name = 'minimal_games'"
    )

    return cur.fetchone()[0]

def fun_event_participation_points(conn):
    """
    Query prize points for fn event participation
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT int_value FROM properties WHERE property_name = 'pt_fun_event_participation'"
    )

    return cur.fetchone()[0]

def fun_event_win_points(conn):
    """
    Query prize points for fn event win
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT int_value FROM properties WHERE property_name = 'pt_fun_event_win'"
    )

    return cur.fetchone()[0]

def mutual_games_played(conn, author_id, member_id):
    """
    Query mutual games played with mentioned user
    :param conn: the Connection object
    :param author_id: author of the command
    :param member_id: member to check
    :return:
    """
    cur = conn.cursor()
    sql = f""" SELECT COUNT(game_id)
               FROM games 
               WHERE tournament = 0
               AND fun_event = 0
               AND ((winner_id = {author_id} AND looser_id = {member_id}) OR (winner_id = {member_id} AND looser_id = {author_id}));
           """
    cur.execute(sql)
    return cur.fetchone()[0]

def curr_date(conn):
    """
    Query date
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT datetime('now', 'localtime')")

    return cur.fetchone()[0]

def member_stats(conn, member_id):
    """
    Select and print league statistics for member
    "param member_id: get stats for ctx.author.id
    """
    sql_win = f""" SELECT count(g.winner_id) cnt_win
                   FROM  members m 
                   LEFT JOIN games g ON m.member_id=g.winner_id
                   WHERE 1=1
                   AND g.fun_event = 0
                   AND m.member_id={member_id} """
    cur_w = conn.cursor()
    cur_w.execute(sql_win)
    cnt_win = cur_w.fetchone()[0]

    sql_loss = f"""SELECT count(g.looser_id) cnt_loose
                   FROM  members m 
                   LEFT JOIN games g ON m.member_id=g.looser_id
                   WHERE 1=1
                   AND g.fun_event = 0
                   AND m.member_id={member_id} """
    cur_l = conn.cursor()
    cur_l.execute(sql_loss)
    cnt_loss = cur_l.fetchone()[0]

    if cnt_win + cnt_loss > 0:
        winrate = int(round(cnt_win / (cnt_win + cnt_loss) * 100, 0))

        sql = f""" SELECT member_id, rating, {cnt_win} , {cnt_loss}, {winrate}
                   from members
                   where 1=1
                   and member_id={member_id}; """
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    sql = f""" SELECT member_id, rating, {cnt_win} , {cnt_loss}, 0
               from members
               where 1=1
               and member_id={member_id}; """
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows
