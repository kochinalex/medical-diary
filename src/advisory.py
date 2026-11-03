# -*- coding: utf-8 -*-
from datetime import datetime, date
from typing import List, Dict, Any

def calculate_age(birth_date_str: str) -> int:
    try:
        born = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except Exception:
        return 30

def generate_health_advisory(records: List[Dict[str, Any]],
                             biomarkers: Dict[str, List[Dict[str, Any]]],
                             reminders: List[Dict[str, Any]],
                             profile: Dict[str, Any],
                             lang: str = "en") -> Dict[str, Any]:
    insights = []
    actions = []
    upcoming_alerts = []

    age = calculate_age(profile.get("birth_date", "1990-01-01"))
    is_child = age < 18 or profile.get("role", "").lower() == "child"

    # --- 1. PEDIATRIC ADVISORY RULES ---
    if is_child:
        if age <= 6:
            insights.append({
                "type": "info",
                "category": "Pediatric Growth & Vaccines" if lang == "en" else ("Педиатрия и вакцинация" if lang == "ru" else "Pedijatrijski razvoj i vakcine"),
                "title": f"Preschool Vaccine Check ({profile.get('name')}, {age} y.o.)" if lang == "en" else (f"Проверка вакцинации перед садом/школой ({profile.get('name')}, {age} лет)" if lang == "ru" else f"Vakcinacija pre polaska u vrtic/skolu ({profile.get('name')}, {age} god.)"),
                "message": "Preschool booster doses (MMR, DTaP, Polio) are due between ages 4-6." if lang == "en" else ("В возрасте 4-6 лет необходима ревакцинация: корь, паротит, краснуха (КПК) и дифтерия/столбняк/полиомиелит." if lang == "ru" else "U uzrastu 4-6 godina preporucuje se revakcinacija (MMR, DiTePer, polio)."),
                "advice": "Verify preschool immunization records with your pediatrician before kindergarten." if lang == "en" else ("Сверьте календарь прививок с педиатром перед началом учебного года." if lang == "ru" else "Proverite karton vakcinacije kod pedijatra pre upisa u vrtic ili skolu.")
            })

        # Pediatric Dental Checkup
        insights.append({
            "type": "info",
            "category": "Pediatric Dental" if lang == "en" else ("Детская стоматология" if lang == "ru" else "Decja stomatologija"),
            "title": "Bi-annual Pediatric Dental Visit" if lang == "en" else ("Плановый осмотр детского стоматолога" if lang == "ru" else "Kontrola decjeg stomatologa"),
            "message": "Routine examination and fluoride varnish protect developing primary and secondary teeth." if lang == "en" else ("Осмотр формы прикуса молочных зубов и фторирование эмали каждые 6 месяцев." if lang == "ru" else "Redovan pregled mlecnih zuba i zastita fluorom na svakih 6 meseci."),
            "advice": "Book dental appointment every 6 months." if lang == "en" else ("Посещайте детского стоматолога каждые 6 месяцев." if lang == "ru" else "Zakazite stomatoloski pregled svakih 6 meseci.")
        })

    # --- 2. ADULT ADVISORY RULES ---
    else:
        # Check Biomarker Trends for Adults
        for name, history in biomarkers.items():
            if not history:
                continue
            latest = history[-1]
            val = latest["value"]
            unit = latest["unit"]
            flag = latest.get("flag", "NORMAL")

            if name.lower() == "ferritin" and flag == "LOW":
                trend_msg = ""
                if len(history) > 1:
                    prev = history[-2]["value"]
                    diff = val - prev
                    if diff > 0:
                        trend_msg = f" (+{diff:.1f} {unit})"
                title_en = f"Low Iron Stores (Ferritin: {val} {unit}{trend_msg})"
                title_ru = f"Дефицит ферритина (уровень железа: {val} {unit}{trend_msg})"
                title_sr = f"Nizak nivo feritina (zalihe gvozda: {val} {unit}{trend_msg})"
                insights.append({
                    "type": "warning",
                    "category": "Lab Finding" if lang == "en" else ("Анализы крови" if lang == "ru" else "Laboratorijski nalaz"),
                    "title": title_en if lang == "en" else (title_ru if lang == "ru" else title_sr),
                    "message": f"Ferritin remains below reference range ({latest['ref_min']}-{latest['ref_max']} {unit})." if lang == "en" else (f"Уровень ферритина ниже нормы ({latest['ref_min']}-{latest['ref_max']} {unit})." if lang == "ru" else f"Feritin je ispod referentnog opsega ({latest['ref_min']}-{latest['ref_max']} {unit})."),
                    "advice": "Take oral iron with Vitamin C to enhance absorption. Avoid coffee, tea, and calcium within 2h. Retest in 8-12 weeks." if lang == "en" else ("Принимайте препараты железа с витамином C для лучшего усвоения. Исключите кофе, чай и кальций за 2 часа до и после. Повторный анализ через 2-3 месяца." if lang == "ru" else "Uzimajte gvozde sa vitaminom C radi bolje apsorpcije. Izbegavajte kafu, caj i mlecne proizvode 2 sata pre i posle. Ponovite analizu za 2-3 meseca.")
                })

            elif name.lower() == "vitamin d" and flag == "LOW":
                title_en = f"Suboptimal Vitamin D ({val} {unit})"
                title_ru = f"Сниженный витамин D ({val} {unit})"
                title_sr = f"Suboptimalan nivo vitamina D ({val} {unit})"
                insights.append({
                    "type": "info",
                    "category": "Lab Finding" if lang == "en" else ("Анализы крови" if lang == "ru" else "Laboratorijski nalaz"),
                    "title": title_en if lang == "en" else (title_ru if lang == "ru" else title_sr),
                    "message": f"Below optimal threshold (>30 {unit})." if lang == "en" else (f"Ниже оптимального уровня (>30 {unit})." if lang == "ru" else f"Ispod optimalnog nivoa (>30 {unit})."),
                    "advice": "Continue maintenance supplementation (2000-4000 IU daily with meal containing fats)." if lang == "en" else ("Продолжайте прием поддерживающей дозы (2000-4000 МЕ в день с жиросодержащей пищей)." if lang == "ru" else "Nastavite suplementaciju (2000-4000 IJ dnevno uz obrok sa zdravim mastima).")
                })

            elif name.lower() in ["total cholesterol", "ldl"] and flag == "HIGH":
                insights.append({
                    "type": "warning",
                    "category": "Cardiovascular" if lang == "en" else ("Кардиология" if lang == "ru" else "Kardiologija"),
                    "title": f"Elevated {name} ({val} {unit})" if lang == "en" else (f"Повышенный {name} ({val} {unit})" if lang == "ru" else f"Povisen {name} ({val} {unit})"),
                    "message": f"Above recommended baseline ({latest['ref_max']} {unit})." if lang == "en" else (f"Выше нормы ({latest['ref_max']} {unit})." if lang == "ru" else f"Iznad preporucene granice ({latest['ref_max']} {unit})."),
                    "advice": "Incorporate soluble fiber, reduce saturated fats, maintain 150 min/wk moderate cardio." if lang == "en" else ("Увеличьте потребление растворимой клетчатки, сократите насыщенные жиры, поддерживайте 150 мин аэробных нагрузок в неделю." if lang == "ru" else "Povecajte unos rastvorljivih vlakana, smanjite zasicene masti, bavite se umerenom aerobnom aktivnoscu.")
                })

        # Adult Skin & Dental check reminders
        mole_rem = next((r for r in reminders if "mole" in r["title"].lower() or "derma" in r["title"].lower()), None)
        if mole_rem and not mole_rem.get("completed", 0):
            insights.append({
                "type": "info",
                "category": "Preventive Screening" if lang == "en" else ("Онкоскрининг" if lang == "ru" else "Preventivni pregled"),
                "title": "Annual Full-Body Skin Examination" if lang == "en" else ("Ежегодный осмотр родинок (дерматоскопия)" if lang == "ru" else "Godisnji dermoskopski pregled mladeza"),
                "message": "Routine surveillance is recommended following past dysplastic mole removal." if lang == "en" else ("Регулярное наблюдение за кожей после удаления диспластических невусов." if lang == "ru" else "Preporucuje se redovna kontrola koze nakon ranijeg uklanjanja mladeza."),
                "advice": "Use ABCDE rules for self-examination and schedule full-body dermoscopy." if lang == "en" else ("Следите за родинками по правилу ABCDE и запланируйте дерматоскопию." if lang == "ru" else "Pratite ABCDE pravilo za samopregled i zakazite dermoskopiju.")
            })

    # --- 3. COMMON CALENDAR ALERTS ---
    today = date.today()
    for rem in reminders:
        if rem.get("completed", 0) == 1:
            continue
        try:
            due_dt = datetime.strptime(rem["due_date"], "%Y-%m-%d").date()
            diff_days = (due_dt - today).days
            if diff_days < 0:
                days_label = f"Overdue by {abs(diff_days)} days" if lang == "en" else (f"Просрочено на {abs(diff_days)} дн." if lang == "ru" else f"Isteklo pre {abs(diff_days)} dana")
                upcoming_alerts.append({
                    "status": "overdue",
                    "title": rem["title"],
                    "due_date": rem["due_date"],
                    "notes": rem.get("notes", ""),
                    "days_label": days_label
                })
            elif diff_days <= 45:
                days_label = f"Due in {diff_days} days" if lang == "en" else (f"Через {diff_days} дн." if lang == "ru" else f"Rok za {diff_days} dana")
                upcoming_alerts.append({
                    "status": "upcoming",
                    "title": rem["title"],
                    "due_date": rem["due_date"],
                    "notes": rem.get("notes", ""),
                    "days_label": days_label
                })
        except Exception:
            pass

    doctor_brief = generate_doctor_brief(records, biomarkers, profile, lang=lang)

    return {
        "insights": insights,
        "actions": actions,
        "alerts": upcoming_alerts,
        "doctor_brief": doctor_brief
    }

