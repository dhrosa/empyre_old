"""Basic functionality of Empyre.
Sets SIP's QString API to version 2, and creates configuration directories in ~/.empyre."""

import sip
sip.setapi("QString", 2)

import os
import os.path
home = os.path.expanduser("~")
configDir = os.path.join(home, ".empyre")
if not os.path.exists(configDir):
    os.mkdir(configDir)
serverConfigDir = os.path.join(configDir, "server")
if not os.path.exists(serverConfigDir):
    os.mkdir(serverConfigDir)
serverLog = os.path.join(serverConfigDir, "log")
clientConfigDir = os.path.join(configDir, "client")
if not os.path.exists(clientConfigDir):
    os.mkdir(clientConfigDir)
clientLog = os.path.join(clientConfigDir, "log")

def setupArguments(p, client):
    """Adds command line arguments common to both the server and client to the ArgumentParser p.

    client -- Boolean value indicating whether the caller is the client or server."""
    import version
    p.add_argument("-b", "--boardpath", help="The directory to search for boards in.")
    p.add_argument("-l", "--logfile", help="The file to write logs to. Defaults to ~/.empyre/%s/log" % ("client" if client else "server"))
    p.add_argument("-n", "--no-logging", action="store_true", help="Don't write to log file.")
    p.add_argument("-d", "--debug", action="store_true", help="Displays debugging information.")
    p.add_argument("-q", "--quiet", action="store_true", help="Don't output any debug or information lines; warnings and errors will still be output.")
    p.add_argument("-s", "--silent", action="store_true", help="Suppresses all output, even warnings and errors.")
    p.add_argument("-v", "--version", action="version", version=version.version())

def setupLogger(args, client):
    """Configures the logging module to write to stderr and a log file.

    args -- An argparse NameSpace object as returned by parse_args.
    client -- Whether the caller is the client or server.

    Log file options:
    args.no_logging -- Do not write to log file.
    args.logfile -- The log file to write to. By default logs to ~/.empyre/server/log or ~/.empyre/client/log, rotating logfiles every midnight.

    Stderr logging options:
    If none of the following are specified, information and more server messages will be printed to stderr.
    args.silent -- Do not print to stderr.
    args.quiet -- Print only warning and more severe messages to stderr.
    args.debug -- Print debug messages in addition to other messages to stderr.
    """
    import logging, logging.handlers
    import sys
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt="%(levelname)-8s %(name)-8s %(asctime)s %(message)s",
                                  datefmt="%H:%M:%S")
    if not args.no_logging:
        if args.logfile:
            logHandler = logging.FileHandler(args.logfile)
            logHandler.setFormatter(formatter)
            logHandler.setLevel(logging.DEBUG)
            log.addHandler(logHandler)
        else:
            logFile = clientLog if client else serverLog
            logHandler = logging.handlers.TimedRotatingFileHandler(logFile, when="midnight")
            logHandler.setFormatter(formatter)
            logHandler.setLevel(logging.DEBUG)
            log.addHandler(logHandler)

    if not args.silent:
        if args.debug:
            level = logging.DEBUG
        elif args.quiet:
            level = logging.WARNING
        else:
            level = logging.INFO
        streamHandler = logging.StreamHandler(stream=sys.stderr)
        streamHandler.setFormatter(formatter)
        streamHandler.setLevel(level)
        log.addHandler(streamHandler)

class Player(object):
    """Represents a player.
    
    name -- The player's name.
    color -- A 3-tuple representing a player's color in RGB [0-255].
    isPlaying -- Whether the player is in-play.
    cards -- Currently held cards.
    password -- The password used to rejoin the game if the player is disconnected.
    ready -- Whether the player is ready to start the game.
    """

    def __init__(self, name):
        self.name = name
        self.color = (0, 0, 0)
        self.isPlaying = True
        self.cards = []
        self.password = ""
        self.ready = False

    def __str__(self):
        return self.name

    def cardCount(self):
        """The number of cards held by the player."""
        return len(self.cards)

import inspect
class State(object):
    """Enumeration of the game's possible states.

    Lobby -- Waiting period before the game has started
    InitialPlacement -- Initial territory claim phase
    InitialDraft -- Placement of first troops after InitialPlacement
    Draft -- Current player is placing troops
    Attack -- Current player is attacking another
    Fortify -- Current player is fortifying troops from one territory to another
    GameOver -- There are no other players remaining"""
    (
        Lobby,
        InitialPlacement,
        InitialDraft,
        Draft,
        Attack,
        Fortify,
        GameOver,
    ) = range(7)

    @staticmethod
    def toString(state):
        """Returns a string representation of a state."""
        return _stateToString[state]

_stateToString = dict([(m[1], m[0]) for m in inspect.getmembers(State) if m[0][0].isupper()])

class Action(object):
    (
        AddPlayer,
        RemovePlayer,
        StartGame,
        ExchangeCards,
        PlaceTroops,
        Attack,
        EndAttack,
        Fortify,
        EndTurn,
     ) = range(9)

    validArgs = {
        AddPlayer: (str,),
        RemovePlayer: (str,),
        StartGame: (),
        ExchangeCards: (int, int, int),
        PlaceTroops: (str, int),
        Attack: (str, str, int),
        EndAttack: (),
        Fortify: (str, str, int),
        EndTurn: (),
    }

    @staticmethod
    def argMatch(action, args):
        try:
            valid = Action.validArgs[action]
            for i, a in enumerate(args):
                if not type(a) == valid[i]:
                    return False
        except:
            return False
        return True

    @staticmethod
    def toString(action):
        return actionToString[action]

actionToString = dict([(m[1], m[0]) for m in inspect.getmembers(Action) if m[0][0].isupper()])
