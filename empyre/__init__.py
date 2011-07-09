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
    import version
    p.add_argument("-b", "--boardpath", help="The directory to search for boards in.")
    p.add_argument("-l", "--logfile", help="The file to write logs to. Defaults to ~/.empyre/%s/log" % ("client" if client else "server"))
    p.add_argument("-n", "--no-logging", action="store_true", help="Don't write to log file.")
    p.add_argument("-d", "--debug", action="store_true", help="Displays debugging information.")
    p.add_argument("-q", "--quiet", action="store_true", help="Don't output any debug or information lines; warnings and errors will still be output.")
    p.add_argument("-s", "--silent", action="store_true", help="Suppresses all output, even warnings and errors.")
    p.add_argument("-v", "--version", action="version", version=version.version())

def setupLogger(args, client):
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
        return len(self.cards)

import inspect
class State(object):
    (
        OutOfSync,
        Lobby,
        InitialPlacement,
        InitialDraft,
        Draft,
        Attack,
        Fortify,
        GameOver,
    ) = range(8)

    @staticmethod
    def toString(state):
        return stateToString[state]

stateToString = dict([(m[1], m[0]) for m in inspect.getmembers(State) if m[0][0].isupper()])

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
