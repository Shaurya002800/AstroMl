"""Plain-language multilingual presentation for non-expert users."""

from __future__ import annotations

from datetime import datetime


SUPPORTED_LANGUAGES = {
    "English": "en",
    "हिंदी": "hi",
    "Hinglish": "hinglish",
}

DOMAIN_NAMES = {
    "en": {
        "career": "Career and work",
        "relationships": "Relationships and partnership",
        "finance": "Money and resources",
        "education": "Education and learning",
        "wellbeing": "Wellbeing and daily balance",
    },
    "hi": {
        "career": "करियर और काम",
        "relationships": "रिश्ते और साझेदारी",
        "finance": "धन और संसाधन",
        "education": "शिक्षा और सीखना",
        "wellbeing": "स्वास्थ्य और दैनिक संतुलन",
    },
    "hinglish": {
        "career": "Career aur kaam",
        "relationships": "Relationships aur partnership",
        "finance": "Paise aur resources",
        "education": "Education aur learning",
        "wellbeing": "Wellbeing aur daily balance",
    },
}

DOMAIN_FOCUS = {
    "en": {
        "career": "Review responsibilities, direction, workload, recognition, and income from work.",
        "relationships": "Discuss communication, expectations, family context, and existing or future partnerships.",
        "finance": "Review income, savings, obligations, spending, and the difference between expected and available money.",
        "education": "Review the learning goal, consistency, examinations, mentors, and practical obstacles.",
        "wellbeing": "Review routine, sleep, stress, energy, and available support. This is not medical advice.",
    },
    "hi": {
        "career": "जिम्मेदारियों, काम की दिशा, कार्यभार, पहचान और काम से होने वाली आय पर ध्यान दें।",
        "relationships": "बातचीत, अपेक्षाओं, परिवार की भूमिका और वर्तमान या भविष्य के रिश्तों पर चर्चा करें।",
        "finance": "आय, बचत, जिम्मेदारियों, खर्च और अपेक्षित तथा उपलब्ध धन के अंतर को देखें।",
        "education": "पढ़ाई के लक्ष्य, नियमितता, परीक्षा, मार्गदर्शन और व्यावहारिक बाधाओं पर ध्यान दें।",
        "wellbeing": "दिनचर्या, नींद, तनाव, ऊर्जा और सहयोग को देखें। यह चिकित्सकीय सलाह नहीं है।",
    },
    "hinglish": {
        "career": "Responsibilities, work direction, workload, recognition aur work income ko review karein.",
        "relationships": "Communication, expectations, family context aur current ya future partnership par baat karein.",
        "finance": "Income, savings, obligations, spending aur expected versus available money ko review karein.",
        "education": "Learning goal, consistency, exams, mentors aur practical obstacles ko review karein.",
        "wellbeing": "Routine, sleep, stress, energy aur support ko review karein. Yeh medical advice nahi hai.",
    },
}

PLANET_NAMES = {
    "en": {},
    "hi": {
        "Sun": "सूर्य",
        "Moon": "चंद्र",
        "Mars": "मंगल",
        "Mercury": "बुध",
        "Jupiter": "गुरु",
        "Venus": "शुक्र",
        "Saturn": "शनि",
        "Rahu": "राहु",
        "Ketu": "केतु",
    },
    "hinglish": {
        "Sun": "Surya",
        "Moon": "Chandra",
        "Mars": "Mangal",
        "Mercury": "Budh",
        "Jupiter": "Guru",
        "Venus": "Shukra",
        "Saturn": "Shani",
        "Rahu": "Rahu",
        "Ketu": "Ketu",
    },
}

