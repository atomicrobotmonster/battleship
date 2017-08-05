#!/usr/bin/env python3

import unittest

import engine


class GameTest(unittest.TestCase):

    def setUp(self):
        self.p1 = engine.Player('Player One')

        self.p2_submarine = engine.Ship.submarine()
        self.p2_destroyer = engine.Ship.destroyer()

        self.p2 = engine.Player('Player Two')
        self.p2.place_ship(
            self.p2_submarine, 'A1', engine.Orientation.LANDSCAPE)
        self.p2.place_ship(
            self.p2_destroyer, 'C7', engine.Orientation.PORTRAIT)

        self.game = engine.Game(self.p1, self.p2)

    def test_miss(self):
        self.assertEquals(
            engine.Outcome.miss(),
            self.game.take_turn('B3'))

    def test_hit(self):
        self.assertEquals(
            engine.Outcome.hit(self.p2_submarine),
            self.game.take_turn('A2'))

    def test_sunk(self):
        self.game.take_turn('A1')
        self.game.take_turn('A3')

        self.assertEquals(
            engine.Outcome.sunk(self.p2_submarine),
            self.game.take_turn('A2'))

    def test_game_over(self):
        self.game.take_turn('A1')
        self.game.take_turn('A2')
        self.game.take_turn('A3')
        self.game.take_turn('D7')
        actual = self.game.take_turn('C7')

        self.assertEquals(
            engine.Outcome.win(self.p2_destroyer),
            actual)

        self.assertTrue(actual.is_game_over())

    def test_already_attacked_raises_exception(self):
        targetCoord = 'A1'

        with self.assertRaises(engine.AlreadyAttacked) as cm:
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
        self.player = engine.Player('Testy')
        self.carrier = engine.Ship.carrier()

    def test_set_grid_space(self):
        coord = 'A1'

        self.player._set_grid_space(coord, self.carrier)

        self.assertEquals(
            self.player.grid[coord], engine.GridSpace(self.player, coord, self.carrier))

    def test_alread_assigned_raises_exception(self):
        duplicateCoord = 'C1'

        self.player._set_grid_space(duplicateCoord, self.carrier)

        with self.assertRaises(engine.AlreadyAssigned) as cm:
            self.player._set_grid_space(duplicateCoord, self.carrier)

        self.assertEquals(cm.exception.coord, duplicateCoord)

    def test_A7_is_valid_coord(self):
        self.assertTrue(self.player.valid_coord('A7'))

    def test_split_coord_A7(self):
        self.assertEquals(('A', '7'), self.player.split_coord('A7'))

    def test_AA7_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord('AA7'))

    def test_AA07_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord('AA07'))

    def test_blank_is_not_valid_coord(self):
        self.assertFalse(self.player.valid_coord(''))

    def test_split_coord_on_blank_raises_exception(self):
        invalidCoord = ''

        with self.assertRaises(engine.InvalidCoord) as cm:
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

    def test_coord_tuple_to_index_tuple_on_CA7(self):
        self.assertEquals(
            self.player.coord_tuple_to_index_tuple(('CA', '7')), (9, 6))

    def test_coord_tuple_to_index_tuple_on_ABC7(self):
        self.assertEquals(
            self.player.coord_tuple_to_index_tuple(('ABC', '7')), (17, 6))

    def test_calculate_coords_landscape(self):
        origin_coord = 'A4'
        coords = self.player._calculate_coords(
            origin_coord, engine.Orientation.LANDSCAPE, 3)
        self.assertEquals(coords, ['A4', 'A5', 'A6'])

    def test_calculate_coords_portrait(self):
        origin_coord = 'A4'
        coords = self.player._calculate_coords(
            origin_coord, engine.Orientation.PORTRAIT, 3)
        self.assertEquals(coords, ['A4', 'B4', 'C4'])

    def test_place_landscape_ship_off_board(self):
        player = engine.Player('Player One')

        with self.assertRaises(engine.InvalidCoord) as cm:
            player.place_ship(engine.Ship.carrier(), 'A8', engine.Orientation.LANDSCAPE)

    def test_place_portrait_ship_off_board(self):
        player = engine.Player('Player One')

        with self.assertRaises(engine.InvalidCoord) as cm:
            player.place_ship(engine.Ship.carrier(), 'E1', engine.Orientation.PORTRAIT)

    def test_place_portrait_ship_on_board(self):
        player = engine.Player('Player One')

        player.place_ship(engine.Ship.carrier(), 'C5', engine.Orientation.PORTRAIT)

if __name__ == '__main__':
    unittest.main()
