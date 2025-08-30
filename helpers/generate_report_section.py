from typing import Tuple
from api.llm import llm

# تابع لتوليد الملخص واسم مختصر للبلاغ
def generate_report_section(user_input: str) -> Tuple[str, str]:
    """
    يُولّد ملخص رسمي موجز للبلاغ + اسم مختصر يمكن استخدامه في التقارير.
    """
    try:
        prompt = f"""
        أنت مساعد ذكي للطوارئ.
        
        مهمتك: 
        1. إعادة صياغة البلاغ التالي بطريقة رسمية، موجزة وواضحة لتكون جاهزة للإرسال لفرق الطوارئ.
        2. توليد اسم مختصر للبلاغ لا يتجاوز 5 كلمات ويصف الحالة بشكل واضح.

        البلاغ: "{user_input}"

        أعد الإجابة في صيغة JSON فقط، بهذا الشكل:
        {{
            "summary": "ملخص رسمي موجز للبلاغ",
            "short_name": "اسم مختصر للبلاغ"
        }}
        """
        response = llm.predict(prompt).strip()

        import json, re
        try:
            result = json.loads(response)
        except:
            json_str = re.search(r"\{.*\}", response, re.S)
            if json_str:
                result = json.loads(json_str.group())
            else:
                # fallback إذا فشل ال LLM
                result = {
                    "summary": user_input,
                    "short_name": "بلاغ طارئ"
                }

        # لو في نقص بالرد
        summary = result.get("summary", user_input)
        short_name = result.get("short_name", "بلاغ طارئ")

        return summary, short_name

    except:
        # fallback في حالة فشل أي شيء
        return user_input, "بلاغ طارئ"
