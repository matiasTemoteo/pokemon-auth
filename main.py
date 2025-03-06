from website import create_app
import os

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

app = create_app()

if __name__ == '__main__':
    context = ('certs/code.crt', 'certs/code.key')
    app.config['DEBUG'] = True
    app.run(ssl_context=context)