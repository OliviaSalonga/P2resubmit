#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

conn = psycopg2.connect("dbname='tournament'")
cur = conn.cursor()

def commit():
    """Permanently post all changes to the database.
	
    """
	conn.commit()
	
def closeConnect():
    """Close cursor & connection to free system resources.
	
    """
	cur.close()
	conn.close()

def deleteMatches(tournament_id):
    """Remove the match records for the tournament or matches from the database.
	
	Args:
	  tournament_id: the tournament's ID currently being processed.
					 If tournament_id is None, all records in the table are deleted.
	"""	
    if tournament_id is None:
		cur.execute("DELETE FROM matchResults")	
    else:		
		cur.execute("DELETE FROM matchResults WHERE tournament_id = %s", (tournament_id,))	
		
def deletePlayersInTournament(tournament_id):
    """Remove all players in the tournament or all players from the database.
	
	Args:
	  tournament_id: the tournament's ID currently being processed.  
	                 If "None" is passed, all records will be deleted from the table.
	"""
    if tournament_id is None:
		cur.execute("DELETE FROM playersInTournament")
    else: 		
		cur.execute("DELETE FROM playersInTournament WHERE tournament_id = %s", (tournament_id,))

def deleteAllPlayers():
    """Remove all players from the database.
	
    """
    cur.execute("DELETE FROM players")
	
def deleteAllTournaments():
    """Remove all tournaments from the database.
	"""
    cur.execute("DELETE FROM tournaments")	
		
def countPlayersInTournament(tournament_id):
	"""Returns the number of players currently registered in the tournament.
	
	Args:
	  tournament_id: the tournament's ID currently being processed
	"""
	cur.execute("SELECT count(*) FROM playersInTournament WHERE tournament_id = %s", (tournament_id,))
	playersCount = cur.fetchone()
	return playersCount[0]	

def registerPlayer(tournament_id, playerName):
    """Adds a player to the tournament database and the player to the current tournament being processed.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

	A player can be part of several tournaments. A player can only be added to the tournament once.
	This method checks that a player is only registered to the tournament once.  Also, the	
	playersInTournament has unique constraint to check this as well. 
	
    Args:
	  tournament_id: the tournament's ID currently being processed
      name: the player's full name (need not be unique).
    """
    newPlayerAdded = False
    player_id = getPlayerId(playerName)
    if player_id is None:
		cur.execute("INSERT INTO players (name) VALUES (%s)", (playerName,))
		player_id = getPlayerId(playerName)
		newPlayerAdded = True
    if newPlayerAdded:
		cur.execute("INSERT INTO playersInTournament (tournament_id, player_id) VALUES (%s,%s)", 
		(tournament_id, player_id,))
    else: 
		recordCount = countPlayersInTournmentForPlayer(tournament_id, player_id)
		if recordCount == 0: 
			cur.execute("INSERT INTO playersInTournament (tournament_id, player_id) VALUES (%s,%s)", 
			(tournament_id, player_id,))
	
def countPlayersInTournmentForPlayer(tournament_id,player_id):
    cur.execute("SELECT count(*) FROM playersInTournament WHERE tournament_id = %s AND player_id = %s",
	(tournament_id, player_id,))
    recordCount = cur.fetchone()
    return recordCount[0]
	
def getTournamentsOfPlayer(player_id):
    cur.execute("SELECT * FROM playersInTournament WHERE player_id = %s",
	(player_id,))
    tournamentsOfPlayers = cur.fetchall()
    return tournamentsOfPlayers	
		
def getPlayerId(name):
    """Finds the player ID given the name.
 
    Args:
      name: the player's name.
    """
    player_id = 0
    cur.execute("SELECT player_id FROM players WHERE name = %s", (name,))
    player_id = cur.fetchone()
    cur.execute("SELECT * FROM players")
    players = cur.fetchall()	
    return player_id
	
def playerStandings(tournament_id):
    """Returns a list of the players in the tournament and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
	tied for first place if there is currently a tie.
	
	Args:
	  tournament_id: the tournament's ID currently being processed
	
	Returns:
	    A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    stmt = ('SELECT a.player_id, name, count(b.*) AS wins, count(c.*) AS matches ',
     'FROM players x, playersInTournament a ', 
     'LEFT JOIN matchResults b ', 
     'ON a.player_id = b.winner ',  
     'AND a.tournament_id = b.tournament_id ', 
     'LEFT JOIN matchResults c ',
     'ON (a.player_id = c.playerOne OR a.player_id = c.playerTwo) ', 
     'AND a.tournament_id = c.tournament_id ', 
     'WHERE a.tournament_id = %s ',
     'AND x.player_id = a.player_id ',	 
     'GROUP BY a.player_id, name ',
     'ORDER BY wins DESC')
    cur.execute(''.join(stmt), (tournament_id,))
    standings = cur.fetchall()
    return standings

def reportMatch(tournament_id, winner, loser):
    """Records the outcome of a single match between two players in the tournament.

    Args:
	  tournament_id: the tournament's ID currently being processed
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    cur.execute("INSERT INTO matchResults (tournament_id, playerOne, playerTwo, winner) VALUES (%s,%s,%s,%s) RETURNING match_id",(tournament_id, winner, loser, winner,))
		
def swissPairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match in the tournament.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
	
	Args:
	  tournament_id: the tournament's ID currently being processed
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
	
    pairingCount = 0
    playerCount = 0
    standings = playerStandings(tournament_id)
    nbrOfPairs = len(standings) / 2
    pairings = [[]for x in range(nbrOfPairs)]	
	
    for standing in standings:	
		if playerCount == 0:
			pairings[pairingCount].append(standing[0])
			pairings[pairingCount].append(standing[1])
			playerCount += 1
		else:
			pairings[pairingCount].append(standing[0])
			pairings[pairingCount].append(standing[1])
			playerCount = 0
			pairingCount += 1			
    return pairings					
	
def registerTournament(name):
    """Adds a tournament to the tournament database.The database assigns a unique serial id number for the tournament.  (This 
	should be handled by your SQL database schema, not in your Python code.)
	
	Tournament name must be unique.  This method and the Tournament table unique constraint
	ensures unique Tournament name.
	
	Args:
      name: the tournament name
    """
    cur.execute("SELECT count(*) FROM tournaments WHERE tournamentName = %s", (name,))
    recordCount = cur.fetchone()
    count = recordCount[0]
    if count > 0:
        return False
    else:
		cur.execute("INSERT INTO tournaments (tournamentName) VALUES (%s)", (name,))
		return True

		
def getTournamentID(name):	
    """Finds the tournament ID given the tournament name.
	
	Returns:
      name: the tournament name
    """
    cur.execute("SELECT tournament_id FROM tournaments WHERE tournamentName = %s", (name,))
    tournament_id = cur.fetchone()
    return tournament_id
	
	


