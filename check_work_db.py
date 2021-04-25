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
db = psycopg2.connect(database='dn5ogam91pg6o', user='arfwywhrmkrevi', port="5432", password='125675860de38af1d492d597fb0d1d822a57743deac7328913007198b0f53175', host='ec2-54-87-112-29.compute-1.amazonaws.com', sslmode='require')
sql=db.cursor()

def block_work(user_id):
    sql.execute(f"UPDATE players SET job_blocked = 'unblocked' WHERE chatid = '{user_id}'")
    db.commit()
