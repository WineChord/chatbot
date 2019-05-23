# -*- coding: utf-8 -*-
from generateNEW import *
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'database_chat'
TABLES = {}
TABLES['faulty_part'] = (
    "CREATE TABLE `faulty_part` ("
    "  `record_no` int(3) NOT NULL AUTO_INCREMENT,"
    "  `identifier` varchar(8) NOT NULL,"
    "  `index` varchar(100) NOT NULL,"
    "  `label` varchar(28) NOT NULL,"
    "  `phenomenon` varchar(80) NOT NULL,"
    "  `faulty_body` varchar(16) NOT NULL,"
    "  `degree` varchar(20),"
    "  `explanation` varchar(840) NOT NULL,"
    "  `impact_on_sys` varchar(480) NOT NULL,"
    "  `causes` varchar(750) NOT NULL,"
    "  `solutions` varchar(3000) NOT NULL,"
    "  PRIMARY KEY (`record_no`)"
    ") ENGINE=InnoDB")
TABLES['sensor'] = (
    "CREATE TABLE `sensor` ("
    "  `record_no` int(3) NOT NULL AUTO_INCREMENT,"
    "  `identifier` varchar(8) NOT NULL,"
    "  `index` varchar(100) NOT NULL,"
    "  `label` varchar(28) NOT NULL,"
    "  `phenomenon` varchar(80) NOT NULL,"
    "  `faulty_body` varchar(16) NOT NULL,"
    "  `explanation` varchar(840) NOT NULL,"
    "  `impact_on_sys` varchar(480) NOT NULL,"
    "  `causes` varchar(750) NOT NULL,"
    "  `solutions` varchar(3000) NOT NULL,"
    "  PRIMARY KEY (`record_no`)"
    ") ENGINE=InnoDB")
new_faulty, new_sensor = generateNEW()
cnx = mysql.connector.connect(user='mychat',password='qazwsx456852')
cursor = cnx.cursor()
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)
try:
    cnx.database = DB_NAME 
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

add_faulty_part = ("INSERT INTO faulty_part "
    "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
for j, i in enumerate(new_faulty):
    data_faulty = (i.identifier, i[0], i.label, i.phenomenon, i.faulty_body, i.degree, i.explanation, i.impact_on_sys, i.causes, i.solutions)
    cursor.execute(add_faulty_part, data_faulty)

add_sensor_part = ("INSERT INTO sensor "
    "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
for j, i in enumerate(new_sensor):
    data_sensor = (i.identifier, i[0], i.label, i.phenomenon, i.faulty_body, i.explanation, i.impact_on_sys, i.causes, i.solutions)
    cursor.execute(add_sensor_part, data_sensor)

cnx.commit()
cursor.close()
cnx.close()
