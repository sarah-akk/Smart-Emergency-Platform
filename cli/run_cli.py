from services.emergency_service import run_graph_for_user

if __name__ == "__main__":
    user_id = "user_123"  # could be dynamic
    user_input = input("🚨 الرجاء كتابة بلاغك: ")
    
    final_state = run_graph_for_user(user_id, user_input)
    
    print("\n📦 [النتيجة النهائية]:")
    for key, value in final_state.items():
        print(f"{key}: {value}")
    
    print("\n📦 [التقرير النهائي]:")
    print(final_state["report"])
