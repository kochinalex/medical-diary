import json
from typing import Dict, Any, List

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title": "Medical Diary",
        "app_subtitle": "Family Health Record & Proactive Advisor",
        "all_family": "All Family",
        "add_member": "Add Member",
        "edit_profile": "Edit Profile",
        "delete_profile": "Delete Profile",
        "timeline_tab": "Timeline",
        "biomarkers_tab": "Labs & Vitals",
        "calendar_tab": "Calendar",
        "advisory_tab": "Advice",
        "ice_btn": "ICE Card",
        "filter_all": "All",
        "filter_visit": "Visits",
        "filter_test_result": "Labs",
        "filter_sickness": "Sickness",
        "filter_intervention": "Surgeries",
        "filter_comment": "Notes",
        "cat_visit": "Doctor Visit",
        "cat_test_result": "Lab Results",
        "cat_sickness": "Sickness Episode",
        "cat_intervention": "Procedure / Surgery",
        "cat_comment": "Observation / Note",
        "attached_doc": "Attached Document",
        "biomarker_trends": "Biomarker Trends",
        "biomarker_desc": "Track blood panels, hormones, and vitals over time.",
        "select_biomarker": "Select Biomarker:",
        "latest_values": "Latest Recorded Values",
        "health_calendar": "Health Calendar",
        "calendar_desc": "Scheduled screenings, vaccinations & retests",
        "new_reminder": "New Reminder",
        "overdue_badge": "Overdue",
        "due_in": "Due in",
        "clinical_insights": "Clinical Insights & Advice",
        "clinical_desc": "Proactive health guidance based on evidence guidelines",
        "recommendation": "Recommendation",
        "doctor_brief": "Pre-Visit Doctor Brief",
        "doctor_brief_desc": "Concise 1-page clinical summary ready to hand to your doctor.",
        "copy_btn": "Copy",
        "copied_alert": "Pre-visit brief copied to clipboard!",
        "add_record_title": "Add Health Record",
        "record_category": "Record Category",
        "date_label": "Date",
        "doctor_provider": "Doctor / Provider",
        "title_label": "Title",
        "clinic_facility": "Clinic / Facility",
        "notes_findings": "Notes & Findings",
        "optional_lab": "Optional: Add Lab Biomarker",
        "test_name": "Test Name (e.g. Ferritin)",
        "test_value": "Value",
        "test_unit": "Unit",
        "attach_doc": "Attach Document or Photo (PDF / JPG / PNG)",
        "cancel_btn": "Cancel",
        "save_btn": "Save Record",
        "emergency_card_title": "EMERGENCY HEALTH CARD",
        "blood_group": "Blood Group",
        "patient_name_dob": "Patient Name & DOB",
        "critical_allergies": "Critical Allergies",
        "chronic_conditions": "Chronic Conditions",
        "current_medications": "Current Medications",
        "emergency_contact": "Emergency Contact",
        "print_card": "Print / Save Card",
        "role_label": "Relationship / Role",
        "gender_label": "Gender",
        "member_name": "Member Name",
        "pediatric_mode": "Pediatric Health Profile",
        "adult_mode": "Adult Health Profile",
        "flag_low": "LOW",
        "flag_high": "HIGH",
        "flag_normal": "NORMAL",
        "search_placeholder": "Search events, diagnoses, doctors, notes...",
        "sort_newest": "Newest",
        "sort_oldest": "Oldest",
        "edit_profile_btn": "Edit Profile",
        "edit_profile_title": "Edit Personal Health Profile",
        "save_changes": "Save Changes",
        "no_records_found": "No records found matching your search.",
        "delete_record_btn": "Delete Record",
        "delete_record_confirm": "Are you sure you want to delete this health record?",
        "delete_reminder_btn": "Delete Reminder",
        "delete_reminder_confirm": "Are you sure you want to delete this reminder?",
        "clear_sample_btn": "Clear Sample Data",
        "clear_sample_confirm": "This will remove pre-loaded sample records so you can start with a clean health diary. Continue?",
        "login_title": "Sign In to Medical Diary",
        "register_title": "Create Your Private Health Vault",
        "email_label": "Email Address",
        "password_label": "Password",
        "full_name_label": "Your Name",
        "login_btn": "Sign In",
        "register_btn": "Create Account",
        "no_account": "Don't have an account? Create one",
        "have_account": "Already have an account? Sign in",
        "logout_btn": "Log Out",
        "invalid_credentials": "Invalid email or password. Please try again.",
        "email_exists": "An account with this email already exists.",
        "import_data_btn": "Import Backup Data",
        "import_data_title": "Import Previous Medical History",
        "import_data_desc": "Upload a JSON backup file from a previous diary export or prior version.",
        "import_btn": "Import Now",
        "import_success": "Medical records imported successfully!",
        "select_file_prompt": "Select a .json file to import",
        "export_data_btn": "Export Backup (JSON)"
    },
    "ru": {
        "app_title": "Медицинский Дневник",
        "app_subtitle": "Семейная медкнижка и умные рекомендации",
        "all_family": "Вся семья",
        "add_member": "Добавить члена семьи",
        "edit_profile": "Редактировать",
        "delete_profile": "Удалить профиль",
        "timeline_tab": "Хроника",
        "biomarkers_tab": "Анализы",
        "calendar_tab": "Календарь",
        "advisory_tab": "Советы",
        "ice_btn": "SOS Карта",
        "filter_all": "Все",
        "filter_visit": "Приемы",
        "filter_test_result": "Анализы",
        "filter_sickness": "Болезни",
        "filter_intervention": "Операции",
        "filter_comment": "Заметки",
        "cat_visit": "Прием врача",
        "cat_test_result": "Результаты анализов",
        "cat_sickness": "Заболевание / Симптомы",
        "cat_intervention": "Процедура / Операция",
        "cat_comment": "Заметка / Наблюдение",
        "attached_doc": "Прикрепленный документ",
        "biomarker_trends": "Динамика показателей",
        "biomarker_desc": "Отслеживайте показатели крови, гормоны и жизненные маркеры.",
        "select_biomarker": "Выберите показатель:",
        "latest_values": "Последние результаты",
        "health_calendar": "Календарь здоровья",
        "calendar_desc": "Плановые чекапы, вакцинация и повторные анализы",
        "new_reminder": "Новое напоминание",
        "overdue_badge": "Просрочено",
        "due_in": "Срок через",
        "clinical_insights": "Клинические рекомендации",
        "clinical_desc": "Персональные советы на основе доказательной медицины",
        "recommendation": "Рекомендация",
        "doctor_brief": "Справка для врача",
        "doctor_brief_desc": "Краткая выжимка (анамнез, аллергии, анализы) для приема у доктора.",
        "copy_btn": "Копировать",
        "copied_alert": "Справка для врача скопирована в буфер обмена!",
        "add_record_title": "Добавить запись о здоровье",
        "record_category": "Категория записи",
        "date_label": "Дата",
        "doctor_provider": "Врач / Специалист",
        "title_label": "Название / Диагноз",
        "clinic_facility": "Клиника / Лаборатория",
        "notes_findings": "Жалобы, назначения и выводы",
        "optional_lab": "Добавить показатель анализа",
        "test_name": "Название теста (напр. Ферритин)",
        "test_value": "Значение",
        "test_unit": "Ед. изм.",
        "attach_doc": "Прикрепить фото или PDF (выписка, результат)",
        "cancel_btn": "Отмена",
        "save_btn": "Сохранить запись",
        "emergency_card_title": "ЭКСТРЕННАЯ МЕДИЦИНСКАЯ КАРТА",
        "blood_group": "Группа крови",
        "patient_name_dob": "ФИО и дата рождения",
        "critical_allergies": "Опасные аллергии",
        "chronic_conditions": "Хронические диагнозы",
        "current_medications": "Принимаемые препараты",
        "emergency_contact": "Экстренный контакт",
        "print_card": "Печать / Экспорт карты",
        "role_label": "Роль в семье",
        "gender_label": "Пол",
        "member_name": "Имя члена семьи",
        "pediatric_mode": "Детский профиль (педиатрия)",
        "adult_mode": "Взрослый профиль",
        "flag_low": "НИЗКИЙ",
        "flag_high": "ВЫСОКИЙ",
        "flag_normal": "НОРМА",
        "search_placeholder": "Поиск по диагнозам, врачам, заметкам...",
        "sort_newest": "Сначала новые",
        "sort_oldest": "Сначала старые",
        "edit_profile_btn": "Редактировать профиль",
        "edit_profile_title": "Редактирование медицинской карты",
        "save_changes": "Сохранить изменения",
        "no_records_found": "Записи по вашему запросу не найдены.",
        "delete_record_btn": "Удалить запись",
        "delete_record_confirm": "Вы уверены, что хотите удалить эту медицинскую запись?",
        "delete_reminder_btn": "Удалить напоминание",
        "delete_reminder_confirm": "Вы уверены, что хотите удалить это напоминание?",
        "clear_sample_btn": "Очистить демо-данные",
        "clear_sample_confirm": "Это удалит демонстрационные записи, чтобы начать вести дневник с чистого листа. Продолжить?",
        "login_title": "Вход в Медицинский Дневник",
        "register_title": "Создать личную медкнижку",
        "email_label": "Электронная почта",
        "password_label": "Пароль",
        "full_name_label": "Ваше имя",
        "login_btn": "Войти",
        "register_btn": "Зарегистрироваться",
        "no_account": "Нет аккаунта? Создать",
        "have_account": "Уже есть аккаунт? Войти",
        "logout_btn": "Выйти",
        "invalid_credentials": "Неверный email или пароль. Попробуйте еще раз.",
        "email_exists": "Пользователь с таким email уже зарегистрирован.",
        "import_data_btn": "Импорт архива данных",
        "import_data_title": "Импорт предыдущих медицинских записей",
        "import_data_desc": "Загрузите файл резервной копии (JSON) из предыдущей версии или экспорта.",
        "import_btn": "Импортировать",
        "import_success": "Медицинские данные успешно импортированы!",
        "select_file_prompt": "Выберите файл .json для импорта",
        "export_data_btn": "Экспорт архива (JSON)"
    },
    "sr": {
        "app_title": "Medicinski Dnevnik",
        "app_subtitle": "Porodični zdravstveni karton i pametni saveti",
        "all_family": "Cela porodica",
        "add_member": "Dodaj člana",
        "edit_profile": "Izmeni profil",
        "delete_profile": "Obriši profil",
        "timeline_tab": "Hronika",
        "biomarkers_tab": "Nalazi",
        "calendar_tab": "Kalendar",
        "advisory_tab": "Saveti",
        "ice_btn": "Hitna kartica",
        "filter_all": "Sve",
        "filter_visit": "Pregledi",
        "filter_test_result": "Laboratorija",
        "filter_sickness": "Bolesti",
        "filter_intervention": "Operacije",
        "filter_comment": "Beleške",
        "cat_visit": "Pregled lekara",
        "cat_test_result": "Laboratorijski nalaz",
        "cat_sickness": "Bolest / Simptomi",
        "cat_intervention": "Intervencija / Operacija",
        "cat_comment": "Beleška / Zapažanje",
        "attached_doc": "Priložen dokument",
        "biomarker_trends": "Trendovi laboratorijskih parametara",
        "biomarker_desc": "Pratite krvnu sliku, hormone i vitalne parametre kroz vreme.",
        "select_biomarker": "Izaberite parametar:",
        "latest_values": "Poslednje zabeležene vrednosti",
        "health_calendar": "Zdravstveni kalendar",
        "calendar_desc": "Zakazani kontrolni pregledi, vakcine i ponovne analize",
        "new_reminder": "Novi podsetnik",
        "overdue_badge": "Isteklo",
        "due_in": "Rok za",
        "clinical_insights": "Klinički uvid i saveti",
        "clinical_desc": "Proaktivni zdravstveni saveti zasnovani na medicinskim smernicama",
        "recommendation": "Preporuka",
        "doctor_brief": "Izveštaj za lekara",
        "doctor_brief_desc": "Kratak sažetak (istorija, terapija, alergije) za vašeg lekara.",
        "copy_btn": "Kopiraj",
        "copied_alert": "Izveštaj za lekara je kopiran!",
        "add_record_title": "Dodaj zdravstveni zapis",
        "record_category": "Kategorija zapisa",
        "date_label": "Datum",
        "doctor_provider": "Lekar / Specijalista",
        "title_label": "Naziv / Dijagnoza",
        "clinic_facility": "Klinika / Ustanova",
        "notes_findings": "Nalaz, terapija i zapažanja",
        "optional_lab": "Opciono: Dodaj laboratorijski parametar",
        "test_name": "Naziv analize (npr. Feritin)",
        "test_value": "Vrednost",
        "test_unit": "Jedinica",
        "attach_doc": "Priloži dokument ili sliku (PDF / JPG / PNG)",
        "cancel_btn": "Otkaži",
        "save_btn": "Sačuvaj zapis",
        "emergency_card_title": "HITNA MEDICINSKA KARTICA",
        "blood_group": "Krvna grupa",
        "patient_name_dob": "Ime pacijenta i datum rođenja",
        "critical_allergies": "Alergije na lekove i hranu",
        "chronic_conditions": "Hronične bolesti",
        "current_medications": "Redovna terapija i lekovi",
        "emergency_contact": "Kontakt za hitne slučajeve",
        "print_card": "Štampaj / Sačuvaj karticu",
        "role_label": "Uloga u porodici",
        "gender_label": "Pol",
        "member_name": "Ime člana porodice",
        "pediatric_mode": "Pedijatrijski profil (deca)",
        "adult_mode": "Profil za odrasle",
        "flag_low": "NISKO",
        "flag_high": "VISOKO",
        "flag_normal": "NORMALNO",
        "search_placeholder": "Pretraga po dijagnozama, lekarima, beleškama...",
        "sort_newest": "Prvo najnovije",
        "sort_oldest": "Prvo najstarije",
        "edit_profile_btn": "Izmeni profil",
        "edit_profile_title": "Izmena zdravstvenog kartona",
        "save_changes": "Sačuvaj izmene",
        "no_records_found": "Nema pronađenih zapisa za uneti upit.",
        "delete_record_btn": "Obriši zapis",
        "delete_record_confirm": "Da li ste sigurni da želite da obrišete ovaj zdravstveni zapis?",
        "delete_reminder_btn": "Obriši podsetnik",
        "delete_reminder_confirm": "Da li ste sigurni da želite da obrišete ovaj podsetnik?",
        "clear_sample_btn": "Obriši probne podatke",
        "clear_sample_confirm": "Ovo će ukloniti sve probne zapise kako biste započeli sa čistim kartonom. Nastaviti?",
        "login_title": "Prijava u Medicinski Dnevnik",
        "register_title": "Kreirajte vaš zdravstveni karton",
        "email_label": "Email adresa",
        "password_label": "Lozinka",
        "full_name_label": "Vaše ime",
        "login_btn": "Prijavi se",
        "register_btn": "Registruj se",
        "no_account": "Nemate nalog? Kreirajte ga",
        "have_account": "Već imate nalog? Prijavite se",
        "logout_btn": "Odjavi se",
        "invalid_credentials": "Pogrešan email ili lozinka. Pokušajte ponovo.",
        "email_exists": "Nalog sa ovom email adresom već postoji.",
        "import_data_btn": "Uvezi rezervne podatke",
        "import_data_title": "Uvoz prethodnih zdravstvenih zapisa",
        "import_data_desc": "Otpremite JSON datoteku iz prethodnog izvoza ili prethodne verzije dnevnika.",
        "import_btn": "Uvezi podatke",
        "import_success": "Zdravstveni zapisi su uspešno uvezeni!",
        "select_file_prompt": "Izaberite .json datoteku za uvoz",
        "export_data_btn": "Izvoz rezervne kopije (JSON)"
    }
}