def generate_doctor_brief(records: List[Dict[str, Any]],
                          biomarkers: Dict[str, List[Dict[str, Any]]],
                          profile: Dict[str, Any],
                          lang: str = "en") -> str:
    lines = []
    if lang == "ru":
        lines.append(f"МЕДИЦИНСКАЯ ВЫПИСКА ДЛЯ ВРАЧА: {profile.get('name', 'Пациент')}")
        lines.append(f"Дата рожд.: {profile.get('birth_date', 'Н/Д')} | Роль: {profile.get('role', 'Член семьи')} | Группа крови: {profile.get('blood_type', 'Н/Д')}")
        lines.append(f"Аллергии: {profile.get('allergies', 'Не выявлено')}")
        lines.append(f"Хронические диагнозы: {profile.get('chronic_conditions', 'Нет')}")
        lines.append(f"Принимаемые препараты: {profile.get('current_medications', 'Нет')}")
        lines.append("-" * 40)
        lines.append("ПОСЛЕДНИЕ ПОКАЗАТЕЛИ АНАЛИЗОВ:")
        for b_name, history in biomarkers.items():
            if history:
                latest = history[-1]
                flag_str = f" ({latest['flag']})" if latest.get('flag') and latest['flag'] != 'NORMAL' else ""
                lines.append(f"  * {b_name}: {latest['value']} {latest['unit']}{flag_str} от {latest['test_date']}")
        lines.append("-" * 40)
        lines.append("ПОСЛЕДНИЕ СОБЫТИЯ И ОБРАЩЕНИЯ:")
        for ev in records[:4]:
            lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev.get('provider') or 'Пациент'}): {ev.get('notes', '')[:70]}...")
    elif lang == "sr":
        lines.append(f"LEKARSKI SAZETAK: {profile.get('name', 'Pacijent')}")
        lines.append(f"Datum rodenja: {profile.get('birth_date', 'N/A')} | Uloga: {profile.get('role', 'Clan porodice')} | Krvna grupa: {profile.get('blood_type', 'N/A')}")
        lines.append(f"Poznate alergije: {profile.get('allergies', 'Nema zabelezenih')}")
        lines.append(f"Hronicne dijagnoze: {profile.get('chronic_conditions', 'Nema')}")
        lines.append(f"Redovna terapija: {profile.get('current_medications', 'Nema')}")
        lines.append("-" * 40)
        lines.append("POSLEDNJI NALAZI:")
        for b_name, history in biomarkers.items():
            if history:
                latest = history[-1]
                flag_str = f" ({latest['flag']})" if latest.get('flag') and latest['flag'] != 'NORMAL' else ""
                lines.append(f"  * {b_name}: {latest['value']} {latest['unit']}{flag_str} - {latest['test_date']}")
        lines.append("-" * 40)
        lines.append("PRETHODNI PREGLEDI I DOGADAJI:")
        for ev in records[:4]:
            lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev.get('provider') or 'Licni unos'}): {ev.get('notes', '')[:70]}...")
    else:
        lines.append(f"PATIENT BRIEF: {profile.get('name', 'Patient')}")
        lines.append(f"DOB: {profile.get('birth_date', 'N/A')} | Role: {profile.get('role', 'Family Member')} | Blood Group: {profile.get('blood_type', 'N/A')}")
        lines.append(f"Known Allergies: {profile.get('allergies', 'None reported')}")
        lines.append(f"Active Conditions: {profile.get('chronic_conditions', 'None')}")
        lines.append(f"Current Regimen / Meds: {profile.get('current_medications', 'None')}")
        lines.append("-" * 40)
        lines.append("KEY RECENT LABS:")
        for b_name, history in biomarkers.items():
            if history:
                latest = history[-1]
                flag_str = f" ({latest['flag']})" if latest.get('flag') and latest['flag'] != 'NORMAL' else ""
                lines.append(f"  * {b_name}: {latest['value']} {latest['unit']}{flag_str} on {latest['test_date']}")
        lines.append("-" * 40)
        lines.append("RECENT CLINICAL EVENTS (Past 12 Months):")
        for ev in records[:4]:
            lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev.get('provider') or 'Self'}): {ev.get('notes', '')[:70]}...")

    return "\n".join(lines)
