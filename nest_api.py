import os
import sqlite3

import bcrypt
from flask import Flask, request
from flask_restful import Api, Resource
from dotenv import load_dotenv

from nest import nest

app = Flask(__name__)
api = Api(app)
load_dotenv()


class DBInteraction():
    def __init__(self, conn):
        self.conn = conn
        self.cur = self.conn.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS User
             (username text, password_hash text)"""
        )
        self.conn.commit()

    def user_exists(self, username):
        if self.cur.execute("""SELECT * from User WHERE username = ?""",
                            (username,)).fetchone() is None:
            return False
        else:
            return True

    def verify_pw(self, username, password):
        hashed_pw = self.cur.execute("""
        SELECT password_hash from User WHERE username = ?""",
                                     (username,)).fetchone()[0]

        if bcrypt.checkpw(password.encode("utf-8"), hashed_pw):
            return True
        else:
            return False

    def verify_credentials(self, username, password):
        if not self.user_exists(username):
            return "Invalid Username", True

        correct_pw = self.verify_pw(username, password)

        if not correct_pw:
            return "Incorrect Password", True

        return None, False

    def add_new_user(self, username, password):
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        self.cur.execute('''INSERT INTO User Values (?, ?)''',
                         (username, hashed_pw))
        self.conn.commit()

    def delete_user(self, username):
        self.cur.execute('''DELETE FROM User WHERE username = ?''',
                         (username,))
        self.conn.commit()


class Register(Resource):
    def post(self):
        if os.getenv("FLASK_ENV") == "TEST":
            db = DBInteraction(sqlite3.connect("nest_test.db"))
        else:
            db = DBInteraction(sqlite3.connect("nest.db"))

        user_data = request.get_json()

        username = user_data["username"]
        password = user_data["password"]

        if db.user_exists(username):
            return "Username already exists", 409

        db.add_new_user(username, password)

        return "You successfully signed up for the API", 200


class Nest(Resource):
    def post(self):
        if os.getenv("FLASK_ENV") == "TEST":
            db = DBInteraction(sqlite3.connect("nest_test.db"))
        else:
            db = DBInteraction(sqlite3.connect("nest.db"))
        user_data = request.get_json()

        username = user_data["username"]
        password = user_data["password"]

        error_msg, error = db.verify_credentials(username, password)
        if not error:
            data = user_data["data"]
            levels = request.args["levels"].split(",")
            result, successful = nest(data, levels)

            if not successful:
                return result, 400
            else:
                return result, 200
        else:
            return error_msg, 400


api.add_resource(Register, '/register')
api.add_resource(Nest, '/nest')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
