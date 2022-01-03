from flask import Flask

from rdfexplorer import routes
from config import Config


def create_app(config_object=Config):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(routes.bp)
    app.config.config_object(config_object)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
