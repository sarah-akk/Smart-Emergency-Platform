# ========================= التصنيفات المعتمدة ==========================
CLASSES = [
    "CIVIL", "POLICE", "MEDICAL", "TRAFFIC", "FIRE"
]

SUBCLASSES = [
    "missing_item", "stolen_car", "theft", "complaint", "armed_robbery",
    "found_item", "missing_person", "body", "road_obstruction", "violent_crime",
    "verbal_abuse", "fight", "blood_donation_req", "gun_fight", "missing_person_found",
    "explosion", "cardiac_arrest", "kidnapping", "murder", "charity",
    "gunwound", "unconscious", "major_accident", "structure_fire", "vandalism",
    "wildfire", "warning", "fallen", "rouge_faction", "unknown_fire"
]

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