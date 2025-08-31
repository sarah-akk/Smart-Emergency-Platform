from langchain.tools import tool
from api.llm import llm
import json

@tool(description="يقرر ما إذا كان يجب طلب المزيد من المعلومات أو تقديم نصائح السلامة.")
def decide_next_step_agent(input_text: str) -> str:
    """
    يستعمل LLM ليقرر ما إذا كنا بحاجة إلى معلومات إضافية أم يمكننا الانتقال مباشرة إلى نصائح السلامة.
    """
    prompt = f"""
    أنت مساعد ذكي في إدارة الطوارئ.
    بناءً على المعلومات التالية، قرر ما إذا كان ينبغي طلب المزيد من التفاصيل أو إعطاء نصائح السلامة مباشرة.

    {input_text}

    اختر أحد الخيارين فقط وأعد النتيجة في صيغة JSON:
    {{
        "next_step": "detect_missing_info" أو "get_safety_tips",
        "reason": "سبب القرار هنا"
    }}
    """

    response = llm.predict(prompt)

    try:
        result = json.loads(response)
    except:
        import re
        json_str = re.search(r"\{.*\}", response, re.S)
        if json_str:
            result = json.loads(json_str.group())
        else:
            result = {"next_step": "get_safety_tips", "reason": "تعذر التحليل، الانتقال مباشرة لإعطاء النصائح."}

    return result
