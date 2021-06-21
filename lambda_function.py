import json
import psycopg2
from config import config

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

        return cur.fetchone()
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def lambda_handler(event, context):
    # TODO implement
    # https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway-tutorial.html
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
                if 'id' in t:
                    #body = connect("insert into teams (name, coach) values (\'groundhog\',\'moley\') RETURNING *")
                    #break
                    if 'name' in t:
                        body = connect("update teams set name = \'"+ t['name'] + "\' where id = "+t['id']+' RETURNING *')
                    if 'coach' in t:
                        body = connect("update teams set coach = \'"+t['coach']+"\' where id = "+t['id']+' RETURNING *')
    return {
        'statusCode': 200,
        #'body': json.dumps('Hello from Lambda!')
        'body': body
    }