TEXT = {
    "en": {
        "title": "Your Astrology Summary",
        "subtitle": "The most relevant conclusions in simple language",
        "overview": "Main picture",
        "current_phase": "Current life phase",
        "priority_areas": "Important life areas",
        "strengths": "Strongest supports",
        "care": "Areas to handle thoughtfully",
        "reliability": "How carefully to read this report",
        "focus": "What to discuss",
        "attention": "Keep in mind",
        "technical": "Astrology expert details",
        "download": "Download summary",
        "no_major_weakness": (
            "No strongly weak life area was detected by the current rule set. "
            "This does not mean that every outcome will be easy."
        ),
        "no_attention": "No major caution was detected for this area.",
        "mixed_attention": (
            "Some supporting and challenging factors appear together, so real-life "
            "context matters."
        ),
        "yoga": (
            "A traditional yoga pattern was detected, but it still requires an "
            "experienced astrologer to judge its real strength."
        ),
        "disclaimer": (
            "This report describes traditional astrological tendencies, not certain "
            "events or scientifically proven predictions. Use it for reflection and "
            "discussion, not as medical, legal, or financial advice."
        ),
    },
    "hi": {
        "title": "आपकी ज्योतिषीय रिपोर्ट",
        "subtitle": "सरल भाषा में सबसे महत्वपूर्ण निष्कर्ष",
        "overview": "मुख्य तस्वीर",
        "current_phase": "वर्तमान जीवन चरण",
        "priority_areas": "महत्वपूर्ण जीवन क्षेत्र",
        "strengths": "सबसे मजबूत सहायक पक्ष",
        "care": "जिन क्षेत्रों को समझदारी से संभालें",
        "reliability": "इस रिपोर्ट को कितनी सावधानी से पढ़ें",
        "focus": "किस बात पर चर्चा करें",
        "attention": "ध्यान रखें",
        "technical": "ज्योतिष विशेषज्ञ के लिए तकनीकी विवरण",
        "download": "रिपोर्ट डाउनलोड करें",
        "no_major_weakness": (
            "मौजूदा नियमों के अनुसार कोई बहुत कमजोर जीवन क्षेत्र नहीं मिला। "
            "इसका अर्थ यह नहीं कि हर परिणाम आसानी से मिलेगा।"
        ),
        "no_attention": "इस क्षेत्र में कोई बड़ी सावधानी नहीं मिली।",
        "mixed_attention": (
            "यहाँ सहायक और चुनौतीपूर्ण दोनों संकेत हैं, इसलिए वास्तविक जीवन की "
            "परिस्थिति महत्वपूर्ण है।"
        ),
        "yoga": (
            "एक पारंपरिक योग का संकेत मिला है, लेकिन उसकी वास्तविक शक्ति का निर्णय "
            "अनुभवी ज्योतिषी को करना चाहिए।"
        ),
        "disclaimer": (
            "यह रिपोर्ट पारंपरिक ज्योतिषीय प्रवृत्तियाँ बताती है, निश्चित घटनाएँ या "
            "वैज्ञानिक रूप से प्रमाणित भविष्यवाणी नहीं। इसे विचार और चर्चा के लिए "
            "उपयोग करें, चिकित्सकीय, कानूनी या वित्तीय सलाह के रूप में नहीं।"
        ),
    },
    "hinglish": {
        "title": "Aapki Astrology Summary",
        "subtitle": "Simple language mein sabse important conclusions",
        "overview": "Main picture",
        "current_phase": "Current life phase",
        "priority_areas": "Important life areas",
        "strengths": "Sabse strong support",
        "care": "Jin areas ko thoughtfully handle karein",
        "reliability": "Is report ko kitni carefully padhein",
        "focus": "Kis baat par discuss karein",
        "attention": "Dhyan rakhein",
        "technical": "Astrology expert ke liye technical details",
        "download": "Summary download karein",
        "no_major_weakness": (
            "Current rules ke according koi bahut weak life area detect nahi hua. "
            "Iska matlab yeh nahi ki har result easily milega."
        ),
        "no_attention": "Is area mein koi major caution detect nahi hua.",
        "mixed_attention": (
            "Supportive aur challenging factors dono hain, isliye real-life context "
            "important hai."
        ),
        "yoga": (
            "Ek traditional yoga pattern detect hua hai, lekin uski real strength "
            "experienced astrologer ko judge karni chahiye."
        ),
        "disclaimer": (
            "Yeh report traditional astrological tendencies batati hai, certain "
            "events ya scientifically proven predictions nahi. Isse reflection aur "
            "discussion ke liye use karein, medical, legal ya financial advice ke "
            "liye nahi."
        ),
    },
}


def build_plain_language_report(
    model_payload: dict,
    language: str = "en",
) -> dict:
    if language not in TEXT:
        raise ValueError(f"Unsupported report language: {language}")

    brief = model_payload["consultation_brief"]
    domains = brief["domain_reviews"]
    ranked_domains = sorted(
        domains.items(),
        key=lambda item: (
            item[1]["activation_score"],
            item[1]["support_score"],
        ),
        reverse=True,
    )
    domain_sections = [
        _domain_section(key, review, language)
        for key, review in ranked_domains
    ]

    return {
        "language": language,
        "labels": TEXT[language],
        "title": TEXT[language]["title"],
        "subtitle": TEXT[language]["subtitle"],
        "overview": _overview(ranked_domains, language),
        "current_phase": _current_phase(
            brief["dasha_focus"],
            ranked_domains,
            language,
        ),
        "priority_areas": domain_sections,
        "strengths": _strengths(brief, ranked_domains, language),
        "care": _care_items(brief, ranked_domains, language),
        "reliability": _reliability(brief, language),
        "disclaimer": TEXT[language]["disclaimer"],
    }


