from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config, TestingConfig

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes import users, products, orders
    app.register_blueprint(users.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(orders.bp)

    return app
