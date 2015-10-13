#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *
tournament_id = 0

def testDeleteAllRecords():
    """Clean up all database records from previous run before starting a new test.
	
    """
    deleteMatches(None)
    deletePlayersInTournament(None)
    deleteAllPlayers()
    deleteAllTournaments()
    print "A. All database records can be deleted."	

def testRegisterTournament(tournamentName):
    """Create a new tournament.
	
    """
	registerTournament(tournamentName)
	
def testDuplicateTournament(tournamentName):
    """Raises an error if the tournament name already exist in the database.
	
    """
    duplicateAdded = registerTournament(tournamentName)
    if duplicateAdded:
		raise ValueError("Duplicate Tournament must not be added.")
    print "B. Was not able to add duplicate tournament as expected."

def testDeleteMatches():
    deleteMatches(tournament_id)
    print "1. Old matches can be deleted."

def testDelete():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    print "2. Player records can be deleted."

def testCount():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    c = countPlayersInTournament(tournament_id)
    if c == '0':
        raise TypeError(
            "countPlayersInTournament() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayersInTournament should return zero.")
	print "3. After deleting, countPlayersInTournament() returns zero."	

def testRegisterPlayers():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    registerPlayer(tournament_id, "Chandra Nalaar")
    c = countPlayersInTournament(tournament_id)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayersInTournament() should be 1.")
    print "4. After registering a player, countPlayersInTournament() returns 1."
	
def testRegisterCountDelete():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    registerPlayer(tournament_id,"Markov Chaney")
    registerPlayer(tournament_id, "Joe Malik")
    registerPlayer(tournament_id, "Mao Tsu-hsi")
    registerPlayer(tournament_id, "Atlanta Hope")
    c = countPlayersInTournament(tournament_id)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayersInTournament should be 4.")
    deletePlayersInTournament(tournament_id)
    c = countPlayersInTournament(tournament_id)
    if c != 0:
        raise ValueError("After deleting, countPlayersInTournament should return zero.")
    print "5. Players can be registered and deleted."

def testStandingsBeforeMatches():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    registerPlayer(tournament_id, "Melpomene Murray")
    registerPlayer(tournament_id, "Randy Schwartz")
    standings = playerStandings(tournament_id)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."

def testReportMatches():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    registerPlayer(tournament_id, "Bruno Walton")
    registerPlayer(tournament_id, "Boots O'Neal")
    registerPlayer(tournament_id, "Cathy Burton")
    registerPlayer(tournament_id, "Diane Grant")
    standings = playerStandings(tournament_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tournament_id,id1, id2)
    reportMatch(tournament_id,id3, id4)
    standings = playerStandings(tournament_id)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."

def testPairings():
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    registerPlayer(tournament_id, "Twilight Sparkle")
    registerPlayer(tournament_id, "Fluttershy")
    registerPlayer(tournament_id, "Applejack")
    registerPlayer(tournament_id, "Pinkie Pie")
    standings = playerStandings(tournament_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tournament_id,id1, id2)
    reportMatch(tournament_id,id3, id4)
    pairings = swissPairings(tournament_id)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."
	
def testMultiTournaments(tournamentName):
    """Add the same player to 2 tournaments.
	
    """
    # Register matches for 1st tournament. 
    deleteMatches(tournament_id)
    deletePlayersInTournament(tournament_id)
    registerPlayer(tournament_id, "Twilight Sparkle")
    player_id = getPlayerId("Twilight Sparkle")
	# Register matches for 2nd tournament with players already registered in 1st 
	# tournament.
    secondTournamentName = tournamentName + "-SECOND"
    registerTournament(secondTournamentName)
    secoundTournament_id = getTournamentID(secondTournamentName)
    registerPlayer(secoundTournament_id, "Twilight Sparkle")
    tournamentsOfPlayers = getTournamentsOfPlayer(player_id)
    if len(tournamentsOfPlayers) != 2:
        raise ValueError("The player must be registered to 2 matches.")
    print "9. The player is registered to 2 matches."	
	
def getTournamentNameFromUser():
    """Ask user to enter the tournament name to process.  
	
    """
	while True:
		tournamentName = raw_input('Enter tournament name:  ')
		if not tournamentName:
			print "Tournament name is required."
		else:
			break
	return tournamentName
	
if __name__ == '__main__':
    testDeleteAllRecords()
    tournamentName = getTournamentNameFromUser()
    testRegisterTournament(tournamentName)
    testDuplicateTournament(tournamentName)
    tournament_id = getTournamentID(tournamentName)
    testDeleteMatches()
    testDelete()
    testCount()
    testRegisterPlayers()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testMultiTournaments(tournamentName)
    commit()
    closeConnect()
    print "Success!  All tests pass!"


