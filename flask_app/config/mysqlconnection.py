import pymysql.cursors
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MySQLConnection:
    def __init__(self, db):
        # change the user and password as needed
        connection = pymysql.connect(host = 'localhost',
                                    user = 'root', 
                                    password = '@00#we4/', 
                                    db = db,
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = False)
        self.connection = connection
    def query_db(self, query:str, data:dict=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                print("Running Query:", query)
     
                cursor.execute(query)
                if query.lower().find("insert") >= 0:
                    # INSERT queries will return the ID NUMBER of the row inserted
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
                    result = cursor.fetchall()
                    return result
                else:
                    # UPDATE and DELETE queries will return nothing
                    self.connection.commit()
            except Exception as e:
                # if the query fails the method will return FALSE
                print("Something went wrong", e)
                return False
            finally:
                # close the connection
                self.connection.close() 

def connect_to_mysql(db_name=None):
    if db_name is None:
        db_name = 'pies'
    
    try:
        logger.debug(f"Attempting to connect to MySQL database: {db_name}")
        connection = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            db=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        logger.info(f"Successfully connected to MySQL database: {db_name}")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to MySQL database: {db_name}. Error: {str(e)}")
        raise

def query_db(query: str, data: dict = None):
    connection = connect_to_mysql()
    try:
        with connection.cursor() as cursor:
            query = cursor.mogrify(query, data)
            logger.debug(f"Executing query: {query}")
            
            cursor.execute(query)
            if query.lower().find("insert") >= 0:
                # INSERT queries will return the ID NUMBER of the row inserted
                connection.commit()
                return cursor.lastrowid
            elif query.lower().find("select") >= 0:
                # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
                result = cursor.fetchall()
                logger.debug(f"Query returned {len(result) if result else 0} results")
                return result
            else:
                # UPDATE and DELETE queries will return nothing
                connection.commit()
    except Exception as e:
        # if the query fails the method will return FALSE
        logger.error(f"Query failed: {str(e)}")
        return False
    finally:
        # close the connection
        connection.close()

