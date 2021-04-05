import logging

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from ecommerce_api.config import Config
from ecommerce_api.resources import db
from ecommerce_api.api.rest import create_json_api

LOGGER = logging.getLogger(__name__)


def init_flask():
  LOGGER.info("Configurating Flask server")
  app = Flask(__name__, static_folder="static", template_folder="templates")
  app.wsgi_app = ProxyFix(app.wsgi_app, x_for=3)
  app.config.from_object(Config)
  LOGGER.info("Flask server configurated")

  return app


def init_sqlalquemy(app):
  db.init_app(app)
  LOGGER.info("Flask SQLAlquemy configurated")


def init_migrate(app):
  migrate = Migrate()
  migrate.init_app(app, db)
  LOGGER.info("Flask Migrate configurated")


def init_cors(app):
  CORS(
    app,
    resources={
      r"/*": {
          "origins": "*"
      }
  })
  LOGGER.info("Flask CORS configurated")


def init_api(app):
  api = Api(app, prefix='/'+Config.VERSION)
  create_json_api(api)
  LOGGER.info("API endpoints configurated")


def create_app():
  app = init_flask()
  init_cors(app)
  init_sqlalquemy(app)
  init_migrate(app)
  init_api(app)

  return app