def render_plain_language_markdown(summary: dict) -> str:
    labels = summary["labels"]
    lines = [
        f"# {summary['title']}",
        "",
        summary["subtitle"],
        "",
        f"## {labels['overview']}",
        summary["overview"],
        "",
        f"## {labels['current_phase']}",
        f"**{summary['current_phase']['title']}**",
        "",
        summary["current_phase"]["summary"],
        "",
        summary["current_phase"]["dates"],
        "",
        f"## {labels['priority_areas']}",
    ]
    for area in summary["priority_areas"]:
        lines.extend([
            "",
            f"### {area['title']}",
            f"**{area['status']}**",
            "",
            area["summary"],
            "",
            f"**{labels['focus']}:** {area['focus']}",
            "",
            f"**{labels['attention']}:** {area['attention']}",
        ])
    lines.extend(["", f"## {labels['strengths']}"])
    lines.extend(f"- {item}" for item in summary["strengths"])
    lines.extend(["", f"## {labels['care']}"])
    lines.extend(f"- {item}" for item in summary["care"])
    lines.extend([
        "",
        f"## {labels['reliability']}",
        f"**{summary['reliability']['level']}**",
        "",
        summary["reliability"]["text"],
        "",
        "---",
        summary["disclaimer"],
    ])
    return "\n".join(lines)


def _overview(ranked_domains: list, language: str) -> str:
    first = DOMAIN_NAMES[language][ranked_domains[0][0]]
    second = DOMAIN_NAMES[language][ranked_domains[1][0]]
    top_areas = _join_names([first, second], language)
    if language == "hi":
        return (
            f"इस समय {top_areas} सबसे अधिक सक्रिय विषय दिखाई देते हैं। "
            "कुंडली में इनके लिए सहायक आधार है, लेकिन निर्णय वास्तविक परिस्थिति "
            "और व्यक्ति के अनुभव को समझकर ही लें।"
        )
    if language == "hinglish":
        return (
            f"Is time {top_areas} sabse zyada active themes dikh rahe "
            "hain. Inke liye chart mein support hai, lekin decision real-life "
            "situation aur person ke experience ko samajhkar hi lein."
        )
    return (
        f"At present, {top_areas} appear to be the most active themes. "
        "The chart shows support for them, but decisions should still be based on "
        "the person's real circumstances and experience."
    )


def _current_phase(dasha: dict, ranked_domains: list, language: str) -> dict:
    main = _planet(dasha["mahadasha_lord"], language)
    supporting = _planet(dasha.get("antardasha_lord"), language)
    short = _planet(dasha.get("pratyantar_lord"), language)
    top_area_names = [
        DOMAIN_NAMES[language][item[0]]
        for item in ranked_domains[:2]
    ]
    top_areas = _join_names(top_area_names, language)
    if language == "hi":
        title = f"मुख्य प्रभाव: {main} | सहायक प्रभाव: {supporting}"
        summary = (
            f"अभी दीर्घकालीन चरण {main}, मध्यम चरण {supporting} और निकट चरण "
            f"{short} से जुड़ा है। वर्तमान गणना में {top_areas} पर अधिक ध्यान "
            "दिखता है। इसे समय का संकेत मानें, निश्चित घटना नहीं।"
        )
        dates = (
            f"मध्यम चरण: {_date(dasha['antardasha_start'])} से "
            f"{_date(dasha['antardasha_end'])}"
        )
    elif language == "hinglish":
        title = f"Main influence: {main} | Supporting influence: {supporting}"
        summary = (
            f"Long-term phase {main}, medium phase {supporting} aur short-term "
            f"phase {short} se linked hai. Current calculation mein {top_areas} "
            "par zyada focus dikh raha hai. Isse timing context samjhein, certain "
            "event nahi."
        )
        dates = (
            f"Medium phase: {_date(dasha['antardasha_start'])} se "
            f"{_date(dasha['antardasha_end'])}"
        )
    else:
        title = f"Main influence: {main} | Supporting influence: {supporting}"
        summary = (
            f"The long-term phase is linked with {main}, the supporting phase "
            f"with {supporting}, and the shorter phase with {short}. The current "
            f"calculation places more attention on {top_areas}. Treat this as "
            "timing context, not a certain event."
        )
        dates = (
            f"Supporting phase: {_date(dasha['antardasha_start'])} to "
            f"{_date(dasha['antardasha_end'])}"
        )
    return {"title": title, "summary": summary, "dates": dates}


