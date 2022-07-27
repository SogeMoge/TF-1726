##########################             ##########################
##########################  DB TABLES  ##########################
##########################             ##########################

sql_create_members_table = """CREATE TABLE IF NOT EXISTS members (
                                member_id integer UNIQUE PRIMARY KEY,
                                member_name text NOT NULL,
                                win_streak integer DEFAULT 0,
                                rating INT DEFAULT 1500
                            );"""

# To-DO CREATE STAT VIEW

sql_create_properties_table = """CREATE TABLE IF NOT EXISTS properties (
                                id integer PRIMARY KEY autoincrement,
                                property_name text NOT NULL,
                                int_value integer,
                                float_value float,
                                char_value varchar,
                                date_value date
                            );"""

sql_create_games_table = """CREATE TABLE IF NOT EXISTS games (
                                game_id integer UNIQUE PRIMARY KEY autoincrement,
                                winner_id integer REFERENCES members(member_id),
                                winner_score integer NOT NULL,
                                winner_rating_diff integer NOT NULL,
                                looser_id integer REFERENCES members(member_id),
                                looser_score integer NOT NULL,
                                looser_rating_diff integer NOT NULL,
                                tournament boolean DEFAULT FALSE,
                                fun_event boolean DEFAULT FALSE,
                                game_date date NOT NULL
                            );"""

sql_drop_members_table = """DROP TABLE members;"""

sql_drop_properties_table = """DROP TABLE properties;"""

sql_drop_games_table = """DROP TABLE games;"""