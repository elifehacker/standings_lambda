import json
import psycopg2
from config import config
from datetime import datetime

def connect(cmd):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        #print('PostgreSQL database version:')
        #cur.execute('SELECT version()')
        cur.execute(cmd)
        
        # display the PostgreSQL database server version
        #db_version = cur.fetchone()
        #print(db_version)
        #return db_version
        
        # https://stackoverflow.com/questions/50279896/postgresql-not-inserting-in-python-on-aws-lambda-with-psycopg2/50280452
        conn.commit()

        return cur.fetchall()
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def connect_log(sid, score, date_time_str):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
	# execute a statement
        cur.execute("""INSERT INTO standing_logs (team_id, score, date) VALUES (%s, %s, %s);""",(sid, score, date_time_obj))
        conn.commit()

        return cur.fetchall()
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def update_teams(t):
    if 'id' in t:
        if len(connect("select * from teams where id = "+t['id'])) == 0:
            print(connect('insert into teams (id, name, coach) values (' + t['id']+',\''+t['name']+'\',\''+t['coach']+ '\') RETURNING *'))
            
        # Bad example. exposed to SQL injection, use query parameter instead
        if 'name' in t and 'coach' in t:
            body = connect("update teams set name = \'"+ t['name'] + "\', coach = \'"+ t['coach'] +"\' where id = "+t['id']+' RETURNING *')
        elif 'name' in t:
            body = connect("update teams set name = \'"+ t['name'] + "\' where id = "+t['id']+' RETURNING *')
        elif 'coach' in t:
            body = connect("update teams set coach = \'"+t['coach']+"\' where id = "+t['id']+' RETURNING *')
            
        if 'score' in t:
            connect("update standings set score = \'"+t['score']+"\' where team_id = "+t['id']+' RETURNING *')
            connect_log(t['id'], t['score'], t[date])
            
    return body

def lambda_handler(event, context):
    # TODO implement
    # https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway-tutorial.html
    
    # consider using below instead
    # https://stackoverflow.com/questions/31329958/how-to-pass-a-querystring-or-route-parameter-to-aws-lambda-from-amazon-api-gatew
    print('event: ',event)
    print('context: ',context)
    op = event['operation']
    body = ''
    if op == 'read':
        if 'team' in event:
            body = connect("Select * from teams where id = "+event['team'])
        else:
            body = connect("Select * from teams")
    if op == 'update':
        if 'teams' in event:
            teams = event['teams']
            print('teams:', teams)
            for t in teams:
                print('t:',t)
                body = update_teams(t)
    return {
        'statusCode': 200,
        #'body': json.dumps('Hello from Lambda!')
        'body': body
    }
