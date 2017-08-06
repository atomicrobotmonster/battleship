#!/usr/bin/env python

import re
import random
import traceback

from enum import Enum, auto


class OutcomeState(Enum):
    MISS = auto()
    HIT = auto()
    SUNK = auto()
    WIN = auto()


class Orientation(Enum):
    PORTRAIT = auto()
    LANDSCAPE = auto()


class Outcome:
    """Outcome of a player turn.

    Clients should use static factory methods miss(),
    hit(ship), sunk(ship) and win(ship).
    """

    def __init__(self, outcome_state, ship_name=None):
        """Allocate a new instance..

        :param outcome_state: OutcomeState value
        :param ship_name: optional ship name, not used for misses
        :return: new Outcome instance
        """
        self.outcome_state = outcome_state
        self.ship_name = ship_name

    def __eq__(self, other):
        return self.outcome_state == other.outcome_state and self.ship_name == other.ship_name

    def __str__(self):
        if self.outcome_state == OutcomeState.MISS:
            mesg = 'Miss'
        elif self.outcome_state == OutcomeState.HIT:
            mesg = 'Hit {0}'.format(self.ship_name)
        elif self.outcome_state == OutcomeState.SUNK:
            mesg = 'Sunk {0}'.format(self.ship_name)
        elif self.outcome_state == OutcomeState.WIN:
            mesg = 'Game over - last ship sunk was {0}'.format(self.ship_name)
        else:
            mesg = 'Invalid game outcome'

        return mesg

    def is_game_over(self):
        """Tests whether this outcome indicates the game is now over.

        :return: True when the game is over; False otherwise
        """
        return self.outcome_state == OutcomeState.WIN

    @staticmethod
    def miss():
        """Factory method to create a Miss Outcome.

        :return: new instance of miss Outcome.
        """
        return Outcome(OutcomeState.MISS)

    @staticmethod
    def hit(ship):
        """Factory method to create a Ship Hit Outcome.

        :param ship: the sunk ship
        :return: new instance of ship hit Outcome.
        """
        return Outcome(OutcomeState.HIT, ship.name)

    @staticmethod
    def sunk(ship):
        """Factory method to create a Ship Sunk Outcome.

        :param ship: the sunk ship
        :return: new ship sunk Outcome
        """
        return Outcome(OutcomeState.SUNK, ship.name)

    @staticmethod
    def win(ship):
        """Factory method to create a Game Over Outcome.

        :param ship: the last ship sunk that caused the game to be won
        :return: new game over Outcome
        """
        return Outcome(OutcomeState.WIN, ship.name)


class AlreadyAttacked(Exception):
    """Raised when a grid space has already been attacked."""

    def __init__(self, coord):
        """Allocates a new instance.

        :param coord: the coord of the previously attacked grid space
        :return: new instance
        """

        self.coord = coord

    def __str__(self):
        return "Coordinate {0} has already been attacked.".format(self.coord)


class AlreadyAssigned(Exception):

    """Raised when a ship square has already been assigned to a grid space."""

    def __init__(self, coord):
        """Allocates a new instance.

        :param coord: the coord of the grid space
        :return: new instance
        """
        self.coord = coord

    def __str__(self):
        return "Coordinate {0} has already been assigned a GridSpace.".format(
            self.coord)


class InvalidCoord(Exception):

    """Raised when a co-ordinate is poorly formed or out of range."""

    def __init__(self, coord):
        """Allocates a new instance.

        :param coord: the coord that is invalid
        :return: new instance
        """
        self.coord = coord

    def __str__(self):
        return "Coordinate {0} is invalid.".format(self.coord)


class GridSpace:

    """Represents a non-empty space in the player game grid."""

    def __init__(self, grid, coord, ship=None, state=''):
        """Allocates a new instance.

        :param owning_player: player to which this grid space belongs to
        :param coord: the human readable coord string (e.g. 'A7')
        :param ship: optional ship that occupies this space
        :param state: tracks un-attacked (''), hit ('hit') or miss ('miss')
        :return: new instance
        """

        self.grid = grid
        self.coord = coord
        self.ship = ship
        self.state = state

    def attack(self):
        """Resolves an attack against this grid space.

        :return: an Outcome instance - miss(), hit(ship), sunk(ship) or win(ship)
        """

        if not self._already_attacked():
            self._hit()

            if self.ship.is_sunk():
                self.grid.active_ship_count -= 1

                if (self.grid.active_ship_count == 0):
                    return Outcome.win(self.ship)
                else:
                    return Outcome.sunk(self.ship)
            else:
                return Outcome.hit(self.ship)
        else:
            raise AlreadyAttacked(self.coord)

    def _hit(self):
        """"Records a hit on this grid space and notifies hit ship."""

        if self.ship:
            self.state = 'hit'
            self.ship.hit()

    def _already_attacked(self):
        """Tests whether this space has already been attacked

        :return: True when already attacked; False otherwise
        """

        return self.state != ''

    def is_hit(self):
        """Tests whether this space contains a hit on a ship.

        :return: True when grid space contains a hit on a ship; False otherwise
        """
        return self.state == 'hit'

    def is_miss(self):
        """Tests whether this space contains a missed shot.

        :return: True when grid space contains a miss; False otherwise
        """
        return self.state == 'miss'

    def __eq__(self, other):
        return self.grid == other.grid and self.coord == other.coord and self.ship == other.ship and self.state == other.state

    def __str__(self):
        return '{0}: {1} {2}'.format(
            self.coord, self.state, self.ship.name if self.ship else '')

