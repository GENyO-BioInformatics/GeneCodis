import psycopg2, psycopg2.extras, pandas, os

def launchQuery(cmdTemplate,args,getDF=True):
    args = [tuple(arg) if isinstance(arg,list) else arg for arg in args]
    conn = open_connection()
    print(cmdTemplate)
    if getDF:
        df = pandas.read_sql_query(cmdTemplate,conn,params=args)
        close_connection(conn)
        return (df)
    cur = conn.cursor()
    cur.execute(cmdTemplate,args)
    cur.close()
    close_connection(conn)

def open_connection():
    conn = psycopg2.connect(host='localhost', dbname=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))
    return conn

def close_connection(conn):
    conn.commit()
    conn.close()

def createGC4logTable():
    cmd = """
    CREATE TABLE
    gc4log (hash VARCHAR,
            gc4uid VARCHAR NOT NULL PRIMARY KEY,
            email VARCHAR,
            startdate DATE,
            startime TIME,
            enddate DATE,
            endtime TIME);
    """
    try:
        launchQuery(cmd,(),getDF=False)
        print('DB LOG CREATED')
    except:
        mode = input('DB LOG EXISTS, ReCreate? (Y/n)\n')
        if mode == 'n':
            print('KEPT')
        if mode == 'Y':
            print('REMOVE')
            removeTable('gc4log')
            launchQuery(cmd,(),getDF=False)

def defineArgsNtemplate(colNvalue):
    strFormat = []
    args = tuple()
    for col in colNvalue:
        strFormat.append("{} = %s ".format(col))
        args += (colNvalue[col],)
    return ','.join(strFormat),args

def addLog(colNvalue,rowCondition={}):
    if bool(rowCondition):
        strFormat,args = defineArgsNtemplate(colNvalue)
        cmdTemplate = "UPDATE gc4log SET "+strFormat
        strFormat,args2 = defineArgsNtemplate(rowCondition)
        cmdTemplate += "WHERE "+strFormat
        args += args2
    else:
        cmdTemplate = "INSERT INTO gc4log ({}) VALUES %s".format(','.join(list(colNvalue.keys())))
        args = (tuple(list(colNvalue.values())),)
    launchQuery(cmdTemplate+";",args,getDF=False)

def removeTable(table):
    cmd="DROP TABLE {};".format(table)
    try:
        launchQuery(cmd,(),getDF=False)
    except:
        createGC4logTable()

def checkExistence(column,value,table="gc4log"):
    cmd = "SELECT exists (SELECT 1 FROM {} WHERE {} = %s LIMIT 1);"
    cmd = cmd.format(table,column)
    existence = launchQuery(cmd,(value,)).exists[0]
    return(existence)

def getgc4uidfromHash(hash):
    cmd = "SELECT gc4uid FROM gc4log WHERE hash = %s;"
    gc4uid = launchQuery(cmd,(hash,)).gc4uid[0]
    return(gc4uid)

# removeTable('gc4log')
# createGC4logTable()
