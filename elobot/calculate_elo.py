def calculate_delta_points(opponent_rating, member_rating):
    """
    Compute delta points for opponents
    :param opponent_rating: current opponent rating
    :param member_rating: current player ratng
    """
    E = round(
        1 / (1 + 10 ** ((opponent_rating - member_rating) / 400)), 2
    )
    return E


def calculate_rating(win, K, R, E):
    """
    Compute new rating
    :param win: 1 for win, 0 for loss
    :param K: K property extracted from DB
    :param R: current rating of player
    :param E: delta poins of player
    """
    Rn = round(R + K * (win - E), 2)
    return Rn