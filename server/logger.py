import mysql.connector
import datetime

from test import *

cnx = mysql.connector.connect(user='root', password='root',
                              host='localhost', database='chat')


def register(connection, username, mail, password):
    existing_user = get_user(connection, mail)
    if existing_user:
        cursor.close()
        return "Error: This email is already registered."
    else:
        create_user(connection, 5, username, password, datetime.datetime.now(), mail, 1)
        cursor.close()
        return "User registered successfully!"


def login(connection, username, mail, password):
    existing_user = get_user(mail)
    if existing_user:
        # login
        cursor.close()
        return "User logged in successfully!"
    else:
        cursor.close()
        return "Error: This email is not registered."

register(cnx, "Wojtek", "mail@wp.pl", "123456")

# TODO: zmienić bazę żeby nie bylo id usera tylko email byl primary keyem
#TODO: to logowanie że sprawdzić hasło i maila czy dobra kombinacja
