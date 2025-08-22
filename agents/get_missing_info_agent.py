import re
import json
from langchain.agents import initialize_agent, AgentType  # type: ignore
from langchain.tools import tool  # type: ignore
from llm import llm  # type: ignore

# قاعدة بيانات الأسئلة حسب نوع الطارئ
emergency_questions = {
  "CIVIL": [
    "الموقع الدقيق",
    "هل هناك مصابون أو مفقودون ",
    "هل الطرق مقطوعة ",
    "هل تحتاجون إلى إنقاذ فوري ",
    "موقع المشكلة ",
    "مدى تأثيرها (منزل واحد / حي كامل، ولدينا خيارات إضافية)",
    "منذ متى بدأت المشكلة؟ ",
    "هل يوجد خطر مباشر على المارة؟ ",
    "وصف الشخص (الطفل، المفقود...) ",
    "موقع آخر مشاهدة ",
    "هل هو في خطر مباشر؟ ",
    "مدة الغياب أو فقدان الاتصال ",
    "هل أظهر سلوكًا غريبًا أو خطرًا؟ ",
    "تفاصيل التواصل إن وُجدت "
  ],
  "FIRE": [
    "نوع المكان المحترق (منزل، سيارة، مستودع...) ",
    "هل هناك أشخاص عالقون ",
    "مدى انتشار الحريق ",
    "وجود مواد قابلة للانفجار ",
    "مصدر الانفجار أو التسرب ",
    "هل يوجد مصابون ",
    "هل تم إخلاء المكان ",
    "مدى الضرر المادي الظاهر "
  ],
  "MEDICAL": [
    "عمر المريض التقريبي ",
    "الوعي: واعي / فاقد وعي ",
    "هل يتنفس المريض ",
    "هل تلقى المريض أي إسعاف أولي ",
    "مدة استمرار الحالة "
  ],
  "POLICE": [
    "عدد المصابين ",
    "هل الطريق مغلق ",
    "موقع دقيق ",
    "نوع المركبات ",
    "عدد الأشخاص المشاركين ",
    "نوع السلاح إن وُجد ",
    "هل هناك مصابون ",
    "وصف الشخص أو الأشخاص المتورطين "
  ]
}

# =============================================================>


# تعريف الدالة tool بشكل صحيح
@tool
def get_missing_info(input_text: str) -> str:
    """
    يحلل البلاغ ويستنتج ما هي المعلومات الناقصة (مثل عدد المصابين، حالة الموقع، صور، ...).
    يرجع نصًا يحتوي على أسئلة توضيحية بلغة مهذبة بناءً على نوع الطارئ فقط.
    """
    
    import re, json

    user_input_match = re.search(r"بلاغ المستخدم:\s*(.*)", input_text)
    emergency_type_match = re.search(r"نوع الطارئ:\s*(.*)", input_text)
    emergency_subtype_match = re.search(r"النوع الفرعي:\s*(.*)", input_text)

    user_input = user_input_match.group(1).strip() if user_input_match else ""
    emergency_type = emergency_type_match.group(1).strip() if emergency_type_match else "UNKNOWN"
    emergency_subtype = emergency_subtype_match.group(1).strip() if emergency_subtype_match else ""

    questions = emergency_questions.get(emergency_type)
    if not questions:
        return f"❌ نوع الطارئ غير معروف: {emergency_type}"

    questions_prompt = "\n".join([f"- {q}" for q in questions])
    prompt = f"""
هذا بلاغ من المستخدم: {user_input}

❗️نوع البلاغ: {emergency_type}
🧩 النوع الفرعي: {emergency_subtype}

هل توجد أي معلومات ناقصة يجب على المستخدم إدخالها؟  
فيما يلي قائمة أمثلة لمساعدتك في تحديد المعلومات التي قد تكون ناقصة:

{questions_prompt}

✅ أجب فقط بقائمة JSON تحتوي على الأسئلة الناقصة من البلاغ.
[
"؟",
"؟",
...
]

⛔️ لا تكتب أي شرح أو جملة خارج JSON.
"""
    response = llm.invoke(prompt)
    try:
        match = re.search(r"\[.*?\]", response.content, re.DOTALL)
        missing_questions = json.loads(match.group(0)) if match else []
        if missing_questions:
            formatted_list = "\n".join([f"- {q}" for q in missing_questions])
            return f"✅ شكرًا على البلاغ. لتحسين الاستجابة، يُرجى توضيح بعض المعلومات:\n{formatted_list}"
        else:
            return "✅ البلاغ يحتوي على معلومات كافية كبداية، شكرًا لك."
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
