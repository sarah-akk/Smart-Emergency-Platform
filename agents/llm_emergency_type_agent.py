from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from api.llm import llm
from data.emergency_types import CLASSES, SUBCLASSES
import json


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

        1. "type": choose ONLY one from {json.dumps(CLASSES)}
        2. "subtype": after selecting the type, choose ONLY from the corresponding list below:
           {json.dumps(SUBCLASSES, ensure_ascii=False)}
        3. "severity": a float number between 0 and 1 indicating severity (0 = low, 1 = extremely critical).

        Respond ONLY in JSON format, like this:
        {{
            "type": "POLICE",
            "subtype": "stolen_car",
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
        valid_subtypes = SUBCLASSES.get(result["type"], [])
        if result["subtype"] not in valid_subtypes:
            result["subtype"] = valid_subtypes[0] if valid_subtypes else "other"
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
