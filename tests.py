#!/usr/bin/env python

from engine import Game, Player, Ship, GridSpace, Outcome, AlreadyAttacked, AlreadyAssigned, InvalidCoord

import unittest


class GameTest(unittest.TestCase):

    def setUp(self):
        self.p1 = Player('Player One')

        self.p2_submarine = Ship.submarine()
        self.p2_destroyer = Ship.destroyer()

        self.p2 = Player('Player Two')
        self.p2.place_ship(self.p2_submarine, ['A1', 'A2', 'A3'])
        self.p2.place_ship(self.p2_destroyer, ['C7', 'D7'])

        self.game = Game(self.p1, self.p2)

    def test_miss(self):
        self.assertEquals(
            Outcome.miss(),
            self.game.take_turn('B3'))

    def test_hit(self):
        self.assertEquals(
            Outcome.hit(self.p2_submarine),
            self.game.take_turn('A2'))

    def test_sunk(self):
        self.game.take_turn('A1')
        self.game.take_turn('A3')

        self.assertEquals(
            Outcome.sunk(self.p2_submarine),
            self.game.take_turn('A2'))

    def test_game_over(self):
        self.game.take_turn('A1')
        self.game.take_turn('A2')
        self.game.take_turn('A3')
        self.game.take_turn('D7')
        actual = self.game.take_turn('C7')

        self.assertEquals(
            Outcome.win(self.p2_destroyer),
            actual)

        self.assertTrue(actual.is_game_over())

    def test_already_attacked_raises_exception(self):
        targetCoord = 'A1'

        with self.assertRaises(AlreadyAttacked) as cm:
            self.game.take_turn(targetCoord)
            self.game.take_turn(targetCoord)

        self.assertEquals(cm.exception.coord, targetCoord)

    def test_next_player(self):
        prior_player = self.game.current_player
        prior_opponent = self.game.current_opponent

        self.game.next_player()

        self.assertEquals(self.game.current_player, prior_opponent)
        self.assertEquals(self.game.current_opponent, prior_player)


class PlayerTest(unittest.TestCase):

    def setUp(self):
        self.player = Player('Testy')
        self.carrier = Ship.carrier()

    def test_set_grid_space(self):
        coord = 'A1'

        self.player._set_grid_space(coord, self.carrier)

        self.assertEquals(
            self.player.grid[coord], GridSpace(self.player, coord, self.carrier))

    def test_alread_assigned_raises_exception(self):
        duplicateCoord = 'C1'

        self.player._set_grid_space(duplicateCoord, self.carrier)

        with self.assertRaises(AlreadyAssigned) as cm:
            self.player._set_grid_space(duplicateCoord, self.carrier)

        self.assertEquals(cm.exception.coord, duplicateCoord)

    def test_A7_is_valid_coord(self):
        self.assertTrue(self.player.valid_coord('A7'))

    def test_split_coord_A7(self):
        self.assertEquals(('A', '7'), self.player.split_coord('A7'))

    def test_AA7_is_valid_coord(self):
        self.assertTrue(self.player.valid_coord('AA7'))

    def test_split_coord_AA7(self):
        self.assertEquals(('AA', '7'), self.player.split_coord('AA7'))

    def test_AA07_is_valid_coord(self):
        self.assertTrue(self.player.valid_coord('AA07'))

    def test_split_coord_AA07(self):
        self.assertEquals(('AA', '07'), self.player.split_coord('AA07'))

    def test_blank_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord(''))

    def test_split_coord_on_blank_raises_exception(self):
        invalidCoord = ''

        with self.assertRaises(InvalidCoord) as cm:
            self.player.split_coord(invalidCoord)

        self.assertEquals(cm.exception.coord, invalidCoord)

    def test_reversed_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord('7A'))

    def test_numeral_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord('7'))

    def test_character_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord('A'))

    def test_coord_tuple_to_index_tuple_on_C7(self):
        self.assertEquals(
            self.player.coord_tuple_to_index_tuple(('C', '7')), (2, 6))

    def test_coord_tuple_to_index_tuple_on_AA7(self):
        self.assertEquals(
            self.player.coord_tuple_to_index_tuple(('CA', '7')), (9, 6))

    def test_coord_tuple_to_index_tuple_on_AA7(self):
        self.assertEquals(
            self.player.coord_tuple_to_index_tuple(('ABC', '7')), (17, 6))


if __name__ == '__main__':
    unittest.main()
