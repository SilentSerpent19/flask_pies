from flask_app.config.mysqlconnection import connect_to_mysql, query_db
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

from flask import flash
import logging
from flask_app.models.pie import Pie

logger = logging.getLogger(__name__)

class User:
    db_name = "pies_db"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.pies = []  # List to store user's pies

    @classmethod
    def create_user(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return query_db(query, data)

    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        result = query_db(query, data)
        if result:
            user = cls(result[0])
            # Load user's pies
            user.pies = Pie.get_all_pies_of_user({'user_id': user.id})
            logger.debug(f"Loaded {len(user.pies)} pies for user {user.id}")
            return user
        return None

    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = query_db(query, data)
        if result:
            user = cls(result[0])
            # Load user's pies
            user.pies = Pie.get_all_pies_of_user({'user_id': user.id})
            logger.debug(f"Loaded {len(user.pies)} pies for user {user.id}")
            return user
        return None
    

    @staticmethod
    def validate_user(data):
        is_valid = True
        if len(data['first_name']) < 2:
            flash("First name must be at least 2 characters.", 'first_name')
            is_valid = False
        if len(data['last_name']) < 2:
            flash("Last name must be at least 2 characters.", 'last_name')
            is_valid = False
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            flash("Invalid email address.", 'emailRegister')
            is_valid = False
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters.", 'passwordRegister')
            is_valid = False
        if data['password'] != data['confirmPassword']:
            flash("Passwords do not match.", 'passwordConfirm')
            is_valid = False
        return is_valid