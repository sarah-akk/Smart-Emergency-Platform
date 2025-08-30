# coordinator_graph.py
from langgraph.graph import StateGraph, END
from agents.intent_detection_agent import detect_intent
from agents.llm_emergency_type_agent import llm_emergency_type_agent
# from agents.emergency_type_agent import emergency_type_agent
from agents.get_missing_info_agent import get_missing_info_agent
from agents.get_safety_tips_agent import get_safety_tips_agent
from agents.check_user_missing_info_agent import check_user_missing_info_agent
from typing_extensions import TypedDict
from data.emergency_types import SUBTYPE_TRANSLATIONS, severity_to_text
from llm import llm  

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
    not_important: bool



def detect_intent_node(state: EmergencyState) -> EmergencyState:
    intent = detect_intent.run(state["user_input"])

    # إذا البلاغ غير مهم → نوقف أي معالجة لاحقة
    if not intent.get("emergency", False):
        state["ai_response"] = intent.get("reply", "👋 أهلاً! كيف يمكنني مساعدتك؟")
        state["not_important"] = True
        return state

    # البلاغ مهم → نكمل
    state["not_important"] = False
    return state


# ==============================================================
# NODE 1 - تحديد نوع الطارئ
def detect_emergency_type(state: EmergencyState) -> EmergencyState:

    if state.get("emergency_type"):
        return state  # النوع موجود مسبقاً → لا حاجة للوكيل

    if state.get("not_important", False):
        return state
        
    result = llm_emergency_type_agent.invoke({"input": state["user_input"]})

    if "intermediate_steps" in result and len(result["intermediate_steps"]) > 0:
        tool_output = result["intermediate_steps"][-1][1]
        if isinstance(tool_output, dict):
            arabic_subtype = SUBTYPE_TRANSLATIONS.get(tool_output['subtype'], "طوارئ غير معروفة")
            severity_text = severity_to_text(tool_output['severity'])

            state["report"] = (state.get("report") or "") + f"\n🚨 نوع الطوارئ: {arabic_subtype}"
            state["report"] += f"\n⚠️ مستوى الخطورة: {severity_text}"

            # ✅ استدعاء LLM لعمل ملخص واضح للبلاغ
            try:
                summary_prompt = f"""
                أنت مساعد ذكي متخصص في صياغة بلاغات الطوارئ.
                مهمتك: إعادة صياغة البلاغ التالي بطريقة رسمية، مختصرة وواضحة، لتكون جاهزة للإرسال إلى فرق الطوارئ:
                البلاغ: "{state['user_input']}"
                
                يجب أن يكون النص الناتج موجزًا، دقيقًا، ورسميًا.
                """
                summary_response = llm.predict(summary_prompt).strip()
                state["report"] += f"\n📝: {summary_response}"
            except:
                # في حال حدوث أي خطأ نضع النص كما هو
                state["report"] += f"\n📝: {state['user_input']}"
                
            state["emergency_type"] = tool_output["type"]
            state["emergency_subtype"] = tool_output["subtype"]
            state["severity"] = float(tool_output["severity"])  # ضمان إرجاع float
            return state

    state["emergency_type"] = ""
    state["emergency_subtype"] = ""
    state["severity"] = ""
    return state


# ==============================================================

# NODE 2 - الحصول على المعلومات الناقصة
def detect_missing_info(state: EmergencyState) -> EmergencyState:

    if state.get("missing_info") or not state.get("emergency_type"):
        return state  # لا نستدعي الوكيل إذا المعلومات مكتملة أو النوع غير معروف

    if state.get("not_important", False):
        return state

    emergency_type = state.get("emergency_type", "UNKNOWN")
    emergency_subtype = state.get("emergency_subtype", "")
    user_input = state.get("user_input", "")

    if emergency_type == "UNKNOWN":
        state["missing_info"] = "❌ لا يمكن تحديد المعلومات الناقصة بدون نوع الطارئ."
        return state

    input_text = f"بلاغ المستخدم: {user_input}\nنوع الطارئ: {emergency_type}\nالنوع الفرعي: {emergency_subtype}"
    missing_info = get_missing_info_agent.run( input_text)

    state["ai_response"] = missing_info
    return state


# ==============================================================
# NODE 3 - الحصول على إرشادات السلامة
def get_safety_tips(state: EmergencyState) -> EmergencyState:

    if state.get("safety_tips") or not state.get("missing_info"):
        return state  # إذا موجودة مسبقاً → تجاهل

    if state.get("not_important", False):
        return state

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

    if state.get("not_important", False):
        return state

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
            state["report"] += f"\n🆘 معلومة جديدة: {useful_info.split(':', 1)[-1].strip()}"

    except Exception:
        pass

    return state

# ==============================================================

def build_emergency_coordinator_graph():
    builder = StateGraph(EmergencyState)

    # إضافة النود الجديد أولاً
    builder.add_node("detect_intent_node", detect_intent_node)
    builder.add_node("check_user_missing_info", check_user_missing_info)
    builder.add_node("detect_emergency_type", detect_emergency_type)
    builder.add_node("detect_missing_info", detect_missing_info)
    builder.add_node("get_safety_tips", get_safety_tips)

    # نقطة الدخول للنود الجديد
    builder.set_entry_point("detect_intent_node")

    # إذا البلاغ مهم → نكمل الباقي
    builder.add_edge("detect_intent_node", "check_user_missing_info")
    builder.add_edge("check_user_missing_info", "detect_emergency_type")
    builder.add_edge("detect_emergency_type", "detect_missing_info")
    builder.add_edge("detect_missing_info", "get_safety_tips")
    builder.add_edge("get_safety_tips", END)

    return builder.compile()
