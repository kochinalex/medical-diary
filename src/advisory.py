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
                "category": "Pediatric Growth & Vaccines" if lang == "en" else ("Вакцинация и развитие" if lang == "ru" else "Pedijatrijski razvoj i vakcine"),
                "title": f"Preschool Vaccine Check ({profile.get('name')}, {age} y.o.)" if lang == "en" else (f"Плановые прививки перед школой ({profile.get('name')}, {age} лет)" if lang == "ru" else f"Vakcinacija pre polaska u vrtić/školu ({profile.get('name')}, {age} god.)"),
                "message": "Preschool booster doses (MMR, DTaP, Polio) are due between ages 4-6." if lang == "en" else ("В возрасте 4-6 лет проводится ревакцинация против кори, паротита, краснухи (КПК) и дифтерии/столбняка." if lang == "ru" else "U uzrastu 4-6 godina preporučuje se revakcinacija (MMR, DiTePer, polio)."),
                "advice": "Verify preschool immunization records with your pediatrician before kindergarten." if lang == "en" else ("Сверьте календарь прививок с педиатром перед началом учебного года." if lang == "ru" else "Proverite karton vakcinacije kod pedijatra pre upisa u vrtić ili školu.")
            })

        # Pediatric Dental Checkup
        insights.append({
            "type": "info",
            "category": "Pediatric Dental" if lang == "en" else ("Детская стоматология" if lang == "ru" else "Dečja stomatologija"),
            "title": "Bi-annual Pediatric Dental Visit" if lang == "en" else ("Профосмотр у детского стоматолога" if lang == "ru" else "Kontrola dečjeg stomatologa"),
            "message": "Routine examination and fluoride varnish protect developing primary and secondary teeth." if lang == "en" else ("Осмотр эмали молочных зубов и покрытие фторлаком каждые 6 месяцев." if lang == "ru" else "Redovan pregled mlečnih zuba i zaštita fluorom na svakih 6 meseci."),
            "advice": "Book dental appointment every 6 months." if lang == "en" else ("Посещайте детского стоматолога дважды в год." if lang == "ru" else "Zakažite stomatološki pregled svakih 6 meseci.")
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
                title_ru = f"Дефицит ферритина (уровень: {val} {unit}{trend_msg})"
                title_sr = f"Nizak nivo feritina (zalihe gvožđa: {val} {unit}{trend_msg})"
                insights.append({
                    "type": "warning",
                    "category": "Lab Finding" if lang == "en" else ("Анализ крови" if lang == "ru" else "Laboratorijski nalaz"),
                    "title": title_en if lang == "en" else (title_ru if lang == "ru" else title_sr),
                    "message": f"Ferritin remains below reference range ({latest['ref_min']}-{latest['ref_max']} {unit})." if lang == "en" else (f"Уровень ферритина ниже нормы ({latest['ref_min']}-{latest['ref_max']} {unit})." if lang == "ru" else f"Feritin je ispod referentnog opsega ({latest['ref_min']}-{latest['ref_max']} {unit})."),
                    "advice": "Take oral iron with Vitamin C to enhance absorption. Avoid coffee, tea, and calcium within 2h. Retest in 8-12 weeks." if lang == "en" else ("Принимайте препараты железа с витамином C. Избегайте кофе, чая и молочных продуктов за 2 часа до/после приема. Повторите анализ через 2-3 месяца." if lang == "ru" else "Uzimajte gvožđe sa vitaminom C radi bolje apsorpcije. Izbegavajte kafu, čaj i mlečne proizvode 2 sata pre i posle. Ponovite analizu za 2-3 meseca.")
                })

            elif name.lower() == "vitamin d" and flag == "LOW":
                title_en = f"Suboptimal Vitamin D ({val} {unit})"
                title_ru = f"Сниженный витамин D ({val} {unit})"
                title_sr = f"Suboptimalan nivo vitamina D ({val} {unit})"
                insights.append({
                    "type": "info",
                    "category": "Lab Finding" if lang == "en" else ("Анализ крови" if lang == "ru" else "Laboratorijski nalaz"),
                    "title": title_en if lang == "en" else (title_ru if lang == "ru" else title_sr),
                    "message": f"Below optimal threshold (>30 {unit})." if lang == "en" else (f"Ниже оптимальной нормы (>30 {unit})." if lang == "ru" else f"Ispod optimalnog nivoa (>30 {unit})."),
                    "advice": "Continue maintenance supplementation (2000-4000 IU daily with meal containing fats)." if lang == "en" else ("Рекомендуется прием поддерживающей дозы (2000-4000 МЕ с жиросодержащей пищей)." if lang == "ru" else "Nastavite suplementaciju (2000-4000 IJ dnevno uz obrok sa zdravim mastima).")
                })

            elif name.lower() in ["total cholesterol", "ldl"] and flag == "HIGH":
                insights.append({
                    "type": "warning",
                    "category": "Cardiovascular" if lang == "en" else ("Кардиология" if lang == "ru" else "Kardiologija"),
                    "title": f"Elevated {name} ({val} {unit})" if lang == "en" else (f"Повышенный {name} ({val} {unit})" if lang == "ru" else f"Povišen {name} ({val} {unit})"),
                    "message": f"Above recommended baseline ({latest['ref_max']} {unit})." if lang == "en" else (f"Выше нормы ({latest['ref_max']} {unit})." if lang == "ru" else f"Iznad preporučene granice ({latest['ref_max']} {unit})."),
                    "advice": "Incorporate soluble fiber, reduce saturated fats, maintain 150 min/wk moderate cardio." if lang == "en" else ("Увеличьте потребление клетчатки, ограничьте трансжиры, поддерживайте кардионагрузки." if lang == "ru" else "Povećajte unos rastvorljivih vlakana, smanjite zasićene masti, bavite se umerenom aerobnom aktivnošću.")
                })

        # Adult Skin & Dental check reminders
        mole_rem = next((r for r in reminders if "mole" in r["title"].lower() or "derma" in r["title"].lower()), None)
        if mole_rem and not mole_rem.get("completed", 0):
            insights.append({
                "type": "info",
                "category": "Preventive Screening" if lang == "en" else ("Профосмотр" if lang == "ru" else "Preventivni pregled"),
                "title": "Annual Full-Body Skin Examination" if lang == "en" else ("Ежегодный осмотр родинок (дерматоскопия)" if lang == "ru" else "Godišnji dermoskopski pregled mladeža"),
                "message": "Routine surveillance is recommended following past dysplastic mole removal." if lang == "en" else ("Регулярное наблюдение за родинками после удаления диспластического невуса." if lang == "ru" else "Preporučuje se redovna kontrola kože nakon ranijeg uklanjanja mladeža."),
                "advice": "Use ABCDE rules for self-examination and schedule full-body dermoscopy." if lang == "en" else ("Следите за изменениями по шкале ABCDE и посетите дерматолога." if lang == "ru" else "Pratite ABCDE pravilo za samopregled i zakažite dermoskopiju.")
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
        lines.append(f"МЕДИЦИНСКАЯ ВЫПИСКА: {profile.get('name', 'Пациент')}")
        lines.append(f"Дата рожд: {profile.get('birth_date', 'Н/Д')} | Роль: {profile.get('role', 'Член семьи')} | Группа крови: {profile.get('blood_type', 'Н/Д')}")
        lines.append(f"Аллергии: {profile.get('allergies', 'Не выявлено')}")
        lines.append(f"Хронические диагнозы: {profile.get('chronic_conditions', 'Нет')}")
        lines.append(f"Текущая терапия: {profile.get('current_medications', 'Нет')}")
        lines.append("-" * 40)
        lines.append("ПОСЛЕДНИЕ АНАЛИЗЫ:")
        for b_name, history in biomarkers.items():
            if history:
                latest = history[-1]
                lines.append(f"  * {b_name}: {latest['value']} {latest['unit']} ({latest['flag']}) от {latest['test_date']}")
        lines.append("-" * 40)
        lines.append("СОБЫТИЯ ЗА ПОСЛЕДНИЙ ГОД:")
        for ev in records[:4]:
            lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev.get('provider') or 'Самоотчет'}): {ev.get('notes', '')[:70]}...")
    elif lang == "sr":
        lines.append(f"LEKARSKI SAŽETAK: {profile.get('name', 'Pacijent')}")
        lines.append(f"Datum rođenja: {profile.get('birth_date', 'N/A')} | Uloga: {profile.get('role', 'Član porodice')} | Krvna grupa: {profile.get('blood_type', 'N/A')}")
        lines.append(f"Poznate alergije: {profile.get('allergies', 'Nema zabeleženih')}")
        lines.append(f"Hronične dijagnoze: {profile.get('chronic_conditions', 'Nema')}")
        lines.append(f"Redovna terapija: {profile.get('current_medications', 'Nema')}")
        lines.append("-" * 40)
        lines.append("POSLEDNJI NALAZI:")
        for b_name, history in biomarkers.items():
            if history:
                latest = history[-1]
                lines.append(f"  * {b_name}: {latest['value']} {latest['unit']} ({latest['flag']}) - {latest['test_date']}")
        lines.append("-" * 40)
        lines.append("PRETHODNI PREGLEDI I DOGAĐAJI:")
        for ev in records[:4]:
            lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev.get('provider') or 'Lični unos'}): {ev.get('notes', '')[:70]}...")
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
                lines.append(f"  * {b_name}: {latest['value']} {latest['unit']} ({latest['flag']}) on {latest['test_date']}")
        lines.append("-" * 40)
        lines.append("RECENT CLINICAL EVENTS (Past 12 Months):")
        for ev in records[:4]:
            lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev.get('provider') or 'Self'}): {ev.get('notes', '')[:70]}...")

    return "\n".join(lines)
