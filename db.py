import logging

log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.policies import RoundRobinPolicy

KEYSPACE = "mnist"


def createKeySpace():
    cluster = Cluster(contact_points=['cassandra'], load_balancing_policy=RoundRobinPolicy(),port=9042,)
    session = cluster.connect()

    log.info("Creating keyspace...")
    try:
        session.execute("""
            CREATE KEYSPACE %s
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
            """ % KEYSPACE)

        log.info("Setting keyspace...")
        session.set_keyspace(KEYSPACE)

        log.info("Creating table...")
        session.execute("""
            CREATE TABLE History (
                IP_Address text,
                access_time timestamp,
                image_path text,
                mnist_result text,
                PRIMARY KEY (IP_Address, access_time)
            )
            """)
            
        
    except Exception as e:
        log.error("Unable to create keyspace")
        log.error(e)

def insertData(ip_addr, access_time, image_path, mnist_result):
    cluster = Cluster(contact_points=['cassandra'],load_balancing_policy=None, port=9042,)
    session = cluster.connect()
    log.info("Inserting data...")
    try:
        session.execute(""" 
            INSERT INTO mnist.History (IP_Address, access_time, image_path, mnist_result)
            VALUES(%s, %s, %s, %s);
            """,
            (ip_addr, access_time, image_path, mnist_result)
        )
    except Exception as e:
        log.error("Unable to insert data")
        log.error(e)