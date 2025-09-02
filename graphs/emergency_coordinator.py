# coordinator_graph.py
import json
from langgraph.graph import StateGraph, END
from agents.decide_next_step_agent import decide_next_step_agent
from agents.intent_detection_agent import detect_intent
from agents.llm_emergency_type_agent import llm_emergency_type_agent
# from agents.emergency_type_agent import emergency_type_agent
from agents.get_missing_info_agent import get_missing_info_agent
from agents.get_safety_tips_agent import get_safety_tips_agent
from agents.check_user_missing_info_agent import check_user_missing_info_agent
from typing_extensions import TypedDict
from data.emergency_types import SUBTYPE_TRANSLATIONS, severity_to_text
from helpers.extract_history_text import extract_history_text
from helpers.generate_report_section import generate_report_section

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
    next_step : str | None
    name : str | None
    discription : str | None
    report: str
    not_important: bool

# ==============================================================
# NODE  - تحديد نية المستخدم
# ==============================================================
def detect_intent_node(state: EmergencyState) -> EmergencyState:

    history_text = extract_history_text(state)
    
    intent = detect_intent.run({
        "history": history_text,
        "text": state["user_input"]
    })

    # إذا البلاغ غير مهم → نوقف أي معالجة لاحقة
    if not intent.get("emergency", False):
        state["ai_response"] = intent.get("reply", "👋 أهلاً! كيف يمكنني مساعدتك؟")
        state["not_important"] = True
        return state

    # البلاغ مهم → نكمل
    state["not_important"] = False
    return state


# ==============================================================
# NODE  - تحديد نوع الطارئ
# ==============================================================

def detect_emergency_type(state: EmergencyState) -> EmergencyState:

    if state.get("emergency_type"):
        return state  # النوع موجود مسبقاً → لا حاجة للوكيل

    if state.get("not_important", False):
        return state

    history_text = extract_history_text(state)    
    result = llm_emergency_type_agent.invoke({"input": state["user_input"]})

    if "intermediate_steps" in result and len(result["intermediate_steps"]) > 0:
        tool_output = result["intermediate_steps"][-1][1]
        if isinstance(tool_output, dict):
            arabic_subtype = SUBTYPE_TRANSLATIONS.get(tool_output['subtype'], "طوارئ غير معروفة")
            severity_text = severity_to_text(tool_output['severity'])

            state["report"] = (state.get("report") or "") + f"\n🚨 نوع الطوارئ: {arabic_subtype}"
            state["report"] += f"\n⚠️ مستوى الخطورة: {severity_text}"

            # ✅ استدعاء التابع الجديد لتوليد الملخص والاسم المختصر
            summary, short_name = generate_report_section(state['user_input'])
            state["name"] = f"\n{short_name}"
            state["discription"] = f"\n{summary}"
            state["report"] += f"\n📝 البلاغ: {summary}"
                
            state["emergency_type"] = tool_output["type"]
            state["emergency_subtype"] = tool_output["subtype"]
            state["severity"] = float(tool_output["severity"]) 
            return state

    state["emergency_type"] = ""
    state["emergency_subtype"] = ""
    state["severity"] = ""
    return state


# ==============================================================
# NODE  - الحصول على المعلومات الناقصة
# ==============================================================

def detect_missing_info(state: EmergencyState) -> EmergencyState:

    if not state.get("emergency_type"):
        return state 

    if state.get("not_important", False) or state["next_step"] == "get_safety_tips" or state["next_step"] == "terminated":
        return state

    # if state.get("missing_info") or not state.get("emergency_type"):
    #    return state

    history_text = extract_history_text(state)    
    input_text = (
    f"بلاغ المستخدم: {state['user_input']}\n"
    f"نوع الطارئ: {state['emergency_type']}\n"
    f"النوع الفرعي: {state['emergency_subtype']}\n"
    f"تاريخ المحادثة: {history_text}"
    ) 
    missing_info = get_missing_info_agent.run({"input": input_text})

    state["ai_response"] = missing_info
    return state


# ==============================================================
# NODE  - الحصول على إرشادات السلامة
# ==============================================================

