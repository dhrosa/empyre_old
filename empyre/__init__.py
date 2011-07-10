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

class Enumerated(object):
    """Represents a named enumeration item.
    Intended for use with makeEnumeration. See the State, Action, and network.Message classes for example subclasses."""
    def __init__(self, name, value, argTypes = None):
        """name -- The name of the item.
        value -- The integral value of the item.
        argTypes -- An optional list of valid argument types to go with this item."""
        self.name = name
        self.value = value
        self.argTypes = argTypes

    def __eq__(self, other):
        """Equality operator.
        
        This operator is implemented such that an Enumerated can be compared to an int."""
        try:
            return int(self) == int(other)
        except TypeError:
            return False
    
    def __int__(self):
        return self.value

    def __repr__(self):
        if self.argTypes:
            return "%s('%s', %d, %s)" % (self.__class__.__name__, self.name, self.value, self.argTypes)
        else:
            return "%s('%s', %d)" % (self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return self.name

    @classmethod
    def fromInt(cls, val):
        """Converts an integer into an Enumerated subclass, returns None if the conversion fails.

        Example usage:
        >>> State.fromInt(0)
        State('Lobby', 0)"""
        try:
            return cls._int_to_enum[int(val)]
        except KeyError:
            return None

    def validateArgs(self, args = []):
        """Validates the types of the objects in args against self.argTypes, returns whether the args are valid.
        Any unicode objects in args are converted to str if the expected type is str."""
        if not self.argTypes:
            return True
        if len(args) != len(self.argTypes):
            return False
        for i, arg in enumerate(args):
            validType = self.argTypes[i]
            if validType == str and type(arg) in (str, unicode):
                args[i] = str(arg)
            elif validType != type(arg):
                return False
        return True

def makeEnumeration(klass, names):
    """Adds an enumeration to klass's attributes.
    
    klass -- The class to add the attributes to.
    names -- A list of enumeration names.
    
    Example usage:
    >>> class Fruits(Enumerated):
    >>>     pass
    >>>
    >>> makeEnumeration(Fruits, ["Apple", "Banana", "Cucumber", "Durian"])
    >>> print Fruits.Apple
    'Apple'
    >>> print int(Fruits.Apple)
    0
    >>> print int(Fruits.Banana)
    1
    >>> print int(Fruits.Cucumber)
    2"""
    try:
        klass._int_to_enum
    except AttributeError:
        klass._int_to_enum = {}
    for i, name in enumerate(names):
        enum = klass(name, i)
        klass._int_to_enum[i] = enum
        setattr(klass, name, enum)

def makeValidatedEnumeration(klass, entries):
    """Adds an enumeration to klass's attributes.
    
    klass -- The class to add the attributes to.
    entries -- A dictionary whose keys are enumeration names and whose values are lists of valid argument types.

    Example usage:
    >>> class Action(Enumerated):
    >>>    pass
    >>> #DoPushUps takes an integer that represents the number of pushups to do
    >>> #Run takes two integers, speed and number of laps to run
    >>> makeValidatedEnumeration(Action, {"DoPushUps": (int,), "Run": (int, int)})
    >>> print Action.Run
    'Run'
    >>> print int(Action.DoPushups)
    0
    >>> print int(Action.Run)
    1
    >>> print Action.Run.validateArgs([5, 10])
    True
    >>> print Action.Run.validateArgs(["cats", 3])
    False"""
    try:
        klass._int_to_enum
    except AttributeError:
        klass._int_to_enum = {}
    for i, (name, args) in enumerate(entries.iteritems()):
        enum = klass(name, i, args)
        klass._int_to_enum[i] = enum
        setattr(klass, name, enum)

class State(Enumerated):
    """Enumeration of the game's possible states.

    Lobby -- Waiting period before the game has started
    InitialPlacement -- Initial territory claim phase
    InitialDraft -- Placement of first troops after InitialPlacement
    Draft -- Current player is placing troops
    Attack -- Current player is attacking another
    Fortify -- Current player is fortifying troops from one territory to another
    GameOver -- There are no other players remaining"""
    pass

makeEnumeration(State, [
        "Lobby",
        "InitialPlacement",
        "InitialDraft",
        "Draft",
        "Attack",
        "Fortify",
        "GameOver",
        ])
