import re
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool

from api.llm import llm


@tool
def check_user_missing_info_agent(input_text: str) -> str:
    """
    يتحقق من أن المعلومة الجديدة التي أدخلها المستخدم مفيدة ومكملة للبلاغ.
    """
    prompt = f"""
 مهم جدًا: أعد المعلومة المضافة فقط من المستخدم بدون أي تعديل أو إضافة أو عنوان أو تنسيق أو كلمات زائدة. 

------------------------------
{input_text}
------------------------------

- إذا كانت المعلومة مفيدة → أعد بلاغ المستخدم كما هو بالضبط.
- إذا كانت المعلومة غير مفيدة → أعد فقط نص فارغ.
- ممنوع إضافة أي جمل تفسيرية أو نصائح أو إعادة صياغة.
- لا تضف نوع الحادث .
- المخرجات يجب أن تكون مطابقة 100% للمعلومة أو فارغة فقط.
"""
    response = llm.invoke(prompt)
    return response.content.strip()