def _domain_section(key: str, review: dict, language: str) -> dict:
    support = _support_bucket(review["support_level"])
    activation = _activation_bucket(review["activation_score"])
    status, summary = _domain_status_text(support, activation, language)
    attention = (
        TEXT[language]["mixed_attention"]
        if review["attention_evidence"]
        else TEXT[language]["no_attention"]
    )
    return {
        "key": key,
        "title": DOMAIN_NAMES[language][key],
        "status": status,
        "summary": summary,
        "focus": DOMAIN_FOCUS[language][key],
        "attention": attention,
        "relevance_rank": review["activation_score"],
    }


def _domain_status_text(
    support: str,
    activation: str,
    language: str,
) -> tuple[str, str]:
    if language == "hi":
        status = {
            "high": "अभी बहुत महत्वपूर्ण",
            "active": "अभी महत्वपूर्ण",
            "some": "कुछ सक्रियता",
            "quiet": "फिलहाल शांत",
        }[activation]
        support_text = {
            "strong": "इस क्षेत्र का आधार सहायक और मजबूत दिखाई देता है।",
            "moderate": "इस क्षेत्र में उचित सहयोग है, लेकिन निरंतर प्रयास जरूरी है।",
            "mixed": "इस क्षेत्र में मिले-जुले संकेत हैं; परिस्थिति के अनुसार परिणाम बदल सकते हैं।",
            "attention": "इस क्षेत्र में अधिक धैर्य, योजना और सहयोग की जरूरत हो सकती है।",
        }[support]
        activation_text = {
            "high": "यह वर्तमान समय के सबसे प्रमुख विषयों में से एक है।",
            "active": "यह विषय वर्तमान समय में स्पष्ट रूप से सक्रिय है।",
            "some": "यह विषय मौजूद है, पर सबसे प्रमुख नहीं है।",
            "quiet": "यह अभी मुख्य विषय नहीं दिखता।",
        }[activation]
    elif language == "hinglish":
        status = {
            "high": "Abhi bahut important",
            "active": "Abhi important",
            "some": "Kuch activity",
            "quiet": "Filhaal quiet",
        }[activation]
        support_text = {
            "strong": "Is area ka foundation supportive aur strong dikh raha hai.",
            "moderate": "Is area mein reasonable support hai, lekin consistent effort zaroori hai.",
            "mixed": "Is area mein mixed signals hain; result situation ke according change ho sakta hai.",
            "attention": "Is area mein extra patience, planning aur support ki zarurat ho sakti hai.",
        }[support]
        activation_text = {
            "high": "Yeh current time ke sabse prominent themes mein se ek hai.",
            "active": "Yeh theme current time mein clearly active hai.",
            "some": "Yeh theme present hai, lekin sabse prominent nahi.",
            "quiet": "Yeh abhi main theme nahi dikh raha.",
        }[activation]
    else:
        status = {
            "high": "Very important now",
            "active": "Important now",
            "some": "Some current activity",
            "quiet": "Relatively quiet now",
        }[activation]
        support_text = {
            "strong": "This area has a supportive and comparatively strong foundation.",
            "moderate": "This area has reasonable support, although steady effort still matters.",
            "mixed": "This area shows mixed factors, so results can vary with circumstances.",
            "attention": "This area may need more patience, planning, and support.",
        }[support]
        activation_text = {
            "high": "It is one of the most prominent themes in the current period.",
            "active": "It is clearly active in the current period.",
            "some": "It is present, but it is not the strongest current focus.",
            "quiet": "It does not appear to be a main current focus.",
        }[activation]
    return status, f"{support_text} {activation_text}"


def _strengths(brief: dict, ranked_domains: list, language: str) -> list[str]:
    strong_domains = [
        DOMAIN_NAMES[language][key]
        for key, review in ranked_domains
        if _support_bucket(review["support_level"]) == "strong"
    ][:3]
    strong_planets = [
        _planet(item["planet"], language)
        for item in brief["notable_strengths"]["strong_planets"]
    ][:3]

    if language == "hi":
        items = [
            f"{_join_names(strong_domains, language)} के लिए कुंडली में "
            "अपेक्षाकृत मजबूत आधार है।"
        ]
        if strong_planets:
            items.append(
                f"{_join_names(strong_planets, language)} तुलनात्मक रूप से "
                "मजबूत हैं; इन्हें "
                "अकेले देखकर निष्कर्ष न निकालें।"
            )
    elif language == "hinglish":
        items = [
            f"{_join_names(strong_domains, language)} ke liye chart mein "
            "comparatively strong foundation hai."
        ]
        if strong_planets:
            items.append(
                f"{_join_names(strong_planets, language)} comparatively strong "
                "hain; inko "
                "akele dekhkar conclusion na nikalein."
            )
    else:
        items = [
            "The chart shows a comparatively strong foundation for "
            f"{_join_names(strong_domains, language)}."
        ]
        if strong_planets:
            items.append(
                f"{_join_names(strong_planets, language)} are comparatively "
                "strong; they "
                "should not be interpreted in isolation."
            )
    if brief["notable_strengths"]["detected_yogas"]:
        items.append(TEXT[language]["yoga"])
    return items


