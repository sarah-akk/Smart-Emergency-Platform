import json
from fastapi import FastAPI, Request
from pyngrok import ngrok
import uvicorn

from graphs.emergency_coordinator import EmergencyState, build_emergency_coordinator_graph

app = FastAPI()
graph = build_emergency_coordinator_graph()

# public_url = ngrok.connect(8000)
# print("✅ ngrok tunnel opened:", public_url)


@app.post("/answer")
async def process_report(request: Request):

    # Read request body as JSON
    body = await request.json()

    print("\n" + "="*50)
    print("📩 Received New Request on /answer")
    print("="*50)
    print("🔹 Full Body Received:")
    print(body)
    print("-"*50)

    # Extract the user's current message text
    try:
        print(f"📝 Extracted User Message: '{body["body"]["current_message"]["text"]}'")
    except KeyError:
        print("❌ Error: Could not find ['body']['current_message']['text'] in request")
        return {"error": "Invalid request structure"}

    print("-"*50)

    # Build initial state for the graph
    last_state = body.get("body", {}).get("last_state") or {}
    state_data = last_state.get("state", {})

    state: EmergencyState = {
        "user_info": body.get("body", {}).get("user_info"),
        "user_input": body.get("body", {}).get("current_message", {}).get("text"),
        "ai_response": "",
        "history": body.get("body", {}).get("history", []),
        "location": body.get("body", {}).get("current_message", {}).get("location", {}).get("address", ""),
        "emergency_type": state_data.get("emergency_type"),
        "emergency_subtype": state_data.get("emergency_subtype"),
        "severity": state_data.get("severity"),
        "missing_info": state_data.get("missing_info"),
        "safety_tips": state_data.get("safety_tips"),
        "report": state_data.get("report"),
    }


    print("🚀 Initial State Passed to Graph:")
    print(state)
    print("-"*50)

    # Run the graph logic
    final_state = graph.invoke(state)

    print("🔹 Final State Before Returning:")
    print(json.dumps(final_state, ensure_ascii=False, indent=4))

    print("="*50 + "\n")

    # ✅ Return custom response
    return {
        "message": final_state.get("ai_response", ""),
        "state": {
            "emergency_type" : final_state.get("emergency_type", ""),
            "emergency_subtype" : final_state.get("emergency_subtype", ""),
            "severity" : final_state.get("severity", ""),
            "missing_info" : final_state.get("missing_info", ""),
            "safety_tips" : final_state.get("safety_tips", ""),
            "report" : {
                "name" :  final_state.get("name", ""),  
                "discription" :  final_state.get("discription", ""),  
                "text" :  final_state.get("report", ""),  
            } 
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
