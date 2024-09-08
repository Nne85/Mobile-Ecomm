## This project provides details for the APIs required for a mobile ecommerce application

Start this project in a virtual environment
cd /project_directory
python -m venv venv
source venv/bin/activate

#### Note: Replace the values with your own secrets and database credentials.
Install dependencies: Run the following command to install the required dependencies:
pip install -r requirements.txt

### Running the App
To run the app, follow these steps:
Create a .env file: Create a new file named .env in the root directory of the project. Add the fo
llowing environment variables:
SECRET_KEY=your_secret_key
DATABASE_URL=mysql://user:password@host:port/dbname
JWT_SECRET_KEY=your_jwt_secret_key
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_mysql_db
TEST_DATABASE_URL=mysql://user:password@host:port/test_dbname

Run the app: Run the following command to start the app:
python run.py

### Code
The code for the implemented APIs can be found in the app/routes directory.

### Testing
The tests for the implemented APIs can be found in the tests directory. To run the tests, use the following command:
python -m unittest tests/test_orders.py

###Technology Stack
Python
Flask 
Flask-JWT-Extended for authentication
Flask-SQLAlchemy - ORM (Object-Relational Mapping) tool for Python
MySQL 
