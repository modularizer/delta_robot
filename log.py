class LOG(object):
    """object which mimics logging.Logger with the added capability of color coded logging

    https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
    level = 'debug'
    """logging level, anything below will not get printed"""

    header = '\033[95m'
    """escape characters for header text"""
    blue = '\033[94m'
    """escape characters for blue text"""
    cyan = '\033[96m'
    """escape characters for cyan text"""
    green = '\033[92m'
    """escape characters for green text"""
    yellow = '\033[93m'
    """escape characters for yellow text"""
    red = '\033[91m'
    """escape characters for red text"""
    end_color = '\033[0m'
    """escape characters for ending colored text"""
    bold = '\033[1m'
    """escape characters for bold text"""
    underline = '\033[4m'
    """escape characters for underlined text"""
    end = '\x1b[0m'
    """escape characters for ending formatted text"""
    print = print
    """function used for printing"""

    levels = ['debug', 'info', 'warning', 'error', 'exception', 'critical']
    """order of logging levels"""

    _level = lambda n: 1 * (LOG.levels.index(n) >= LOG.levels.index(LOG.level))
    """bool whether level is above LOG.level"""

    _func = lambda n: [lambda *a, **kw: None, LOG.print][LOG._level(n)]
    """get logging function if level is above LOG.level"""

    debug = lambda *a, **kw: LOG._func('debug')(*a, LOG.end_color, **kw)
    """print debug statement in black"""

    info = lambda *a, **kw: LOG._func('info')(LOG.green, *a, LOG.end_color, **kw)
    """print info statement in green"""

    warning = lambda *a, **kw: LOG._func('warning')(LOG.yellow, *a, LOG.end_color, **kw)
    """print warning statement in yellow"""

    error = lambda *a, **kw: LOG._func('error')(LOG.red, *a, LOG.end_color, **kw)
    """print error statement in red"""

    exception = lambda *a, **kw: LOG._func('exception')(LOG.red, LOG.underline, *a,
                                                                 LOG.end, **kw)
    """print exception statement in underlined red"""

    critical = lambda *a, **kw: LOG._func('critical')(LOG.red, LOG.bold, *a,
                                                               LOG.end, **kw)
    """print critical statement in bold red"""

    def __init__(self, *a, **kw):
        LOG.print(*a, **kw)