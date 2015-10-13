-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE tournaments 
(
tournament_id serial PRIMARY KEY,
tournamentName varchar(255) NOT NULL UNIQUE
);

CREATE TABLE players
(
player_id serial PRIMARY KEY,
name varchar(255) NOT NULL
);

CREATE TABLE playersInTournament
(
tournament_id int NOT NULL REFERENCES tournaments(tournament_id),
player_id int NOT NULL REFERENCES players(player_id),
PRIMARY KEY (tournament_id, player_id) 
);

CREATE TABLE matchResults
(
match_id serial PRIMARY KEY,
tournament_id int NOT NULL REFERENCES tournaments(tournament_id),
playerOne int NOT NULL REFERENCES players(player_id),
playerTwo int NOT NULL REFERENCES players(player_id),  
winner int,
UNIQUE (tournament_id, playerOne, playerTwo)
);





