from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
import tensorflow as tf
import pickle
import numpy as np
from api.llm import llm

# ========================= تحميل الملفات ==========================
with open("Models/preprocessing_objects.pkl", "rb") as f:
    preprocessing = pickle.load(f)

tokenizer = preprocessing["tokenizer"]
class_encoder = preprocessing["class_encoder"]
subclass_encoder = preprocessing["subclass_encoder"]
max_len = preprocessing.get("max_length", 100)
severity_scaler = preprocessing.get("severity_scaler", None)

model = tf.saved_model.load("Models/arabic_emergency_marbert_model")
infer = model.signatures["serving_default"]

# ====================== أداة التصنيف ============================
@tool(description="يصنف نوع الحالة وخطورتها باستخدام النموذج المدرب.")
def classify_emergency(text: str) -> dict:
    try:
        encoding = tokenizer.encode_plus(
            text,
            truncation=True,
            padding="max_length",
            max_length=max_len,
            return_tensors="tf"
        )

        result = infer(
            input_ids=encoding["input_ids"],
            attention_mask=encoding["attention_mask"]
        )

        # التنبؤ الأساسي (النوع)
        class_pred = result["output_1"].numpy()
        class_index = np.argmax(class_pred, axis=1)[0]
        class_label = class_encoder.classes_[class_index]

        # التنبؤ الفرعي (النوع الفرعي)
        subclass_pred = result["output_2"].numpy()
        subclass_index = np.argmax(subclass_pred, axis=1)[0]
        subclass_label = subclass_encoder.classes_[subclass_index]

        # التنبؤ بالخطورة
        severity_pred = result["output_0"].numpy()
        severity_value = severity_pred[0][0]
        severity_label = (
            severity_scaler.inverse_transform([[severity_value]])[0][0]
            if severity_scaler else float(severity_value)
        )

        # نحولها ل float عادي من بايثون
        severity_label = float(severity_label)

        return {
            "type": class_label,
            "subtype": subclass_label,
            "severity": severity_label
        }

    except Exception as e:
        print("[❌ Error in model prediction]:", str(e))
        return {
            "type": "غير معروف",
            "subtype": "غير معروف",
            "severity": "غير معروف"
        }

# ====================== تهيئة الـ Agent ==========================
emergency_type_agent = initialize_agent(
    tools=[classify_emergency],
    llm=llm,
    agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose=False,
    return_intermediate_steps=True  # << مهم جداً
)

