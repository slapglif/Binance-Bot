import sys


def handle_error(e):
    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)