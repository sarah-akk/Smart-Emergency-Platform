def extract_history_text(state: dict) -> str:
    """
    دالة لاستخراج نص المحادثة الكاملة من history إذا وجد،
    أو ترجع user_input إذا لم يكن هناك تاريخ للمحادثة.
    """
    if state.get("history") and isinstance(state["history"], dict):
        sorted_keys = sorted(state["history"].keys(), key=lambda k: int(k))
        texts = [
            msg["text"]
            for k in sorted_keys
            if isinstance(state["history"][k], dict) and state["history"][k].get("text")
            for msg in [state["history"][k]]
        ]
        return "\n".join(texts)
    return state.get("user_input", "")