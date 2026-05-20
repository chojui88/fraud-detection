#kafka에서 데이터 읽어서 csv로 저장하는 로직


from kafka import KafkaConsumer
import json
import csv
import os
from datetime import datetime

TOPIC = "payments-topic"
BOOTSTRAP_SERVERS = "localhost:9092"
OUTPUT_FILE = "payment_data.csv"
TARGET_COUNT = 10000 #목표 수집 건수

#CSV 헤더 , 6개 추출 특징
FIELDNAMES = ["amount", "hour", "ip_last", "device_num",  "freq_score", "failed_count", "isFraud"]

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers = BOOTSTRAP_SERVERS,
    value_deserializer = lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset = "latest",  
    group_id = "data-collector" 
)

print(f"Kafka 연결됨 -{TOPIC} 토픽 수신 시작")
print(f"목표: {TARGET_COUNT:,}건 수집 -> {OUTPUT_FILE} 저장")

count = 0
file_exists = os.path.exists(OUTPUT_FILE) #데이터 파일에 존재하나

with open(OUTPUT_FILE, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames = FIELDNAMES)
    if not file_exists:
        writer.writeheader()
    
    for message in consumer:
        event = message.value

        #hour 단위로 변환
        ts = event.get("timestamp", 0) / 1000
        hour = datetime.fromtimestamp(ts).hour

        #ip 마지막 부분 추출
        ip = event.get("ipAddress", "0.0.0.0")
        ip_last = int(ip.split(".")[-1]) if ip else 0

        #device_num 추출
        device = event.get("deviceId", "DEV-0")
        device_num = int(device.split("-")[-1]) if "-" in device else 0

        writer.writerow({
            "amount":   event.get("amount",0),
            "hour":     hour,
            "ip_last":  ip_last,
            "device_num":device_num,
            "freq_score":   0.0,    
            "failed_count":event.get("failedCount",0),
            "isFraud":  1 if event.get("fraud",False)else 0
        })

        count +=1
        if count % 500 == 0: #500건마다 한 번씩만
            print(f"    {count:,}건 수집중...")
        if count >= TARGET_COUNT:
            print(f"\n{TARGET_COUNT:,}건 수집 완료! -> {OUTPUT_FILE}")
            break

consumer.close()