# Standard Biomarker Translations (Universal Clinical Dictionary)
BIOMARKER_NAMES: Dict[str, Dict[str, str]] = {
    "Ferritin": {"en": "Ferritin", "ru": "Ферритин", "sr": "Feritin"},
    "Vitamin D": {"en": "Vitamin D (25-OH)", "ru": "Витамин D (25-OH)", "sr": "Vitamin D (25-OH)"},
    "Total Cholesterol": {"en": "Total Cholesterol", "ru": "Общий холестерин", "sr": "Ukupni holesterol"},
    "LDL": {"en": "LDL Cholesterol", "ru": "ЛПНП (плохой холестерин)", "sr": "LDL holesterol"},
    "HDL": {"en": "HDL Cholesterol", "ru": "ЛПВП (хороший холестерин)", "sr": "HDL holesterol"},
    "Fasting Glucose": {"en": "Fasting Glucose", "ru": "Глюкоза (натощак)", "sr": "Glukoza (natašte)"},
    "HbA1c": {"en": "HbA1c (Glycated Hemoglobin)", "ru": "Гликированный гемоглобин", "sr": "Glikozilirani hemoglobin"},
    "Hemoglobin": {"en": "Hemoglobin", "ru": "Гемоглобин", "sr": "Hemoglobin"},
    "TSH": {"en": "TSH (Thyroid Stimulating Hormone)", "ru": "ТТГ (тиреотропный гормон)", "sr": "TSH (tiroidni hormon)"}
}

