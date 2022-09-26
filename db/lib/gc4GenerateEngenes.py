from datetime import datetime
import glob, sys, json, pandas, os, psycopg2, psycopg2.extras, re
from dotenv import load_dotenv
from pathlib import Path

#### Useful Functions #####
def unique(list1):
    return list(set(list1))

def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    return list( seen_twice )

#### Function to Access to DB ######
def executeSQL(cmd,dbname,user,password):
    """ Function to execute SQL command"""
    conn, cur = startPSQL(dbname,user,password)
    cur.execute(cmd)
    closePSQL(conn, cur)

def startPSQL(dbname,user,password):
    """ Function to open Postgresql database"""
    conn = psycopg2.connect("host='localhost' dbname='"+dbname+"' user='"+user+"' password='"+password+"'")
    cur = conn.cursor()
    return [conn, cur]

def closePSQL(conn, cur):
    """ Function to close Postgresql"""
    conn.commit()
    cur.close()
    conn.close()

def launchQuery(cmdTemplate,args,getDF=True,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD")):
    """ Function to launch queries"""
    args = [tuple(arg) if isinstance(arg,list) else arg for arg in args]
    args = [tuple([arg,'x']) if len(arg) == 1 else arg for arg in args]
    conn = psycopg2.connect(host='localhost', dbname=dbname,
                             user=user, password=password)
    if getDF:
        df = pandas.read_sql_query(cmdTemplate,conn,params=args)
        conn.commit()
        conn.close()
        return (df)
    cur = conn.cursor()
    cur.execute(cmdTemplate,args)
    cur.close()
    conn.commit()
    conn.close()