class Ship:

    """Ship used in the game.

    Prefer use of static factory methods to create specific ship types.
    """

    def __init__(self, name, size, code):
        """Allocates a new instance.

        :param name: the human readable name of the ship
        :param size: the number of contiguous grid spaces the ship occupies
        :param code: a single character code to display on battle grid
        :return: new instance
        """
        self.name = name
        self.size = size
        self.hits = 0
        self.code = code

    def hit(self):
        """Track a hit on this ship."""
        self.hits += 1

    def is_sunk(self):
        """Tests whether this ship has been sunk.

        Compares number of this against ship size.
        :return: True when sunk; False otherwise
        """
        return self.hits >= self.size

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def carrier():
        """Creates a new Carrier of size 5.

        :return: new Carrier instance
        """

        return Ship('Carrier', 5, 'C')

    @staticmethod
    def battleship():
        """Creates a new Battleship of size 4.

        :return: new Battleship instance
        """
        return Ship('Battleship', 4, 'B')

    @staticmethod
    def cruiser():
        """Creates a new Cruiser of size 3.

        :return: new Cruiser instance
        """

        return Ship('Cruiser', 3, 'R')

    @staticmethod
    def submarine():
        """Creates a new Submarine of size 3.

        :return: new Submarine instance
        """
        return Ship('Submarine', 3, 'S')

    @staticmethod
    def destroyer():
        """Creates a new Destroyer of size 3.

        :return: new Destroyer instance
        """

        return Ship('Destroyer', 2, 'D')

fleet = [Ship.carrier(), Ship.battleship(), Ship.cruiser(), Ship.submarine(), Ship.destroyer()]

