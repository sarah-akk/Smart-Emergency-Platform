from langchain.tools import tool
from api.llm import llm
import json
import re

@tool(description="يقرر ما إذا كان يجب طلب المزيد من المعلومات أو تقديم نصائح السلامة أو إنهاء المحادثة.")
def decide_next_step_agent(input_text: str) -> str:
    """
    يستعمل LLM ليقرر:
    1. هل نحتاج إلى المزيد من التفاصيل؟
    2. أم يجب تقديم نصائح السلامة؟
    3. أم يمكن إنهاء المحادثة إذا اكتملت جميع المعلومات وتم تقديم النصائح؟
    """
    prompt = f"""
    أنت مساعد ذكي لإدارة الطوارئ.
    مهمتك هي تحليل حالة المحادثة الحالية وتحديد الخطوة التالية فقط.

    - إذا كانت هناك معلومات أساسية ناقصة → أعد "detect_missing_info".
    - إذا كانت المعلومات مكتملة لكن لم نقدم نصائح بعد → أعد "get_safety_tips".
    - إذا اكتملت جميع المعلومات وتم إعطاء نصائح السلامة → أعد "terminated".

    أعد النتيجة في صيغة JSON فقط:
    {{
        "next_step": "detect_missing_info" أو "get_safety_tips" أو "terminated",
        "reason": "اشرح سبب القرار هنا"
    }}

    السياق:
    {input_text}
    """

    # استدعاء LLM
    response = llm.predict(prompt)

    try:
        # محاولة تحليل الاستجابة كـ JSON مباشرة
        result = json.loads(response)
    except:
        # محاولة استخراج JSON من داخل الرد باستخدام Regex
        json_str = re.search(r"\{.*\}", response, re.S)
        if json_str:
            result = json.loads(json_str.group())
        else:
            # fallback في حالة الفشل التام → نرجع إلى تقديم النصائح
            result = {
                "next_step": "get_safety_tips",
                "reason": "تعذر التحليل، الانتقال لإعطاء النصائح."
            }

    return result
