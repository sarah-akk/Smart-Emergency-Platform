import re
import json
from langchain.agents import initialize_agent, AgentType  # type: ignore
from langchain.tools import tool  # type: ignore
from data.emergency_tips import emergency_tips
from llm import llm  # type: ignore

# =============================================================>

@tool
def get_safety_tips(input_text: str) -> str:
    """
    يُرجع نصائح السلامة المناسبة بناءً على نوع البلاغ ونوعه الفرعي ونص البلاغ.
    يرجع JSON فقط يحتوي قائمة نصائح السلامة.
    """

    user_input_match = re.search(r"بلاغ المستخدم:\s*(.*)", input_text)
    emergency_type_match = re.search(r"نوع الطارئ:\s*(.*)", input_text)
    emergency_subtype_match = re.search(r"النوع الفرعي:\s*(.*)", input_text)

    user_input = user_input_match.group(1).strip() if user_input_match else ""
    emergency_type = emergency_type_match.group(1).strip() if emergency_type_match else "UNKNOWN"
    emergency_subtype = emergency_subtype_match.group(1).strip() if emergency_subtype_match else ""
    
    tips_example_list = emergency_tips.get(emergency_type, ["لا توجد نصائح متوفرة لهذا النوع من الطوارئ."])
    tips_prompt = "\n".join([f"- {tip}" for tip in tips_example_list])

    prompt = f"""

أنت مساعد طوارئ ذكي متخصص في تقديم إرشادات السلامة والإسعافات الأولية. 
أنت هنا لمساعدة المستخدم في أوقات الطوارئ وتقديم النصائح المناسبة التي قد تنقذ الأرواح.

بلاغ المستخدم: {user_input}

نوع الطارئ: {emergency_type}
نوع الطارئ الفرعي: {emergency_subtype}

يرجى تقديم نصائح وإرشادات سلامة مناسبة لهذا الموقف.

فيما يلي قائمة إرشادات مقترحة بناءً على النوع الأساسي:

{tips_prompt}

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
        match = re.search(r"\[.*?\]", response.content, re.DOTALL)
        if not match:
            raise ValueError("JSON list not found")
        safety_tips = json.loads(match.group(0))

        if isinstance(safety_tips, list) and safety_tips:
            return json.dumps(safety_tips, ensure_ascii=False)
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
