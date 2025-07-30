import re
import json
from langchain.agents import initialize_agent, AgentType  # type: ignore
from langchain.tools import tool  # type: ignore
from llm import llm  # type: ignore

# قاعدة بيانات الأسئلة حسب نوع الطارئ
emergency_questions = {
    "حوادث المرور": [
        "عدد المصابين",
        "هل الطريق مغلق",
        "موقع دقيق",
        "نوع المركبات"
    ],
    "الحرائق": [
        "نوع المكان المحترق (منزل، سيارة، مستودع...)",
        "هل هناك أشخاص عالقون",
        "مدى انتشار الحريق",
        "وجود مواد قابلة للانفجار"
    ],
    "الانفجارات والتسريبات": [
        "مصدر الانفجار أو التسرب",
        "هل يوجد مصابون",
        "هل تم إخلاء المكان",
        "مدى الضرر المادي الظاهر"
    ],
    "الجرائم والحوادث الأمنية": [
        "عدد الأشخاص المشاركين",
        "نوع السلاح إن وُجد",
        "هل هناك مصابون",
        "وصف الشخص أو الأشخاص المتورطين"
    ],
    "الحالات الطبية الطارئة": [
        "عمر المريض التقريبي",
        "الوعي: واعي / فاقد وعي",
        "هل يتنفس المريض",
        "هل تلقى المريض أي إسعاف أولي",
        "مدة استمرار الحالة"
    ],
    "الكوارث الطبيعية": [
        "الموقع الدقيق",
        "هل هناك مصابون أو مفقودون",
        "هل الطرق مقطوعة",
        "هل تحتاجون إلى إنقاذ فوري"
    ],
    "طوارئ بنية تحتية": [
        "موقع المشكلة",
        "مدى تأثيرها (منزل واحد / حي كامل)",
        "منذ متى بدأت المشكلة؟",
        "هل يوجد خطر مباشر على المارة؟"
    ],
    "طوارئ إنسانية أو اجتماعية": [
        "وصف الشخص (الطفل، المفقود...)",
        "موقع آخر مشاهدة",
        "هل هو في خطر مباشر؟",
        "مدة الغياب أو فقدان الاتصال",
        "هل أظهر سلوكًا غريبًا أو خطرًا؟",
        "تفاصيل التواصل إن وُجدت"
    ]
}

@tool
def get_missing_info(user_input: str, emergency_type: str) -> str:
    """
    يحلل البلاغ ويستنتج ما هي المعلومات الناقصة (مثل عدد المصابين، حالة الموقع، صور، ...).
    يرجع نصًا يحتوي على أسئلة توضيحية بلغة مهذبة بناءً على نوع الطارئ فقط.
    """

    # التحقق من وجود النوع في القاموس
    questions = emergency_questions.get(emergency_type)
    if not questions:
        return f"❌ نوع الطارئ غير معروف: {emergency_type}"

    questions_prompt = "\n".join([f"- {q}" for q in questions])

    prompt = f"""
    هذا بلاغ من المستخدم: {user_input}

    ❗️نوع البلاغ: {emergency_type}

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
    print("[🔍 raw LLM response]:", response.content)

    try:
        # استخراج أول قائمة JSON باستخدام Regex
        match = re.search(r"\[.*?\]", response.content, re.DOTALL)
        if not match:
            raise ValueError("JSON list not found")

        missing_questions = json.loads(match.group(0))

        if isinstance(missing_questions, list) and missing_questions:
            formatted_list = "\n".join([f"- {q}" for q in missing_questions])
            return f"✅ شكرًا على البلاغ. لتحسين الاستجابة، يُرجى توضيح بعض المعلومات:\n{formatted_list}"
        else:
            return "✅ البلاغ يحتوي على معلومات كافية كبداية، شكرًا لك."

    except Exception as e:
        print("[❌ parsing error]:", e)
        return "تعذر تحليل المعلومات الناقصة. يُرجى إعادة المحاولة."

# إنشاء العميل
get_missing_info_agent = initialize_agent(
    tools=[get_missing_info],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)
