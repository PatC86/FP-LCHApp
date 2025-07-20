# Name      : main
# Author    : Patrick Cronin
# Date      : 19/07/2025
# Updated   : 19/07/2025
# Purpose   : Main Python file for running lifting chain application.

from website import create_app

app = create_app()

## run app would turn of debug if production env
if __name__ == '__main__':
    app.run(debug=True)