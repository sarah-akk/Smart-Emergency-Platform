from graphs.emergency_coordinator import EmergencyState, build_emergency_coordinator_graph
import redis
import json


user_input = input("🚨 الرجاء كتابة بلاغك: ")

graph = build_emergency_coordinator_graph()


initial_state: EmergencyState = {
        "user_input": user_input,
        "location": None,
        "emergency_type": None,
        "emergency_subtype" : "None" , 
        "severity" :  "None" , 
        "missing_info": None,
        "safety_tips": None,
        "report": "",
    }


final_state = graph.invoke(initial_state)

print("\n📦 [النتيجة النهائية]:")
for key, value in final_state.items():
    print(f"{key}: {value}")


print("\n📦 [التقرير النهائي]:")
print(final_state["report"])

