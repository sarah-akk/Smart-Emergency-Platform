from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from llm import llm  # ✅ Your OpenAI LLM instance
import json

# ========================= التصنيفات المعتمدة ==========================
CLASSES = [
    "CIVIL", "POLICE", "MEDICAL", "TRAFFIC", "FIRE"
]

SUBCLASSES = [
    "missing_item", "stolen_car", "theft", "complaint", "armed_robbery",
    "found_item", "missing_person", "body", "road_obstruction", "violent_crime",
    "verbal_abuse", "fight", "blood_donation_req", "gun_fight", "missing_person_found",
    "explosion", "cardiac_arrest", "kidnapping", "murder", "charity",
    "gunwound", "unconscious", "major_accident", "structure_fire", "vandalism",
    "wildfire", "warning", "fallen", "rouge_faction", "unknown_fire"
]

# ====================== أداة التصنيف باستخدام LLM ======================

@tool(description="يصنف نوع الحالة وخطورتها باستخدام LLM. يجب أن يختار القيم فقط من القوائم المعطاة.")
def classify_emergency(text: str) -> dict:
    """
    يعتمد على OpenAI LLM لتصنيف نوع الحالة ونوعها الفرعي وخطورتها
    """
    try:
        prompt = f"""
        You are an emergency classification assistant.
        Given the Arabic incident description: "{text}", 
        classify it into:
        - "type": one of {json.dumps(CLASSES)}
        - "subtype": one of {json.dumps(SUBCLASSES)}
        - "severity": a float number between 0 and 1 indicating severity (0 = low, 1 = extremely critical).

        Respond ONLY in JSON format, like this:
        {{
            "type": "...",
            "subtype": "...",
            "severity": 0.85
        }}
        """

        response = llm.predict(prompt)

        # نحاول نعمل Parse للـ JSON من الرد
        try:
            result = json.loads(response)
        except:
            # إذا ما كان الرد JSON مضبوط نعمل إصلاح سريع
            import re
            json_str = re.search(r"\{.*\}", response, re.S)
            if json_str:
                result = json.loads(json_str.group())
            else:
                raise ValueError("Invalid LLM response format.")

        # التأكد من أن القيم مسموحة
        if result["type"] not in CLASSES:
            result["type"] = "CIVIL"
        if result["subtype"] not in SUBCLASSES:
            result["subtype"] = "missing_item"
        result["severity"] = float(result.get("severity", 0.5))

        return result

    except Exception as e:
        print("[❌ Error in LLM classification]:", str(e))
        return {
            "type": "",
            "subtype": "",
            "severity": ""
        }

# ====================== تهيئة الـ Agent ==========================

llm_emergency_type_agent = initialize_agent(
    tools=[classify_emergency],
    llm=llm,
    agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose=False,
    return_intermediate_steps=True
)
