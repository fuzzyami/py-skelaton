import psycopg2

PG_TABLE_NAME = 'mytable'

def get_connection():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        dbname='mydb',
        user='user',
        password='mysecretpassword')


def drop_table(table):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'drop table {table}')
    conn.commit()
    conn.close()
    return 'success'


def create_table(table):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'create table {table} (user_id int, user_name varchar(100))')
    conn.commit()
    conn.close()
    return 'success'


def setup_pg_db():
    try:
        drop_table('mytable')
    except:
        pass
    create_table('mytable')


def read_from_pg_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'select * from {PG_TABLE_NAME}')
    return cur.fetchall()


def write_to_pg_db(user_id, user_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'insert into {PG_TABLE_NAME} values {user_id, user_name}')
    conn.commit()
    return 'success'
