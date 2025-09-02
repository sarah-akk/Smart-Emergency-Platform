def extract_history_text(state: dict) -> str:
    """
    دالة لاستخراج نص المحادثة من history بترتيب عكسي (الأحدث أولاً)
    مع تحديد المرسل بشكل واضح لزيادة وضوح السياق للـ LLM.
    """
    if state.get("history") and isinstance(state["history"], dict):
        # ترتيب الرسائل من الأحدث للأقدم
        sorted_keys = sorted(state["history"].keys(), key=lambda k: int(k), reverse=True)
        messages = []

        for k in sorted_keys:
            msg = state["history"][k]
            if isinstance(msg, dict) and msg.get("text"):
                sender = "👤 المستخدم" if msg.get("state") is not None else "🤖 المساعد"
                messages.append(f"{sender}:\n{msg['text']}\n" + "-"*50)

        return "\n".join(messages)

    # إذا لم يكن هناك history نرجع فقط user_input
    return f"👤 المستخدم:\n{state.get('user_input', '')}"
