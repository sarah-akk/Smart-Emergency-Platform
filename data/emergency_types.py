# ========================= التصنيفات المعتمدة ==========================
CLASSES = [
    "CIVIL", "POLICE", "MEDICAL", "TRAFFIC", "FIRE"
]

SUBCLASSES = {
    "CIVIL": [
        "missing_item",
        "complaint",
        "found_item",
        "blood_donation_req",
        "charity",
        "warning"
    ],
    "POLICE": [
        "stolen_car",
        "theft",
        "armed_robbery",
        "missing_person",
        "violent_crime",
        "verbal_abuse",
        "fight",
        "gun_fight",
        "missing_person_found",
        "explosion",
        "kidnapping",
        "murder",
        "vandalism",
        "rouge_faction"
    ],
    "MEDICAL": [
        "body",
        "cardiac_arrest",
        "gunwound",
        "unconscious",
        "fallen"
    ],
    "TRAFFIC": [
        "road_obstruction",
        "major_accident"
    ],
    "FIRE": [
        "structure_fire",
        "wildfire",
        "unknown_fire"
    ]
}


# 🟢 خريطة لترجمة نوع الطوارئ من الإنجليزية إلى العربية
SUBTYPE_TRANSLATIONS = {
    "missing_item": "فقدان غرض",
    "stolen_car": "سرقة سيارة",
    "theft": "سرقة",
    "complaint": "شكوى",
    "armed_robbery": "سطو مسلح",
    "found_item": "العثور على غرض",
    "missing_person": "شخص مفقود",
    "body": "جثة",
    "road_obstruction": "انسداد طريق",
    "violent_crime": "جريمة عنف",
    "verbal_abuse": "إساءة لفظية",
    "fight": "شجار",
    "blood_donation_req": "طلب تبرع بالدم",
    "gun_fight": "اشتباك مسلح",
    "missing_person_found": "العثور على الشخص المفقود",
    "explosion": "انفجار",
    "cardiac_arrest": "توقف قلب",
    "kidnapping": "خطف",
    "murder": "جريمة قتل",
    "charity": "حالة إنسانية",
    "gunwound": "إصابة بطلق ناري",
    "unconscious": "فاقد للوعي",
    "major_accident": "حادث كبير",
    "structure_fire": "حريق في مبنى",
    "vandalism": "تخريب",
    "wildfire": "حريق غابات",
    "warning": "تحذير",
    "fallen": "سقوط شخص",
    "rouge_faction": "عصابة خارجة عن القانون",
    "unknown_fire": "حريق مجهول السبب"
}

def severity_to_text(severity: float) -> str:
    if severity < 0.2:
        return "خطورة منخفضة جدًا"
    elif severity < 0.4:
        return "خطورة منخفضة"
    elif severity < 0.6:
        return "خطورة متوسطة"
    elif severity < 0.8:
        return "خطورة عالية"
    elif severity < 0.9:
        return "خطورة خطيرة جدًا"
    else:
        return "حالة طارئة قصوى"