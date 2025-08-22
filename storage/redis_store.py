import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def save_state(user_id: str, state: dict):
    redis_client.set(f"user:{user_id}:state", json.dumps(state))

def load_state(user_id: str) -> dict:
    state_json = redis_client.get(f"user:{user_id}:state")
    return json.loads(state_json) if state_json else None
