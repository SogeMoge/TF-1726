def member(conn, rating):
    """
    update member's rating and streak
    :param conn:
    :param rating:
    :return: project id
    """
    sql = """ UPDATE members
              SET rating = ?
              WHERE member_id = ?"""
    cur = conn.cursor()
    cur.execute(sql, rating)
    conn.commit()