class term_colors:
    """ANSI codes for highlighting code on the command line. Add in a code
    before the text you want highlighted, and the END_COLOR after
    """
    PURPLE = '\033[95m'
    LIGHT_PURPLE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END_COLOR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'