def get_safety_tips(state: EmergencyState) -> EmergencyState:

    if state.get("not_important", False) or state["next_step"] == "detect_missing_info" or state["next_step"] == "terminated":
        return state

    # if state.get("safety_tips") or not state.get("missing_info"):
    #     return state  

    history_text = extract_history_text(state)    

    input_text = (
    f"بلاغ المستخدم: {state['user_input']}\n"
    f"نوع الطارئ: {state['emergency_type']}\n"
    f"النوع الفرعي: {state['emergency_subtype']}\n"
    f"تاريخ المحادثة: {history_text}"
    ) 

    safety_tips = get_safety_tips_agent.run({"input": input_text})

    state["safety_tips"] = safety_tips
    state["ai_response"] = safety_tips
    return state


# ==============================================================
# NODE  - التحقق الذكي من المعلومة الجديدة
# ==============================================================

def check_user_missing_info(state: EmergencyState) -> EmergencyState:
    """
    إذا المستخدم كتب معلومة ناقصة مفيدة → نخزنها في state['missing_info']
    
    """
    if not state.get("emergency_type") :
       return state  # لا شيء لنضيفه

    if state.get("not_important", False):
        return state

    user_input = state.get("user_input", "")

    history_text = extract_history_text(state)    
    input_text = (
    f"بلاغ المستخدم: {state['user_input']}\n"
    f"نوع الطارئ: {state['emergency_type']}\n"
    f"النوع الفرعي: {state['emergency_subtype']}\n"
    f"تاريخ المحادثة: {history_text}"
    ) 

    # ✅ استدعاء الوكيل باستخدام invoke
    useful_info = check_user_missing_info_agent.run(input_text)
    try:
        if useful_info:
            if state.get("missing_info") is None:
                state["missing_info"] = ""
            # نضيف المعلومة الجديدة
            state["missing_info"] += useful_info
            state["report"] += f"\n🆘 معلومة جديدة: {useful_info.split(':', 1)[-1].strip()}"

    except Exception:
        pass

    return state

# ==============================================================
# NODE  - التحقق الذكي من المعلومة الجديدة
# ==============================================================
def decide_next_step(state: EmergencyState) -> EmergencyState:
    """
    نود ذكية تستعمل LLM لتحديد ما إذا كان يجب طلب المزيد من المعلومات أو تقديم نصائح السلامة.
    """
    if state.get("not_important", False):
        return state

    history_text = extract_history_text(state)
    input_text = (
        f"بلاغ المستخدم: {state['user_input']}\n"
        f"نوع الطارئ: {state.get('emergency_type')}\n"
        f"النوع الفرعي: {state.get('emergency_subtype')}\n"
        f"تاريخ المحادثة:\n{history_text}"
    )
    
    print(input_text)

    decision = decide_next_step_agent.run(input_text)

    if isinstance(decision, str):
        try:
            decision = json.loads(decision)
        except:
            decision = {"next_step": "get_safety_tips", "reason": "تعذر التحليل."}

    state["next_step"] = decision["next_step"]
    return state

# ==============================================================


def build_emergency_coordinator_graph():
    builder = StateGraph(EmergencyState)

    # إضافة النود الجديد أولاً
    builder.add_node("detect_intent_node", detect_intent_node)
    builder.add_node("check_user_missing_info", check_user_missing_info)
    builder.add_node("detect_emergency_type", detect_emergency_type)
    builder.add_node("decide_next_step", decide_next_step)
    builder.add_node("detect_missing_info", detect_missing_info)
    builder.add_node("get_safety_tips", get_safety_tips)

    # نقطة الدخول للنود الجديد
    builder.set_entry_point("detect_intent_node")

    # إذا البلاغ مهم → نكمل الباقي
    builder.add_edge("detect_intent_node", "check_user_missing_info")
    builder.add_edge("check_user_missing_info", "detect_emergency_type")
    builder.add_edge("detect_emergency_type", "decide_next_step")
    builder.add_edge("decide_next_step", "detect_missing_info")
    builder.add_edge("detect_missing_info", "get_safety_tips")
    builder.add_edge("get_safety_tips", END)

    return builder.compile()
