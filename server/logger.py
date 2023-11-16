import mysql.connector
import datetime

cnx = mysql.connector.connect(user='root', password='root',
                              host='localhost', database='chat')


def register(connection, username, mail, password):
    query = "SELECT * FROM user WHERE user_email = %s"
    cursor.execute(query, mail)
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return "Error: This email is already registered."
    else:
        create_user(connection, 1, username, password, datetime.datetime.now(), mail, 1)
        cursor.close()
        return "User registered successfully!"


def login(connection, username, mail, password):
    query = "SELECT * FROM user WHERE user_email = %s"
    cursor.execute(query, mail)
    existing_user = cursor.fetchone()
    if existing_user:
        # login
        cursor.close()
        return "User logged in successfully!"
    else:
        cursor.close()
        return "Error: This email is not registered."

# TODO: zmienić bazę żeby nie bylo id usera tylko email byl primary keyem
