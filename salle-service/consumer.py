from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import time

# Retry logic
for i in range(10):
    try:
        consumer = KafkaConsumer(
            'salle-events',
            bootstrap_servers='kafka:9092',
            group_id='salle-consumer-group',
            auto_offset_reset='earliest'
        )
        print("✅ Kafka Consumer connecté")
        break
    except NoBrokersAvailable:
        print(f"⏳ Kafka pas prêt, tentative {i+1}/10...")
        time.sleep(5)
else:
    print("❌ Kafka toujours indisponible après 10 tentatives.")
    exit(1)

# Ton code de consommation ici...
for message in consumer:
    print(f"📥 Message reçu : {message.value.decode()}")

