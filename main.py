#!/usr/bin/env python3

from engine import Player, AIPlayer, RandomAIPlayer, Game, Ship, AlreadyAttacked, Orientation, fleet
from time import sleep
from copy import deepcopy

def create_fleet_view(player):
    view = [['_'] * player.battle_grid.grid_dimension[0]
            for _ in range(player.battle_grid.grid_dimension[1])]

    for coord in player.battle_grid.grid.keys():
        grid_space = player.battle_grid.grid[coord]
        coord_tuple = player.battle_grid.split_coord(coord)
        index_tuple = player.battle_grid.coord_tuple_to_index_tuple(coord_tuple)

        (x, y) = index_tuple

        if grid_space.is_miss():
            view[x][y] = 'O'
        elif grid_space.is_hit():
            view[x][y] = 'X'
        elif grid_space.ship:
            view[x][y] = grid_space.ship.code

    return view


def create_target_view(player):
    view = [['_'] * player.battle_grid.grid_dimension[0]
            for _ in range(player.battle_grid.grid_dimension[1])]

    for coord in player.battle_grid.grid.keys():
        grid_space = player.battle_grid.grid[coord]
        coord_tuple = player.battle_grid.split_coord(coord)
        index_tuple = player.battle_grid.coord_tuple_to_index_tuple(coord_tuple)

        (x, y) = index_tuple

        if grid_space.is_miss():
            view[x][y] = 'O'

        if grid_space.is_hit():
            view[x][y] = 'X'

    return view


def convert_index_to_label(index):
    return chr(index + 65)


def print_view(view, grid_dimension):
    (x, y) = grid_dimension

    lines = []

    column_headers = '  '.join(['{0}'.format(i + 1) for i in range(y)])

    column_header_left_padding = ' ' * 5
    column_header_right_padding = ' ' * 3

    lines.append(column_header_left_padding +
                 column_headers + column_header_right_padding)

    grid_horizontal_edge = '  +--------------------------+'

    lines.append(grid_horizontal_edge)

    row_number = 0
    for row in view:
        row_text = '{0} |  '.format(convert_index_to_label(row_number))
        row_text += '  '.join(row)
        row_text += '  |'

        lines.append(row_text)
        row_number += 1

    lines.append(grid_horizontal_edge)

    return lines


def render_fleet_view(player):
    return print_view(create_fleet_view(player), player.battle_grid.grid_dimension)


def render_target_view(player):
    return print_view(create_target_view(player), player.battle_grid.grid_dimension)


def render_views(game):
    fleet_view = render_fleet_view(game.human)
    target_view = render_target_view(game.computer)

    print('\n')

    for view_tuple in zip(fleet_view, target_view):
        print('          '.join(view_tuple))


if __name__ == '__main__':

    p1 = Player('Player One')
    p1.random_layout(deepcopy(fleet))
    p2 = RandomAIPlayer('Player Two')
    p2.random_layout(deepcopy(fleet))

    game = Game(p1, p2)

    playing = True
    render_views(game)
    while playing:
        if isinstance(game.current_player, AIPlayer):
            command = game.current_player.next_target()
            print('\n{0} is choosing a target'.format(game.current_player), end='')
            for _ in range(3):
                sleep(1)
                print('.',end='',flush=True)
            print(command)
            sleep(0.75)
        else:
            valid_coord = False
            while playing and not valid_coord:
                command = input(
                    '\nYour turn, ' + game.current_player.name + ': ').strip().upper()

                if command == 'QUIT':
                    playing = False
                elif command == 'SHOW':
                    render_views(game)
                elif not p1.battle_grid.valid_coord(command):
                    print('\nPlease enter a valid co-ordinate (e.g. C7), "show" to view the board, or "quit" to end game.')
                else:
                    valid_coord = True

        if playing:
            try:
                outcome = game.take_turn(command)
            except AlreadyAttacked:
                print('\n{0} has already been attacked.'.format(command))
            else:
                print('\n{0}: {1}'.format(command, outcome))
                won = outcome.is_game_over()
                if won:
                    print("\n{0} is the winner!".format(game.current_player))
                playing = not won
                render_views(game)
                game.next_player()

    print('\n')
