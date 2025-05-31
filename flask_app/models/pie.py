from flask_app.config.mysqlconnection import connect_to_mysql, query_db
from flask import flash
import logging

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Pie:
    db_name = "pies_db"
    def __init__(self, data):
        try:
            self.id = data['id']
            self.name = data['name']
            self.filling = data['filling']
            self.crust = data['crust']
            self.user_id = data['user_id']
            self.created_at = data['created_at']
            self.updated_at = data['updated_at']
            self.first_name = None
            self.last_name = None
            self.votes = None
            self.user = None
            
            if 'first_name' in data:
                self.first_name = data['first_name']
            if 'last_name' in data:
                self.last_name = data['last_name']
            if 'votes' in data:
                self.votes = data['votes']
            logger.debug(f"Successfully initialized Pie object with id {self.id}")
        except KeyError as e:
            logger.error(f"Missing required field in pie data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing Pie object: {e}")
            raise

    @classmethod
    def create_pie(cls, data):
        try:
            query = "INSERT INTO pies (name, filling, crust, user_id) VALUES (%(name)s, %(filling)s, %(crust)s, %(user_id)s);"
            logger.debug(f"Creating new pie with data: {data}")
            result = query_db(query, data)
            logger.info(f"Successfully created pie with id {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating pie: {e}")
            return False

    @classmethod
    def get_all_pies_of_user(cls, data):
        try:
            logger.debug(f"Getting all pies for user {data['user_id']}")
            query = """
                SELECT pies.*, users.first_name, users.last_name 
                FROM pies 
                JOIN users ON pies.user_id = users.id 
                WHERE pies.user_id = %(user_id)s;
            """
            logger.debug(f"Executing query: {query} with data: {data}")
            results = query_db(query, data)
            logger.debug(f"Query results: {results}")
            pies = []
            if results:
                for row in results:
                    pie = cls(row)
                    pie.first_name = row['first_name']
                    pie.last_name = row['last_name']
                    logger.debug(f"Created pie object: {pie.__dict__}")
                    pies.append(pie)
            logger.info(f"Successfully retrieved {len(pies)} pies for user {data['user_id']}")
            return pies
        except Exception as e:
            logger.error(f"Error getting pies for user {data.get('user_id')}: {e}")
            return []

    @classmethod
    def all_pies(cls):
        try:
            query = """
                SELECT pies.*, users.first_name, users.last_name 
                FROM pies 
                JOIN users ON pies.user_id = users.id;
            """
            logger.debug("Getting all pies")
            results = query_db(query)
            pies = []
            if results:
                for row in results:
                    pie = cls(row)
                    pie.first_name = row['first_name']
                    pie.last_name = row['last_name']
                    pies.append(pie)
            logger.info(f"Successfully retrieved {len(pies)} pies")
            return pies
        except Exception as e:
            logger.error(f"Error getting all pies: {e}")
            return []

    @classmethod
    def get_pie_by_id(cls, data):
        try:
            query = """
                SELECT pies.*, users.first_name, users.last_name 
                FROM pies 
                JOIN users ON pies.user_id = users.id 
                WHERE pies.id = %(id)s;
            """
            logger.debug(f"Getting pie with id {data['id']}")
            result = query_db(query, data)
            if result:
                pie = cls(result[0])
                pie.first_name = result[0]['first_name']
                pie.last_name = result[0]['last_name']
                logger.info(f"Successfully retrieved pie with id {data['id']}")
                return pie
            logger.warning(f"No pie found with id {data['id']}")
            return None
        except Exception as e:
            logger.error(f"Error getting pie with id {data.get('id')}: {e}")
            return None

    @classmethod
    def update_pie(cls, data):
        try:
            query = "UPDATE pies SET name = %(name)s, filling = %(filling)s, crust = %(crust)s WHERE id = %(id)s;"
            logger.debug(f"Updating pie with id {data['id']}")
            result = query_db(query, data)
            logger.info(f"Successfully updated pie with id {data['id']}")
            return result
        except Exception as e:
            logger.error(f"Error updating pie with id {data.get('id')}: {e}")
            return False

    @classmethod
    def delete_pie(cls, data):
        try:
            query = "DELETE FROM pies WHERE id = %(id)s;"
            logger.debug(f"Deleting pie with id {data['id']}")
            result = query_db(query, data)
            logger.info(f"Successfully deleted pie with id {data['id']}")
            return result
        except Exception as e:
            logger.error(f"Error deleting pie with id {data.get('id')}: {e}")
            return False

    @classmethod
    def get_pie_by_name_and_user(cls, data):
        try:
            logger.debug(f"Checking for pie with name: {data['name']} and user_id: {data['user_id']}")
            query = """
                SELECT pies.*, users.first_name, users.last_name 
                FROM pies 
                JOIN users ON pies.user_id = users.id 
                WHERE pies.name = %(name)s AND pies.user_id = %(user_id)s;
            """
            result = query_db(query, data)
            logger.debug(f"Query result: {result}")
            if result:
                pie = cls(result[0])
                pie.first_name = result[0]['first_name']
                pie.last_name = result[0]['last_name']
                logger.info(f"Found pie with name {data['name']} for user {data['user_id']}")
                return pie
            logger.warning(f"No pie found with name {data['name']} for user {data['user_id']}")
            return None
        except Exception as e:
            logger.error(f"Error checking pie with name {data.get('name')} for user {data.get('user_id')}: {e}")
            return None

    @classmethod
    def get_vote_count(cls, pie_id):
        query = "SELECT COUNT(*) as count FROM votes WHERE pie_id = %(pie_id)s;"
        result = query_db(query, {'pie_id': pie_id})
        return result[0]['count'] if result else 0

    @classmethod
    def user_voted(cls, user_id, pie_id):
        query = "SELECT * FROM votes WHERE user_id = %(user_id)s AND pie_id = %(pie_id)s;"
        result = query_db(query, {'user_id': user_id, 'pie_id': pie_id})
        return bool(result)

    @classmethod
    def cast_vote(cls, user_id, pie_id):
        query = "INSERT INTO votes (user_id, pie_id) VALUES (%(user_id)s, %(pie_id)s);"
        return query_db(query, {'user_id': user_id, 'pie_id': pie_id})

    @classmethod
    def remove_vote(cls, user_id, pie_id):
        query = "DELETE FROM votes WHERE user_id = %(user_id)s AND pie_id = %(pie_id)s;"
        return query_db(query, {'user_id': user_id, 'pie_id': pie_id})

    @classmethod
    def list_user_pies(cls, user_id):
        """Debug method to list all pies for a user"""
        query = "SELECT * FROM pies WHERE user_id = %(user_id)s;"
        result = query_db(query, {'user_id': user_id})
        logger.debug(f"All pies for user {user_id}: {result}")
        return result if result else []

    @staticmethod
    def validate_pie(pie, user_id, is_edit=False, pie_id=None):
        try:
            logger.debug(f"Validating pie: {pie}, user_id: {user_id}, is_edit: {is_edit}, pie_id: {pie_id}")
            is_valid = True
            
            # First, let's see what pies the user already has
            Pie.list_user_pies(user_id)
            
            if len(pie['name']) < 3:
                flash("Name must be at least 3 characters.", 'name')
                is_valid = False
            if len(pie['filling']) < 3:
                flash("Filling must be at least 3 characters.", 'filling')
                is_valid = False
            if len(pie['crust']) < 3:
                flash("Crust must be at least 3 characters.", 'crust')
                is_valid = False 
            
            # Check for duplicate names only for the current user
            if not is_edit or (is_edit and pie_id is not None):
                query = '''
                    SELECT COUNT(*) as count, GROUP_CONCAT(name) as names
                    FROM pies 
                    WHERE name = %(name)s 
                    AND user_id = %(user_id)s
                '''
                if is_edit and pie_id:
                    query += ' AND id != %(pie_id)s'
                
                data = {
                    'name': pie['name'],
                    'user_id': user_id
                }
                if is_edit and pie_id:
                    data['pie_id'] = pie_id
                    
                result = query_db(query, data)
                logger.debug(f"Duplicate check result: {result}")
                
                if result and result[0]['count'] > 0:
                    flash(f"You already have a pie named '{pie['name']}'. Please choose a different name for your pie.", 'name')
                    is_valid = False
                    
            logger.debug(f"Validation result: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Error validating pie: {e}")
            return False