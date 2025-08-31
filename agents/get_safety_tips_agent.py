import re
import json
from langchain.agents import initialize_agent, AgentType  # type: ignore
from langchain.tools import tool  # type: ignore
from api.llm import llm
from data.emergency_tips import emergency_tips

# =============================================================>

@tool
def get_safety_tips(input_text: str) -> str:
    """
    يُرجع نصائح السلامة المناسبة بناءً على نوع البلاغ ونوعه الفرعي ونص البلاغ.
    يرجع JSON فقط يحتوي قائمة نصائح السلامة.
    """

    # استخراج بيانات البلاغ
    user_input_match = re.search(r"بلاغ المستخدم:\s*(.*)", input_text)
    emergency_type_match = re.search(r"نوع الطارئ:\s*(.*)", input_text)
    emergency_subtype_match = re.search(r"النوع الفرعي:\s*(.*)", input_text)

    user_input = user_input_match.group(1).strip() if user_input_match else ""
    emergency_type = emergency_type_match.group(1).strip() if emergency_type_match else "UNKNOWN"
    emergency_subtype = emergency_subtype_match.group(1).strip() if emergency_subtype_match else ""

    # جلب النصائح المبدئية حسب النوع
    tips_example_list = emergency_tips.get(emergency_type, ["لا توجد نصائح متوفرة لهذا النوع من الطوارئ."])
    tips_prompt = "\n".join([f"- {tip}" for tip in tips_example_list])

    # إعداد البرومبت مع التنبيه بعدم ذكر الشرطة 🚨
    prompt = f"""
أنت مساعد طوارئ ذكي متخصص في تقديم إرشادات السلامة والإسعافات الأولية. 
أنت هنا لمساعدة المستخدم في أوقات الطوارئ وتقديم النصائح المناسبة التي قد تنقذ الأرواح.

بلاغ المستخدم: {user_input}
نوع الطارئ: {emergency_type}
نوع الطارئ الفرعي: {emergency_subtype}

يرجى تقديم نصائح وإرشادات سلامة مناسبة لهذا الموقف.

الأسئلة التالية موجودة فقط للمساعدة:
{tips_prompt}

بالإضافة إلى ذلك، يمكنك الإبداع في تقديم نصائح إضافية تراها مناسبة للموقف حتى لو لم تكن ضمن الأسئلة.

✅ أجب فقط بقائمة JSON تحتوي على نصائح السلامة المناسبة لهذا البلاغ.
[
  "نصيحة 1",
  "نصيحة 2",
  ...
]

⛔️ لا تكتب أي شرح أو جملة خارج JSON.
"""

    response = llm.invoke(prompt)
    print("[🔍 raw LLM response]:", response.content)

    try:
        # استخراج القائمة من الرد
        match = re.search(r"\[.*?\]", response.content, re.DOTALL)
        if not match:
            raise ValueError("JSON list not found")
        safety_tips = json.loads(match.group(0))

        # فلترة أي نصائح تتعلق بالشرطة نهائيًا 🚫
        filtered_tips = [
            tip for tip in safety_tips
            if not re.search(r"شرطة|الشرطة|اتصال|الاتصال|اتصل", tip, re.IGNORECASE)
        ]

        # التحقق من وجود نصائح بعد الفلترة
        if isinstance(filtered_tips, list) and filtered_tips:
            return json.dumps(filtered_tips, ensure_ascii=False)
        else:
            return json.dumps(["لا توجد نصائح متوفرة لهذا النوع من الطوارئ."], ensure_ascii=False)

    except Exception as e:
        print("[❌ parsing error]:", e)
        return json.dumps(["تعذر تحليل نصائح السلامة. يرجى إعادة المحاولة."], ensure_ascii=False)


# =============================================================>
# إنشاء العميل
get_safety_tips_agent = initialize_agent(
    tools=[get_safety_tips],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
)
