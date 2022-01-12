from flask import Flask

from rdfexplorer import routes
from config import Config


def create_app(config_object=Config):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_object)

    app.register_blueprint(routes.bp)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
