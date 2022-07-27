##########################                ##########################
##########################  DB PROPERTIES ##########################
##########################                ##########################

sql_drop_members_table = """DROP TABLE members;"""

sql_drop_properties_table = """DROP TABLE properties;"""

sql_drop_games_table = """DROP TABLE games;"""

k_regular_properties = ("k_regular", 16, None, None, None)

k_tournament_properties = ("k_tournament", 32, None, None, None)

pt_fun_event_win_properties = ("pt_fun_event_win", 16, None, None, None)

pt_fun_event_participation_properties = (
    "pt_fun_event_participation",
    8,
    None,
    None,
    None,
)

num_mutual_games = ("mutual_games", 10, None, None, None)

num_minimal_games = ("minimal_games", 1, None, None, None)