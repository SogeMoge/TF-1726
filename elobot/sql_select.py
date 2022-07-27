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