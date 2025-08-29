from langchain.tools import tool
from llm import llm
import json

@tool(description="تحليل نية المستخدم لمعرفة إن كانت الرسالة بلاغ طارئ أم كلام عادي")
def detect_intent(text: str) -> dict:
    """
    يستخدم LLM لتحديد نية المستخدم:
    - إذا كانت الرسالة بلاغ طارئ → نرجع emergency = True
    - إذا كانت الرسالة كلام عابر أو تحية → emergency = False
    """

    try:
        prompt = f"""
        أنت مساعد ذكي للطوارئ.
        مهمتك تحديد نية المستخدم بدقة من النص التالي: "{text}".

        الخيارات المحتملة:
        1. إذا كانت الرسالة **بلاغ طارئ جديد** → emergency = true.
        2. إذا كانت الرسالة **مكملة لبلاغ طارئ سابق** (معلومات إضافية) → emergency = true.
        3. إذا كانت الرسالة **كلام عابر أو غير مهمة** → emergency = false.

        أعد النتيجة في صيغة JSON فقط، مثل:
        {{
            "emergency": true أو false,
            "reply": "الرد المناسب إذا لم تكن حالة طارئة"
        }}
        """

        response = llm.predict(prompt)

        # نحاول استخراج JSON من الرد
        try:
            result = json.loads(response)
        except:
            import re
            json_str = re.search(r"\{.*\}", response, re.S)
            if json_str:
                result = json.loads(json_str.group())
            else:
                result = {
                    "emergency": False,
                    "reply": "👋 أهلاً! كيف يمكنني مساعدتك؟"
                }

        # لو الـ LLM رجّع نتيجة ناقصة نضيف القيم الافتراضية
        if "emergency" not in result:
            result["emergency"] = False
        if "reply" not in result:
            result["reply"] = "👋 أهلاً! كيف يمكنني مساعدتك؟"

        return result

    except Exception:
        return {
            "emergency": False,
            "reply": "👋 أهلاً! كيف يمكنني مساعدتك؟"
        }
