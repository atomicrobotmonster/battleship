#!/usr/bin/env python

from enum import Enum
import re

OutcomeState = Enum('OutcomeState', 'miss hit sunk win')


class Outcome:

    def __init__(self, outcome_state, ship_name=None):
        self.outcome_state = outcome_state
        self.ship_name = ship_name

    def __eq__(self, other):
        return self.outcome_state == other.outcome_state and self.ship_name == other.ship_name

    def __str__(self):
        if self.outcome_state == OutcomeState.miss:
            mesg = 'Miss'
        elif self.outcome_state == OutcomeState.hit:
            mesg = 'Hit {0}'.format(self.ship_name)
        elif self.outcome_state == OutcomeState.sunk:
            mesg = 'Sunk {0}'.format(self.ship_name)
        elif self.outcome_state == OutcomeState.win:
            mesg = 'Game over - last ship sunk was {0}'.format(self.ship_name)
        else:
            mesg = 'Invalid game outcome'

        return mesg

    def is_game_over(self):
        return self.outcome_state == OutcomeState.win

    @staticmethod
    def miss():
        return Outcome(OutcomeState.miss)

    @staticmethod
    def hit(ship):
        return Outcome(OutcomeState.hit, ship.name)

    @staticmethod
    def sunk(ship):
        return Outcome(OutcomeState.sunk, ship.name)

    @staticmethod
    def win(ship):
        return Outcome(OutcomeState.win, ship.name)


class AlreadyAttacked(Exception):

    def __init__(self, coord):
        self.coord = coord

    def __str__(self):
        return "Coordinate {0} has already been attacked.".format(self.coord)


class AlreadyAssigned(Exception):

    def __init__(self, coord):
        self.coord = coord

    def __str__(self):
        return "Coordinate {0} has already been assigned a GridSpace.".format(
            self.coord)


class InvalidCoord(Exception):

    def __init__(self, coord):
        self.coord = coord

    def __str__(self):
        return "Coordinate {0} is invalid.".format(self.coord)


class ShipSizeCoordsMismatch(Exception):

    def __init__(self, ship, coords):
        self.ship = ship
        self.coords = coords

    def __str__(self):
        return "Ship {0} has a size of {1} but {3} co-ordinates were supplied.".format(
            self.ship.name, self.ship.size, len(self.coords))


class GridSpace:

    def __init__(self, owning_player, coord, ship=None, state=''):
        self.owning_player = owning_player
        self.coord = coord
        self.ship = ship
        self.state = state

    def attack(self):
        if not self._already_attacked():
            self._hit()

            if self.ship.is_sunk():
                self.owning_player.active_ship_count -= 1

                if (self.owning_player.active_ship_count == 0):
                    return Outcome.win(self.ship)
                else:
                    return Outcome.sunk(self.ship)
            else:
                return Outcome.hit(self.ship)
        else:
            raise AlreadyAttacked(self.coord)

    def _hit(self):
        if self.ship:
            self.state = 'hit'
            self.ship.hit()

    def _already_attacked(self):
        return self.state != ''

    def is_hit(self):
        return self.state == 'hit'

    def is_miss(self):
        return self.state == 'miss'

    def __eq__(self, other):
        return self.owning_player == other.owning_player and self.coord == other.coord and self.ship == other.ship and self.state == other.state

    def __str__(self):
        return '{0}: {1} {2}'.format(
            self.coord, self.state, self.ship.name if self.ship else '')


class Ship:

    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.hits = 0

    def hit(self):
        self.hits += 1

    def is_sunk(self):
        return self.hits >= self.size

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def carrier():
        return Ship('Carrier', 5)

    @staticmethod
    def battleship():
        return Ship('Battleship', 4)

    @staticmethod
    def cruiser():
        return Ship('Cruiser', 3)

    @staticmethod
    def submarine():
        return Ship('Submarine', 3)

    @staticmethod
    def destroyer():
        return Ship('Destroyer', 2)


class Player:

    coord_regex = r'^([A-H]+)([0-9]+)$'

    def __init__(self, name):
        self.name = name
        self.grid = {}
        self.active_ship_count = 0
        self.grid_dimension = (8, 8)

    def valid_coord(self, coord):
        match = re.search(Player.coord_regex, coord)

        return match is not None

    def split_coord(self, coord):
        match = re.search(Player.coord_regex, coord)

        if (match is not None):
            return (match.group(1), match.group(2))
        else:
            raise InvalidCoord(coord)

    def coord_tuple_to_index_tuple(self, coord_tuple):
        digit_domain = 3

        ord_minus_one = lambda c: ord(c) - 64

        x_ords = list(
            reversed(
                map(ord_minus_one, list(coord_tuple[0]))
            ))

        x_raised = [(x_ords[i] * (digit_domain**i))
                    for i in xrange(len(x_ords))]

        x = sum(x_raised) - 1
        y = int(coord_tuple[1]) - 1

        return (x, y)

    def _set_grid_space(self, coord, ship):
        if (coord not in self.grid):
            self.grid[coord] = GridSpace(self, 'A1', ship)
        else:
            raise AlreadyAssigned(coord)

    def place_ship(self, ship, coords):
        if ship.size != len(coords):
            raise ShipSizeCoordsMismatch(ship, coords)

        self.active_ship_count += 1

        for coord in coords:
            self._set_grid_space(coord, ship)

    def __eq__(self, other):
        return self.name == other.name


class Game:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.current_player = p1
        self.current_opponent = p2

    def next_player(self):
        self.current_player, self.current_opponent = self.current_opponent, self.current_player

    def take_turn(self, coord):
        if (coord in self.current_opponent.grid.keys()):
            targeted = self.current_opponent.grid[coord]
            return targeted.attack()
        else:
            self.current_opponent.grid[coord] = GridSpace(
                self.current_opponent, coord, state='miss')
            return Outcome.miss()
