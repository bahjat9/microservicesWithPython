import json
import threading
import pika
from flask import Flask, jsonify, request

app = Flask(__name__)

consent_store = {}
log_store = {}

def has_consent(user_id: str) -> bool:
    return consent_store.get(user_id, False)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "logging-service"})

@app.post("/v1/consent/<user_id>")
def grant_consent(user_id):
    data = request.get_json(silent=True) or {}
    granted = data.get("granted", True)
    consent_store[user_id] = granted
    return jsonify({"user_id": user_id, "granted": granted})

@app.get("/v1/consent/<user_id>")
def get_consent(user_id):
    granted = consent_store.get(user_id, False)
    return jsonify({"user_id": user_id, "granted": granted})

@app.delete("/v1/consent/<user_id>")
def withdraw_consent(user_id):
    consent_store[user_id] = False
    return jsonify({"user_id": user_id, "granted": False})

@app.delete("/v1/logs/<user_id>")
def delete_logs(user_id):
    deleted = len(log_store.get(user_id, []))
    log_store[user_id] = []
    return jsonify({"user_id": user_id, "deleted_entries": deleted})

@app.get("/v1/logs/<user_id>")
def get_logs(user_id):
    return jsonify(log_store.get(user_id, []))

def consume():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        channel.queue_declare(queue="gamehub.logs", durable=True)

        def callback(ch, method, properties, body):
            data = json.loads(body)
            user_id = data.get("user_id")
            if not has_consent(user_id):
                print(f"[logging] No consent for {user_id}, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            if user_id not in log_store:
                log_store[user_id] = []
            log_store[user_id].append(data)
            print(f"[logging] Logged activity for {user_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue="gamehub.logs", on_message_callback=callback)
        channel.start_consuming()
    except Exception as e:
        print(f"[logging] RabbitMQ consumer error: {e}")

t = threading.Thread(target=consume, daemon=True)
t.start()

if __name__ == "__main__":
    app.run(port=8006)