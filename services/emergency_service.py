from graphs.emergency_coordinator import build_emergency_coordinator_graph
from storage.redis_store import load_state, save_state

def run_graph_for_user(user_id: str, user_input: str):
    state = load_state(user_id)
    if not state:
        state = {
            "user_input": user_input,
            "location": None,
            "emergency_type": None,
            "emergency_subtype": None,
            "severity": None,
            "missing_info": None,
            "safety_tips": None,
            "report": ""
        }
    else:
        state["user_input"] = user_input

    graph = build_emergency_coordinator_graph()
    final_state = graph.invoke(state)

    save_state(user_id, final_state)
    return final_state