# Standard Sample Content Localization Mapping
CONTENT_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Titles
    "Comprehensive Metabolic & Iron Panel (Spring)": {
        "ru": "Биохимический анализ крови и обмен железа (весна)",
        "sr": "Biohemijski nalaz krvi i panel gvožđa (proleće)"
    },
    "Follow-up Iron & Vitamin Panel (Autumn)": {
        "ru": "Контрольный анализ: железо и витамины (осень)",
        "sr": "Kontrolni nalaz: gvožđe i vitamini (jesen)"
    },
    "Cardiology & Blood Pressure Review": {
        "ru": "Консультация кардиолога и мониторинг давления",
        "sr": "Kardiološki pregled i kontrola pritiska"
    },
    "Acute Viral Rhinosinusitis": {
        "ru": "Острый вирусный риносинусит",
        "sr": "Akutni virusni rinosinuzitis"
    },
    "Preventive Dermatological Mole Excision": {
        "ru": "Профилактическое удаление родинки (невуса)",
        "sr": "Preventivno uklanjanje mladeža (nevusa)"
    },
    "Allergy Season Note & Inhaler Refill": {
        "ru": "Сезонная аллергия и рецепт на ингалятор",
        "sr": "Sezonska alergija i inhalator"
    },
    "4-Year Well-Child Pediatric Exam": {
        "ru": "Плановый осмотр педиатра в 4 года",
        "sr": "Sistematski pregled pedijatra u 4. godini"
    },
    "Viral Gastroenteritis Episode": {
        "ru": "Эпизод вирусного гастроэнтерита (ротавирус)",
        "sr": "Epizoda virusnog gastroenteritisa"
    },

    # Notes
    "Routine annual blood work. Mild microcytic anemia indications noted.": {
        "ru": "Плановый ежегодный чекап. Признаки умеренной микроцитарной анемии.",
        "sr": "Rutinski godišnji pregled krvi. Uočeni blagi znaci mikrocitne anemije."
    },
    "Ferritin has started to rise with supplementation but remains below optimal threshold.": {
        "ru": "Уровень ферритина начал расти на фоне приема добавок, но остается ниже оптимальной нормы.",
        "sr": "Nivo feritina počeo je da raste uz suplementaciju, ali je i dalje ispod optimalne granice."
    },
    "Patient reports mild occasional palpitations under work stress. ECG normal. Resting BP 118/76 mmHg. Recommended hydration and magnesium.": {
        "ru": "Жалобы на редкое ощущение учащенного сердцебиения при стрессе на работе. ЭКГ в норме. Давление в покое 118/76 мм рт. ст. Рекомендован питьевой режим и магний.",
        "sr": "Povremene blage palpitacije pri stresu na poslu. EKG uredan. Pritisak u mirovanju 118/76 mmHg. Preporučena hidratacija i magnezijum."
    },
    "Fever up to 38.4C, sinus congestion, headache. Prescribed nasal saline rinse, ibuprofen as needed. Fully resolved in 6 days.": {
        "ru": "Температура до 38.4°C, заложенность пазух носа, головная боль. Назначены промывания солевым раствором, ибупрофен. Полное выздоровление за 6 дней.",
        "sr": "Temperatura do 38.4°C, zapušenost sinusa, glavobolja. Prepisano ispiranje fiziološkim rastvorom, ibuprofen po potrebi. Oporavak za 6 dana."
    },
    "Atypical dysplastic nevus removed from upper back margin. Histopathology confirmed benign margins with clear boundary.": {
        "ru": "Удален атипичный диспластический невус в верхней части спины. Гистология подтвердила доброкачественные чистые края.",
        "sr": "Uklonjen atipični displastični nevus na leđima. Histopatologija potvrdila benigne i čiste ivice."
    },
    "Birch pollen count very high. Started desloratadine 5mg daily. Albuterol inhaler kept on hand, only needed twice after jogging.": {
        "ru": "Высокая концентрация пыльцы березы. Начат дезлоратадин 5 мг/день. Сальбутамол наготове, потребовался дважды после бега.",
        "sr": "Visoka koncentracija polena breze. Započet desloratadin 5mg dnevno. Salbutamol inhalator pri ruci, potreban samo dva puta nakon trčanja."
    },
    "Height: 104 cm (60th percentile), Weight: 17 kg (55th percentile). Vision screening passed. Recommended preschool MMR booster.": {
        "ru": "Рост: 104 см (60-й перцентиль), Вес: 17 кг (55-й перцентиль). Зрение в норме. Рекомендована ревакцинация КПК перед садом/школой.",
        "sr": "Visina: 104 cm (60. percentil), Težina: 17 kg (55. percentil). Pregled vida uredan. Preporučena predškolska MMR revakcinacija."
    },
    "Low fever, mild dehydration. Prescribed oral rehydration salts (ORS) and light diet. Fully resolved in 3 days.": {
        "ru": "Небольшая температура, легкое обезвоживание. Назначен регидрон и диета. Полное выздоровление за 3 дня.",
        "sr": "Blaga temperatura, blaga dehidracija. Prepisani oralni rehidracioni rastvori i lagana ishrana. Potpuni oporavak za 3 dana."
    },

    # Facilities & Providers
    "Central Diagnostics Lab": {
        "ru": "Центральная диагностическая лаборатория",
        "sr": "Centralna dijagnostička laboratorija"
    },
    "Heart & Health Clinic": {
        "ru": "Клиника кардиологии и здоровья",
        "sr": "Klinika za srce i zdravlje"
    },
    "Urgent Care Center": {
        "ru": "Пункт неотложной помощи",
        "sr": "Centar za hitnu pomoć"
    },
    "St. Jude Dermatology": {
        "ru": "Дерматологическая клиника св. Иуды",
        "sr": "Dermatološka ordinacija"
    },
    "City Pediatric Clinic": {
        "ru": "Городская детская поликлиника",
        "sr": "Gradska pedijatrijska klinika"
    },
    "Home Log": {
        "ru": "Домашний дневник",
        "sr": "Kućni dnevnik"
    },
    "Self-Report": {
        "ru": "Самоотчет",
        "sr": "Lični unos"
    },

    # Reminders
    "Bi-annual Dental Cleaning & Examination": {
        "ru": "Профгигиена полости рта и осмотр у стоматолога",
        "sr": "Stomatološki pregled i skidanje kamenca"
    },
    "Last visit was in May 2026. Routine checkup and tartar removal.": {
        "ru": "Прошлый визит был в мае 2026. Плановый осмотр и снятие зубного камня.",
        "sr": "Poslednja poseta u maju 2026. Rutinska kontrola i uklanjanje kamenca."
    },
    "Repeat Ferritin & Complete Blood Count (CBC)": {
        "ru": "Повторный анализ на ферритин и ОАК",
        "sr": "Kontrolni feritin i kompletna krvna slika (KKS)"
    },
    "Check progress after 3 full months on iron bisglycinate.": {
        "ru": "Контроль динамики через 3 месяца приема бисглицината железа.",
        "sr": "Kontrola dinamike nakon 3 meseca suplementacije gvožđem."
    },
    "Annual Dermatological Full-Body Mole Check": {
        "ru": "Ежегодный осмотр родинок у дерматолога (дерматоскопия)",
        "sr": "Godišnji pregled mladeža kod dermatologa (dermoskopija)"
    },
    "12-month follow up after dysplastic mole excision in Nov 2025.": {
        "ru": "Контроль через 12 месяцев после иссечения невуса в ноябре 2025.",
        "sr": "Kontrola 12 meseci nakon uklanjanja nevusa u novembru 2025."
    },
    "Tetanus / Diphtheria / Pertussis Booster (Tdap)": {
        "ru": "Ревакцинация АДС-М (столбняк, дифтерия, коклюш)",
        "sr": "Revakcinacija protiv tetanusa i difterije (DiTePer)"
    },
    "Due every 10 years. Last administered in 2017.": {
        "ru": "Проводится каждые 10 лет. Последняя прививка была в 2017 году.",
        "sr": "Radi se na svakih 10 godina. Poslednja primljena 2017."
    },
    "Preschool MMR (Measles/Mumps/Rubella) Booster": {
        "ru": "Ревакцинация КПК (корь, паротит, краснуха) перед школой",
        "sr": "Predškolska MMR revakcinacija (male boginje, zauške, rubeola)"
    },
    "Required 4-year booster before kindergarten registration.": {
        "ru": "Обязательная ревакцинация в 4-6 лет перед садом или школой.",
        "sr": "Obavezna revakcinacija u uzrastu od 4 godine pre polaska u vrtić."
    },
    "Pediatric Dental Cleaning & Fluoride Check": {
        "ru": "Детский стоматолог: профгигиена и фторирование",
        "sr": "Kontrola dečjeg zubara i zaštita fluorom"
    },
    "Routine dental examination and fluoride varnish.": {
        "ru": "Плановый осмотр молочных зубов и покрытие фторлаком.",
        "sr": "Rutinski pregled zuba i premazivanje fluorom."
    },

    # Profile Attributes
    "Penicillin (mild rash), Pollen": {
        "ru": "Пенициллин (кожная сыпь), пыльца березы",
        "sr": "Penicilin (blagi osip), polen"
    },
    "Mild Seasonal Asthma": {
        "ru": "Легкая сезонная бронхиальная астма",
        "sr": "Blaga sezonska astma"
    },
    "Vitamin D3 (2000 IU daily), Iron Bisglycinate (25mg)": {
        "ru": "Витамин D3 (2000 ME/день), Бисглицинат железа (25 мг)",
        "sr": "Vitamin D3 (2000 IJ dnevno), Gvožđe bisglicinat (25 mg)"
    },
    "Partner: +1 (555) 019-2834": {
        "ru": "Супруг(а): +1 (555) 019-2834",
        "sr": "Partner: +1 (555) 019-2834"
    },
    "Peanuts (mild hives)": {
        "ru": "Арахис (крапивница)",
        "sr": "Kikiriki (blaga koprivnjača)"
    },
    "Multivitamin syrup": {
        "ru": "Детский поливитаминный сироп",
        "sr": "Dečji multivitaminski sirup"
    },
    "Mother (Alex): +1 (555) 019-2834": {
        "ru": "Мама (Алекс): +1 (555) 019-2834",
        "sr": "Majka (Aleks): +1 (555) 019-2834"
    }
}

