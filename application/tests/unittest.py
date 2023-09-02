import unittest
from ..engine import *


class TestApp(unittest.TestCase):
    
    def test_topScorers(self):
        self.assertEqual(topScorers(), (['ROMA', 'AUBAMEYANG', 'AGUERO', 'STERLING', 'RODRíGUEZ', 'POGBA', 'ANDRADE', 'FIRMINO', 'LUKAKU', 'MILIVOJEVI_�'], [30, 22, 21, 17, 13, 13, 13, 12, 12, 12]))

    def test_mostWins(self):
        self.assertEqual(mostWins(), (['MANCHESTER CITY', 'LIVERPOOL FC', 'TOTTENHAM HOTSPUR', 'CHELSEA FC', 'MANCHESTER UNITED', 'WOLVERHAMPTON WANDERERS', 'EVERTON FC', 'LEICESTER CITY', 'WEST HAM HAM', 'CRYSTAL PALACE'], [32, 30, 23, 21, 19, 16, 15, 15, 15, 14]))

    def test_teamsRank(self):
        t1 = 'LIVERPOOL FC'
        t2 = 'WOLVERHAMPTON WANDERERS FC'
        t3 = 'LEICESTER CITY FC'
        self.assertEqual(teamsRank(t1), 2)
        self.assertEqual(teamsRank(t2), 6)
        self.assertEqual(teamsRank(t3), 8)

    def test_playerRank(self):
        p1 = 'RICCARDO ROMA'
        p2 = "N'GOLO KANTé"
        p3 = 'ORIOL ROMEU'
        self.assertEqual(playerRank(p1), 1)
        self.assertEqual(playerRank(p2), 25)
        self.assertEqual(playerRank(p3), 83)

    def test_myStats(self):
        p1 = 'RICCARDO ROMA'
        p2 = "N'GOLO KANTÉ"
        p3 = 'ORIOL ROMEU'
        labels = ['Total Apperances', 'Total Goals', 'Total Assist', 'Penalty Scored', 'Penalty Missed', 'Clean Sheets', 'Yellow Cards', 'Red Cards']
        self.assertEqual(myStats(p1), (labels, [10, 30, 20, 2, 1, 8, 3, 7]))
        self.assertEqual(myStats(p2), (labels, [36, 4, 4, 0, 0, 15, 3, 0]))
        self.assertEqual(myStats(p3), (labels, [31, 1, 0, 0, 0, 6, 11, 0]))

    def test_myTeamsStats(self):
        t1 = 'LIVERPOOL FC'
        t2 = 'WOLVERHAMPTON WANDERERS FC'
        t3 = 'LEICESTER CITY FC'
        labels = ['Matches Played', 'Wins', 'Draws', 'Losses', 'Goals Scored', 'Clean Sheets', 'Cards']
        self.assertEqual(myTeamStats(t1), (labels, [38, 30, 7, 1, 89, 21, 41]))
        self.assertEqual(myTeamStats(t2), (labels, [38, 16, 9, 13, 47, 9, 74]))
        self.assertEqual(myTeamStats(t3), (labels, [38, 15, 7, 16, 51, 10, 67]))     
    
    def test_myTeamsTopScorers(self):
        t1 = 'ARSENAL FC'
        t2 = 'WOLVERHAMPTON WANDERERS FC'
        t3 = 'LEICESTER CITY FC'
        self.assertEqual(myTeamStats(t1), ['PIERRE-EMERICK AUBAMEYANG', 'LAURENT KOSCIELNY', 'LUCAS TORREIRA', 'SHKODRAN MUSTAFI', 'NACHO MONREAL', 'SOKRATIS PAPASTATHOPOULOS', 'KONSTANTINOS MAVROPANOS', 'MATTéO GUENDOUZI OLIé', 'PETR ČECH', 'ROB HOLDING'])
        self.assertEqual(myTeamStats(t2), ['RAúL ALONSO JIMéNEZ RODRíGUEZ', 'MATT DOHERTY', 'WILLY BOLY', 'LEANDER DENDONCKER', 'ROMAIN SAïSS', 'JONNY', 'KORTNEY HAUSE', 'MAX KILMAN'])
        self.assertEqual(myTeamStats(t3), ['YOURI TIELEMANS', 'MARC ALBRIGHTON', 'ONYINYE WILFRED NDIDI', 'RICARDO DOMINGOS BARBOSA PEREIRA', 'JONNY EVANS', 'RACHID GHEZZAL', 'JOHNNY', 'NAMPALYS MENDY', 'SHINJI OKAZAKI'])       

if __name__ == '__main__':
    unittest.main()