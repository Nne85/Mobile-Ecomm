""" This module includes logic to create the tables. """

from app import create_app, db
from app.models import user, product, order
import os


if os.environ.get('TESTING') == 'True':
    app = create_app(config_class=TestingConfig)

else:
    app = create_app()

with app.app_context():
        db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
