Battleships implementation in Python 3.6

# Setup

Creating a virtual env is recommended:

`python3 -m venv ~/python-env/battleship-env`

Don't forget to activate the venv!

`source ~/python-env/battleship-env`

Install dependencies:

pip3 install -r requirements.txt

# Playing the Game

python main.py to run a sample game. The game pits a single human player against a single AI player. At present, the AI player is an easy opponent as it naively selects a target at random.

# Testing

Tests are executed by running `nose2` to run nose2.
