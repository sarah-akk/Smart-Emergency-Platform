import re
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from llm import llm


@tool
def check_user_missing_info_agent(input_text: str) -> str:
    """
    يتحقق من أن المعلومة الجديدة التي أدخلها المستخدم مفيدة ومكملة للبلاغ.
    """
    prompt = f"""
مهم جدًا: أعد فقط المعلومة المضافة من المستخدم كما هي بدون أي شرح أو تحليل أو تعليقات إضافية.

------------------------------
{input_text}
------------------------------

- إذا كانت المعلومة مفيدة → أعد بلاغ المستخدم كما هو بالضبط.
- إذا كانت المعلومة غير مفيدة → أعد فقط نص فارغ.
- ممنوع إضافة أي جمل تفسيرية أو نصائح أو إعادة صياغة.
- المخرجات يجب أن تكون مطابقة 100% للمعلومة أو فارغة فقط.
"""
    response = llm.invoke(prompt)
    return response.content.strip()
