import re
import json
from langchain.agents import initialize_agent, AgentType  # type: ignore
from langchain.tools import tool  # type: ignore
from data.emergency_questions import emergency_questions
from llm import llm  # type: ignore

# =============================================================>
@tool
def get_missing_info(input_text: str) -> str:
    """
    يحلل البلاغ ويحدد فقط المعلومات الناقصة، ويعرضها مع جملة تمهيدية محددة.
    """

    # استخراج البيانات الأساسية من البلاغ
    user_input_match = re.search(r"بلاغ المستخدم:\s*(.*)", input_text)
    emergency_type_match = re.search(r"نوع الطارئ:\s*(.*)", input_text)
    emergency_subtype_match = re.search(r"النوع الفرعي:\s*(.*)", input_text)

    user_input = user_input_match.group(1).strip() if user_input_match else ""
    emergency_type = emergency_type_match.group(1).strip() if emergency_type_match else "UNKNOWN"
    emergency_subtype = emergency_subtype_match.group(1).strip() if emergency_subtype_match else ""

    # الحصول على الأسئلة المناسبة حسب نوع الطارئ
    questions = emergency_questions.get(emergency_type)
    if not questions:
        return f"❌ نوع الطارئ غير معروف: {emergency_type}"

    questions_prompt = "\n".join([f"- {q}" for q in questions])

    # إعداد البرومبت للـ LLM
    prompt = f"""
بلاغ المستخدم: {user_input}

❗️نوع البلاغ: {emergency_type}
🧩 النوع الفرعي: {emergency_subtype}

مهمتك: حدد فقط الأسئلة الناقصة في البلاغ، والتي لم يذكرها المستخدم.
يمكنك أيضًا استنتاج بعض المعلومات بنفسك إذا لزم الأمر لتحديد ما هو مفقود.

الأسئلة التالية موجودة فقط للمساعدة، ويمكنك الاعتماد عليها لتحديد ما هو ناقص:

{questions_prompt}

⛔️ أرجع الرد بصيغة JSON فقط:
[
  "السؤال الناقص الأول",
  "السؤال الناقص الثاني",
  ...
]
لا تضف أي شرح أو نص خارج JSON.
    """

    response = llm.invoke(prompt)

    try:
        match = re.search(r"\[.*?\]", response.content, re.DOTALL)
        missing_questions = json.loads(match.group(0)) if match else []

        # إذا وجد أسئلة ناقصة
        if missing_questions:
            formatted_list = "\n".join(
                [f"{idx+1}. {q}" for idx, q in enumerate(missing_questions)]
            )
            return f"شكرًا على البلاغ. لتحسين الاستجابة، يُرجى توضيح بعض المعلومات:\n{formatted_list}"
        else:
            return "✅ البلاغ يحتوي على جميع المعلومات المطلوبة، شكرًا لك."

    except Exception as e:
        print("[❌ parsing error]:", e)
        return "تعذر تحليل المعلومات الناقصة. يُرجى إعادة المحاولة."


# =============================================================>
# إنشاء العميل
get_missing_info_agent = initialize_agent(
    tools=[get_missing_info],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
)