def get_translations(lang: str = "en") -> Dict[str, str]:
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang]

def localize_biomarker_name(name: str, lang: str = "en") -> str:
    if name in BIOMARKER_NAMES and lang in BIOMARKER_NAMES[name]:
        return BIOMARKER_NAMES[name][lang]
    return name

def localize_text(text: str, lang: str = "en") -> str:
    if not text or lang == "en":
        return text
    if text in CONTENT_TRANSLATIONS and lang in CONTENT_TRANSLATIONS[text]:
        return CONTENT_TRANSLATIONS[text][lang]
    return text

def localize_record(record: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    if lang == "en":
        return record
    r = dict(record)
    r["title"] = localize_text(r.get("title", ""), lang)
    r["notes"] = localize_text(r.get("notes", ""), lang)
    r["provider"] = localize_text(r.get("provider", ""), lang)
    r["facility"] = localize_text(r.get("facility", ""), lang)

    if "biomarkers" in r and r["biomarkers"]:
        localized_bms = []
        for b in r["biomarkers"]:
            b_copy = dict(b)
            b_copy["name"] = localize_biomarker_name(b_copy.get("name", ""), lang)
            localized_bms.append(b_copy)
        r["biomarkers"] = localized_bms
    return r

def localize_reminder(reminder: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    if lang == "en":
        return reminder
    rem = dict(reminder)
    rem["title"] = localize_text(rem.get("title", ""), lang)
    rem["notes"] = localize_text(rem.get("notes", ""), lang)
    return rem

def localize_profile(profile: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    if lang == "en":
        return profile
    p = dict(profile)
    p["allergies"] = localize_text(p.get("allergies", ""), lang)
    p["chronic_conditions"] = localize_text(p.get("chronic_conditions", ""), lang)
    p["current_medications"] = localize_text(p.get("current_medications", ""), lang)
    p["emergency_contact"] = localize_text(p.get("emergency_contact", ""), lang)
    return p