def _care_items(brief: dict, ranked_domains: list, language: str) -> list[str]:
    items = []
    for key, review in ranked_domains:
        support = _support_bucket(review["support_level"])
        if support in {"mixed", "attention"} or review["attention_evidence"]:
            title = DOMAIN_NAMES[language][key]
            if language == "hi":
                items.append(
                    f"{title} में कुछ मिले-जुले संकेत हैं; बातचीत और वास्तविक "
                    "परिस्थिति समझे बिना निश्चित निष्कर्ष न निकालें।"
                )
            elif language == "hinglish":
                items.append(
                    f"{title} mein kuch mixed factors hain; discussion aur real "
                    "situation samjhe bina certain conclusion na nikalein."
                )
            else:
                items.append(
                    f"{title} contains some mixed factors; avoid firm conclusions "
                    "without discussion and real-life context."
                )
    if not items:
        items.append(TEXT[language]["no_major_weakness"])
    return items[:3]


def _reliability(brief: dict, language: str) -> dict:
    precision = brief["assumptions"]["time_precision"]
    stable_15 = brief["birth_time_sensitivity"].get(
        "stable_within_15_minutes",
        False,
    )
    if precision == "exact" and stable_15:
        level = {
            "en": "Higher calculation stability",
            "hi": "गणना की स्थिरता अधिक",
            "hinglish": "Calculation stability higher hai",
        }[language]
        text = {
            "en": "The entered birth time is marked exact, and nearby 15-minute checks remain stable.",
            "hi": "जन्म समय को सटीक बताया गया है और 15 मिनट आसपास की जाँच स्थिर रही।",
            "hinglish": "Birth time exact mark hua hai aur nearby 15-minute checks stable rahe.",
        }[language]
    elif precision == "unknown":
        level = {
            "en": "Use major caution",
            "hi": "बहुत सावधानी से उपयोग करें",
            "hinglish": "Major caution ke saath use karein",
        }[language]
        text = {
            "en": "Birth time is unknown. House and divisional-chart conclusions should not be relied on without rectification.",
            "hi": "जन्म समय ज्ञात नहीं है। समय-सुधार के बिना भाव और वर्ग कुंडली के निष्कर्षों पर भरोसा न करें।",
            "hinglish": "Birth time unknown hai. Rectification ke bina house aur divisional-chart conclusions par rely na karein.",
        }[language]
    else:
        level = {
            "en": "Read fine details cautiously",
            "hi": "सूक्ष्म विवरण सावधानी से पढ़ें",
            "hinglish": "Fine details carefully padhein",
        }[language]
        text = {
            "en": "Some house or divisional details change near the entered time. The broad themes are more useful than minute-level conclusions.",
            "hi": "दिए गए समय के आसपास कुछ भाव या वर्ग विवरण बदलते हैं। बहुत सूक्ष्म निष्कर्षों की तुलना में व्यापक विषय अधिक उपयोगी हैं।",
            "hinglish": "Entered time ke aas-paas kuch house ya divisional details change hote hain. Minute-level conclusions se zyada broad themes useful hain.",
        }[language]
    return {"level": level, "text": text}


def _support_bucket(level: str) -> str:
    if level.startswith("Strong"):
        return "strong"
    if level.startswith("Moderate"):
        return "moderate"
    if level.startswith("Mixed"):
        return "mixed"
    return "attention"


def _activation_bucket(score: int) -> str:
    if score >= 5:
        return "high"
    if score >= 3:
        return "active"
    if score >= 1:
        return "some"
    return "quiet"


def _planet(planet: str | None, language: str) -> str:
    if not planet:
        return "-"
    return PLANET_NAMES[language].get(planet, planet)


def _date(value: str | None) -> str:
    if not value:
        return "-"
    return datetime.fromisoformat(value).strftime("%d-%m-%Y")


def _join_names(items: list[str], language: str) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    conjunction = {
        "en": "and",
        "hi": "और",
        "hinglish": "aur",
    }[language]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"
