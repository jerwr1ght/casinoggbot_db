import threading
import telebot
import datetime
import time
import psycopg2
import os
#DATABASE_URL = os.environ['DATABASE_URL']
global db
global sql
global user_id
db = psycopg2.connect(database='d6ipfqeahpii9', user='tualpgdacfdowa', port="5432", password='415217eb3e4acb039e30c4ff760b49c478935253484832ffe9e16467eb9007f3', host='ec2-52-23-45-36.compute-1.amazonaws.com', sslmode='require')
sql=db.cursor()

def block_work(user_id):
    sql.execute(f"UPDATE players SET job_blocked = 'unblocked' WHERE chatid = '{user_id}'")
    db.commit()
