"""db table create and drop qieries"""

SQL_CREATE_MEMBERS_TABLE = """CREATE TABLE IF NOT EXISTS members (
                                member_id integer UNIQUE PRIMARY KEY,
                                member_name text NOT NULL,
                                win_streak integer DEFAULT 0,
                                rating INT DEFAULT 1500
                            );"""

# To-DO CREATE STAT VIEW

SQL_CREATE_PROPERTIES_TABLE = """CREATE TABLE IF NOT EXISTS properties (
                                id integer PRIMARY KEY autoincrement,
                                property_name text NOT NULL,
                                int_value integer,
                                float_value float,
                                char_value varchar,
                                date_value date
                            );"""

SQL_CREATE_GAMES_TABLE = """CREATE TABLE IF NOT EXISTS games (
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

SQL_DROP_MEMBERS_TABLE = """DROP TABLE members;"""

SQL_DROP_PROPERTIES_TABLE = """DROP TABLE properties;"""

SQL_DROP_GAMES_TABLE = """DROP TABLE games;"""