class BattleGrid:
    coord_regex = r'^([A-H])([0-8])$'

    def __init__(self):
        """Allocates a new instance.

        :return: new instance
        """
        self.grid = {}
        self.active_ship_count = 0
        self.grid_dimension = (8, 8)

    def valid_coord(self, coord):
        """Tests whether player co-ordinate string passes the validation regex.

        :param coord: player co-ordinate string, e.g. 'A7'
        :return: True when valid, False otherwise
        """

        match = re.search(BattleGrid.coord_regex, coord)

        return match is not None

    def split_coord(self, coord):
        """Splits a player co-ordinate string into a tuple of row and column.

        :param coord: player co-ordinate string, e.g. 'A7'
        :return: tuple of row and column, e.g. ('A',7)
        """
        match = re.search(BattleGrid.coord_regex, coord)

        if (match is not None):
            return (match.group(1), match.group(2))
        else:
            raise InvalidCoord(coord)

    def coord_tuple_to_index_tuple(self, coord_tuple):
        """Converts a row and column tuple into a 2D array zero-indexed tuple

        :param coord_tuple: tuple of player co-ordinate, e.g. ('A',7)
        :return: 2D array index tuple, e.g. (0, 6)
        """
        digit_domain = 3

        x_ords = list(reversed([ord(c) - 64 for c in list(coord_tuple[0])]))

        x_raised = [(x_ords[i] * (digit_domain ** i))
                    for i in range(len(x_ords))]

        x = sum(x_raised) - 1
        y = int(coord_tuple[1]) - 1

        return (x, y)

    def index_tuple_to_coord_tuple(self, index_tuple):
        """Converts a 2D array index tuple to a player co-ordinate tuple.

        :param index_tuple 2D array index tuple, e.g. (0, 6)
        :return: tuple of player co-ordinate, e.g. ('A',7)
        """
        (index_x, index_y) = index_tuple

        return (chr(index_x + 65), index_y + 1)

    def _set_grid_space(self, coord, ship):
        """Sets a grid space in the player grid during game setup.

        :param coord: player co-ordinate string
        :param ship: ship at the grid space identified by coord
        """
        if not self.valid_coord(coord):
            raise InvalidCoord(coord)

        if (coord not in self.grid):
            self.grid[coord] = GridSpace(self, coord, ship)
        else:
            raise AlreadyAssigned(coord)

    def _tuple_to_coord(self, coord_tuple):
        """Converts a co-ordinate tuple to a player co-ordinate.

        :param coord_tuple: co-ordinate tuple, e.g. ('A',7)
        :return: player co-ordinate, e.g. 'A7'
        """
        return '{0}{1}'.format(coord_tuple[0], coord_tuple[1])

    def _calculate_coords(self, origin_coord, orientation, size):
        """Calculate the player co-ordinates a ship should occupy.

        Extends the ship a number of spaces from the origin in the direction indicated by orientation.
        For portrait orientation, the origin represents the topmost point of the ship. For landscape
        orientation, the origin represents the leftmost point of the ship.

        :param origin_coord: topmost co-ordinate for portrait orientation, leftmost for landscape
        :param orientation: portrait or landscape layout for the ship
        :param size: the number of spaces to extend from the origin in the direction indicated by orientation
        :return: list of player co-ordinates ship should occupy, e.g. ['A1','A2','A3']
        """
        (origin_row, origin_column) = self.coord_tuple_to_index_tuple(
            origin_coord)

        if Orientation.LANDSCAPE == orientation:
            return [self._tuple_to_coord(self.index_tuple_to_coord_tuple((origin_row, column))) for column in range(origin_column, origin_column + size)]
        elif Orientation.PORTRAIT == orientation:
            return [self._tuple_to_coord(self.index_tuple_to_coord_tuple((row, origin_column))) for row in range(origin_row, origin_row + size)]
        else:
            return []

    def place_ship(self, ship, origin_coord, orientation):
        """Places a ship on the player game grid.

        For portrait orientation, the ship extends from topmost origin point through a number
        of points equal to the ship size. For landscape orientation, origin forms the
        leftmost point.

        :param ship: the ship to place
        :param origin_coord: origin of the topmost or leftmost point
        :param orientation: orientation of the ship, either portrait or landscape
        """
        if not self.valid_coord(origin_coord):
            raise InvalidCoord(origin_coord)

        coord_tuple = self.split_coord(origin_coord)

        coords = self._calculate_coords(coord_tuple, orientation, ship.size)

        # validate all coords within grid and unoccupied
        for coord in coords:
            if not self.valid_coord(coord):
                raise InvalidCoord(coord)
            if coord in self.grid:
                raise AlreadyAssigned(coord)

        for coord in coords:
            self._set_grid_space(coord, ship)

        self.active_ship_count += 1


    def random_layout(self, ships):
        attempted = set()
        max_attempts = 8 * 8 * 2

        ships_remaining = ships[:]
        while len(ships_remaining) > 0:
            while len(attempted) < max_attempts and len(ships_remaining) > 0:
                #generate random coord and orientation
                coord = random.choice('ABCDEFGH') + random.choice('12345678')
                orientation = random.choice(list(Orientation))
                coord_and_orientation = (coord, orientation)
                ship = ships_remaining[0]

                if coord_and_orientation not in attempted:
                    attempted.add(coord_and_orientation)
                    try:
                        self.place_ship(ship, coord, orientation)
                    except (AlreadyAssigned, InvalidCoord) as e:
                        pass
                    except Exception as e:
                        traceback.print_exc(e)
                    else:
                        ships_remaining.pop(0)

            if len(ships_remaining) > 0:
                # we failed to place all the ships so try again
                ships_remaining = ships[:]
                self.reset()

    def reset(self):
        self.grid = {}
        self.active_ship_count = 0


class Player:

    """Player of the game, including their battle grid."""

    def __init__(self, name):
        """Allocates a new instance of a named player.

        :param name: name of player

        :return: new instance
        """
        self.name = name
        self.battle_grid = BattleGrid()


    def random_layout(self, fleet):
        """Randomly layout fleet on player's battle grid.

        :param fleet: ships to place on battle grid
        """
        self.battle_grid.random_layout(fleet)

    def receive_attack(self, coord):
        if (coord in self.battle_grid.grid.keys()):
            targeted = self.battle_grid.grid[coord]
            return targeted.attack()
        else:
            self.battle_grid.grid[coord] = GridSpace(
                self, coord, state='miss')
            return Outcome.miss()


    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

class AIPlayer(Player):
    def __init__(self,name):
        super().__init__(name)

class RandomAIPlayer(AIPlayer):
    def __init__(self,name):
        super().__init__(name)
        self.targets = ["{0}{1}".format(row,column) for row in 'ABCDEFGH' for column in range(1,9)]
        random.shuffle(self.targets)

    def next_target(self):
        return self.targets.pop(0)

class Game:

    """A playable game of Battleship.

    The game accepts two players on construction, however these are assigned to
    current_layer and current_opponent. The next_player() method swaps these players
    and the take_turn method places the current_player in the role of the player
    making the attack and current_opponent as the player being attacked.
    """

    def __init__(self, human, computer):
        """Allocates a new instance.

        :param human: human player
        :param computer: computer player
        :return: new game instance
        """
        self.human = human
        self.computer = computer
        self.current_player = human
        self.current_opponent = computer

    def next_player(self):
        """Swaps current_player and current_opponent."""

        self.current_player, self.current_opponent = self.current_opponent, self.current_player

        return self.current_player

    def take_turn(self, coord):
        """Current player attacks a grid space identified by a player co-ordinate.

        :param coord: the player co-ordinate of the grid space being attacked by current player
        :return: an Outcome representing a miss, a hit on a ship, a hit than sinks a ship
                 or the game being won (including which ship was sunk to trigger the win)
        """

        return self.current_opponent.receive_attack(coord)
