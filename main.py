# Name      : main
# Author    : Patrick Cronin
# Date      : 19/07/2025
# Updated   : 17/08/2025
# Purpose   : Main Python file for running lifting chain application.
import sys

from website import create_app
import logging

try:
    app = create_app()
except Exception as e:
    logging.error(f'Failed to create app: {e}')
    sys.exit(1)


## run app would turn off debug if production env
if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        logging.error(f'Failed to run app: {e}')
        sys.exit(1)