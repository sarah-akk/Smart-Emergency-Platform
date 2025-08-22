# coordinator_graph.py
import json
from langgraph.graph import StateGraph, END
from agents.emergency_type_agent import emergency_type_agent
from agents.get_missing_info_agent import get_missing_info_agent
from agents.get_safety_tips_agent import get_safety_tips_agent
from agents.check_user_missing_info_agent import check_user_missing_info_agent
from typing_extensions import TypedDict


class EmergencyState(TypedDict):
    user_info: dict | None
    user_input: str
    ai_response: str | None
    history: list | None
    location: str | None
    emergency_type: str | None
    emergency_subtype: str | None
    severity: str | None
    missing_info: str | None
    safety_tips: list | None
    report: str


# ==============================================================
# NODE 1 - تحديد نوع الطارئ
def detect_emergency_type(state: EmergencyState) -> EmergencyState:

    if state.get("emergency_type"):
        return state  # النوع موجود مسبقاً → لا حاجة للوكيل

    result = emergency_type_agent.invoke({"input": state["user_input"]})

    if "intermediate_steps" in result and len(result["intermediate_steps"]) > 0:
        tool_output = result["intermediate_steps"][-1][1]
        if isinstance(tool_output, dict):
            state["report"] = (state.get("report") or "") + f"\n🚨 نوع الطوارئ: {tool_output['type']}"
            state["report"] += f"\n🔹 النوع الفرعي: {tool_output['subtype']}"
            state["report"] += f"\n⚠️ مستوى الخطورة: {tool_output['severity']}"
            state["report"] +=  f"\n🌐  موقع الحادث: {state['location']}"

            state["emergency_type"] = tool_output["type"]
            state["emergency_subtype"] = tool_output["subtype"]
            state["severity"] = float(tool_output["severity"])  # ضمان إرجاع float
            return state

    state["emergency_type"] = "غير معروف"
    state["emergency_subtype"] = "غير معروف"
    state["severity"] = "غير معروف"
    return state


# ==============================================================
# NODE 2 - الحصول على المعلومات الناقصة
def detect_missing_info(state: EmergencyState) -> EmergencyState:

    if state.get("missing_info") or not state.get("emergency_type"):
        return state  # لا نستدعي الوكيل إذا المعلومات مكتملة أو النوع غير معروف

    emergency_type = state.get("emergency_type", "UNKNOWN")
    emergency_subtype = state.get("emergency_subtype", "")
    user_input = state.get("user_input", "")

    if emergency_type == "UNKNOWN":
        state["missing_info"] = "❌ لا يمكن تحديد المعلومات الناقصة بدون نوع الطارئ."
        return state

    input_text = f"بلاغ المستخدم: {user_input}\nنوع الطارئ: {emergency_type}\nالنوع الفرعي: {emergency_subtype}"
    missing_info = get_missing_info_agent.run({"input": input_text})

    state["ai_response"] = missing_info
    state["report"] += f"\n📋 معلومات ناقصة مقترحة: {missing_info}"
    return state


# ==============================================================
# NODE 3 - الحصول على إرشادات السلامة
def get_safety_tips(state: EmergencyState) -> EmergencyState:

    if state.get("safety_tips") or not state.get("missing_info"):
        return state  # إذا موجودة مسبقاً → تجاهل

    emergency_type = state.get("emergency_type", "UNKNOWN")
    emergency_subtype = state.get("emergency_subtype", "")
    user_input = state.get("user_input", "")

    input_text = f"بلاغ المستخدم: {user_input}\nنوع الطارئ: {emergency_type}\nالنوع الفرعي: {emergency_subtype}"
    safety_tips = get_safety_tips_agent.run({"input": input_text})

    state["safety_tips"] = safety_tips
    state["ai_response"] = safety_tips
    return state


# ==============================================================
# NODE 4 - التحقق الذكي من المعلومة الجديدة

def check_user_missing_info(state: EmergencyState) -> EmergencyState:
    """
    إذا المستخدم كتب معلومة ناقصة مفيدة → نخزنها في state['missing_info']
    
    """
    if not state.get("emergency_type") :
       return state  # لا شيء لنضيفه

    user_input = state.get("user_input", "")

    input_text = f"بلاغ المستخدم: {user_input}\nنوع الطارئ: {state.get('emergency_type', 'غير معروف')}"

    # ✅ استدعاء الوكيل باستخدام invoke
    useful_info = check_user_missing_info_agent.run(input_text)
    try:
        if useful_info:
            if state.get("missing_info") is None:
                state["missing_info"] = ""
            # نضيف المعلومة الجديدة
            state["missing_info"] += useful_info
            state["report"] += f"\n✅ المستخدم أضاف معلومة مفيدة: {useful_info}"

    except Exception:
        pass

    return state

# ==============================================================

def build_emergency_coordinator_graph():
    builder = StateGraph(EmergencyState)

    # تعريف جميع النودز بشكل متسلسل
    builder.add_node("check_user_missing_info", check_user_missing_info)
    builder.add_node("detect_emergency_type", detect_emergency_type)
    builder.add_node("detect_missing_info", detect_missing_info)
    builder.add_node("get_safety_tips", get_safety_tips)

    builder.set_entry_point("check_user_missing_info")
    # بعد أي نود → نعود للنود الوسيط decide_next_nodes
    builder.add_edge("check_user_missing_info", "detect_emergency_type")
    builder.add_edge("detect_emergency_type", "detect_missing_info")
    builder.add_edge("detect_missing_info", "get_safety_tips")
    builder.add_edge("get_safety_tips", END)

    return builder.compile()
