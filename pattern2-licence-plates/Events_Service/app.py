from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from aiokafka import AIOKafkaConsumer
import asyncio, os, ast
import nest_asyncio
nest_asyncio.apply()

## global variable :: setting this for kafka Consumer
KAFKA_ENDPOINT = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'lpr')
KAFKA_CONSUMER_GROUP_ID = os.getenv('KAFKA_CONSUMER_GROUP_ID', 'event_consumer_group')
loop = asyncio.get_event_loop()

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HT@1202k')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_NAME = os.getenv('TABLE_NAME','event')

engine = create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})

Base = declarative_base()

class Event(Base):
    __tablename__ = "event"
    event_id = Column(String, primary_key=True, index=True)
    event_timestamp = Column('date', DateTime(timezone=True), default=func.now())
    event_vehicle_detected_plate_number = Column(String, index=True)
    #event_vehicle_detected_lat = Column(Numeric(precision=7, scale=5, decimal_return_scale=None, asdecimal=False))
    #event_vehicle_detected_long = Column(Numeric(precision=7, scale=5, decimal_return_scale=None, asdecimal=False))
    event_vehicle_lpn_detection_status = Column(String)
    stationA1 = Column(Boolean, unique=False)
    stationA5201 = Column(Boolean, unique=False)
    stationA13 = Column(Boolean, unique=False)
    stationA2 = Column(Boolean, unique=False)
    stationA23 = Column(Boolean, unique=False)
    stationB313 = Column(Boolean, unique=False)
    stationA4202 = Column(Boolean, unique=False)
    stationA41 = Column(Boolean, unique=False)
    stationB504 = Column(Boolean, unique=False)



async def consume():
    kafkaConsumer = AIOKafkaConsumer(KAFKA_TOPIC, loop=loop, bootstrap_servers=KAFKA_ENDPOINT, group_id=KAFKA_CONSUMER_GROUP_ID)
    connection = engine.connect()
    ## Create Table if does not exists
    Event.__table__.create(bind=engine, checkfirst=True)

    await kafkaConsumer.start()
    try:
        async for msg in kafkaConsumer:
            print(msg.key)
            message = msg.value
            payload=ast.literal_eval(message.decode('utf-8'))
            connection.execute(f"""INSERT INTO public.{TABLE_NAME}(event_id, date, event_vehicle_detected_plate_number, event_vehicle_lpn_detection_status, "stationA1", "stationA5201", "stationA13", "stationA2", "stationA23", "stationB313", "stationA4202" 
, "stationA41", "stationB504" ) VALUES('{payload['event_id']}', '{payload['event_timestamp']}', '{payload['event_vehicle_detected_plate_number']}', '{payload['event_vehicle_lpn_detection_status']}', '{payload['stationA1']}', '{payload['stationA5201']}', '{payload['stationA13']}', '{payload['stationA2']}', '{payload['stationA23']}', '{payload['stationB313']}', '{payload['stationA4202']}', '{payload['stationA41']}', '{payload['stationB504']}'
)""")
            print("===============================================")
            print(payload)
            print("Message written to DB successfully")
            print("===============================================")
    finally:
        await kafkaConsumer.stop()
loop.run_until_complete(consume())
