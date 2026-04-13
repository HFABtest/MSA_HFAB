"""
Survey question bank for unit-level maturity measurement.

Inspired by: Cyber Defence NIS2, SKR metodstöd, MCF.
Adapted for HFAB's context — questions are written so that both
a facilities technician and a financial analyst can understand them.

Structure:
- SURVEY_SECTIONS: The assessment areas
- SURVEY_QUESTIONS: All questions with tags for profile-based filtering
- MATURITY_LEVELS: The 5-level scale
- UNIT_PROFILES: Profile tags derived from HFAB grunduppdrag
"""

# ── Maturity levels (5-level NIS2-inspired scale) ────────────────────

SURVEY_LEVELS = [
    {
        "level": 1,
        "name": "Inte påbörjat",
        "description": "Vi har inte börjat med detta. Det saknas rutiner och dokumentation.",
        "color": "#c0392b",
    },
    {
        "level": 2,
        "name": "Påbörjat",
        "description": "Vi har börjat planera eller precis påbörjat arbetet. Lite eller ingen dokumentation finns.",
        "color": "#e67e22",
    },
    {
        "level": 3,
        "name": "Delvis på plats",
        "description": "Arbetssättet finns delvis. Viss dokumentation finns. De flesta vet vad som gäller.",
        "color": "#f1c40f",
    },
    {
        "level": 4,
        "name": "Till stor del på plats",
        "description": "Arbetssättet fungerar och är dokumenterat. Personal är utbildad. Uppföljning sker men inte systematiskt.",
        "color": "#27ae60",
    },
    {
        "level": 5,
        "name": "Fullt etablerat",
        "description": "Arbetssättet är fullt infört, dokumenterat, mäts och förbättras löpande. Kunskap verifieras.",
        "color": "#2980b9",
    },
]

# ── Sections ─────────────────────────────────────────────────────────

SURVEY_SECTIONS = [
    {
        "key": "awareness",
        "name": "Medvetenhet",
        "description": "Hur väl förstår och hanterar medarbetare informationssäkerhet i vardagen?",
        "icon": "🎓",
    },
    {
        "key": "information_handling",
        "name": "Information",
        "description": "Hur hanteras information genom hela livscykeln — från att den skapas till att den gallras?",
        "icon": "📋",
    },
    {
        "key": "incident",
        "name": "Incidenter",
        "description": "Vet medarbetare hur de ska agera vid incidenter, och finns det rutiner?",
        "icon": "🚨",
    },
    {
        "key": "access",
        "name": "Behörigheter",
        "description": "Hur hanteras behörigheter till system, lokaler och information?",
        "icon": "🔑",
    },
    {
        "key": "suppliers",
        "name": "Leverantörer",
        "description": "Hur hanteras informationssäkerhet gentemot leverantörer och samarbetspartners?",
        "icon": "🤝",
    },
    {
        "key": "continuity",
        "name": "Kontinuitet",
        "description": "Kan verksamheten fortsätta fungera vid störningar, och finns det planer?",
        "icon": "🔄",
    },
    {
        "key": "physical",
        "name": "Fysiskt skydd",
        "description": "Hur skyddas lokaler, utrustning och fysiska informationsbärare?",
        "icon": "🏢",
    },
    {
        "key": "gdpr",
        "name": "GDPR",
        "description": "Hur hanteras personuppgifter och dataskyddsförordningens krav?",
        "icon": "🛡️",
    },
]

# ── Unit profiles (derived from HFAB grunduppdrag) ───────────────────

UNIT_PROFILES = {
    "office_admin": {
        "name": "Kontor och administration",
        "description": "Arbetar med ekonomi, HR, styrning, juridik eller verksamhetsstöd",
        "example_units": ["HR", "Ekonomi och verksamhetsstöd", "Affärsstöd", "Kommunikation"],
        "tags": ["handles_personal_data", "handles_financial_data", "uses_office_systems", "handles_public_records"],
    },
    "it_security": {
        "name": "IT och informationssäkerhet",
        "description": "Arbetar med IT-miljö, system, informationssäkerhet eller dataskydd",
        "example_units": ["IT och informationssäkerhet"],
        "tags": ["handles_personal_data", "handles_financial_data", "uses_office_systems", "manages_it_systems", "handles_public_records", "handles_classified_info"],
    },
    "customer_facing": {
        "name": "Kundkontakt och uthyrning",
        "description": "Arbetar med kundservice, uthyrning, kontraktshantering eller marknadsföring",
        "example_units": ["Kundcenter", "Produkt", "Marknad"],
        "tags": ["handles_personal_data", "handles_customer_data", "uses_office_systems", "handles_contracts"],
    },
    "property_mgmt": {
        "name": "Fastighetsförvaltning",
        "description": "Arbetar med fastighetsförvaltning, affärsområden eller fastighetsstab",
        "example_units": ["Affärsområden", "Fastighetsstab", "Fastighetsutveckling"],
        "tags": ["handles_personal_data", "handles_supplier_data", "uses_field_systems", "handles_building_systems", "handles_contracts"],
    },
    "field_operations": {
        "name": "Fältarbete och drift",
        "description": "Arbetar med underhåll, reparationer, yttre skötsel eller egenregi",
        "example_units": ["Egen regi", "Framtidsakademin"],
        "tags": ["uses_field_systems", "handles_building_systems", "handles_keys_access"],
    },
    "social_work": {
        "name": "Socialt arbete och bostadssocialt",
        "description": "Arbetar med bostadssociala frågor, trygghet, integration eller säkerhet",
        "example_units": ["Bostadssociala"],
        "tags": ["handles_personal_data", "handles_sensitive_personal_data", "handles_customer_data", "uses_office_systems"],
    },
}

# ── Questions ────────────────────────────────────────────────────────
# Each question has:
#   - id: unique identifier
#   - section: which section it belongs to
#   - text: the question (written for everyone to understand)
#   - help_text: explanation to help the respondent
#   - standard: True = everyone gets it, False = only matching profiles
#   - profile_tags: list of tags — question shown if unit has ANY of these tags
#     (empty list + standard=True means everyone)

SURVEY_QUESTIONS = [
    # ── MEDVETENHET OCH UTBILDNING ────────────────────────────────────
    {
        "id": "awareness_01",
        "section": "awareness",
        "text": "Vet du vad som gäller för informationssäkerhet på din arbetsplats?",
        "help_text": "Tänk på om det finns regler, policyer eller riktlinjer som du känner till och förstår. Det kan handla om hur du hanterar lösenord, e-post eller dokument.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "awareness_02",
        "section": "awareness",
        "text": "Har du fått utbildning i informationssäkerhet det senaste året?",
        "help_text": "Utbildning kan vara allt från en e-kurs till en genomgång på ett personalmöte. Det viktiga är att du fått tillfälle att lära dig om risker och hur du skyddar information.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "awareness_03",
        "section": "awareness",
        "text": "Skulle du känna igen ett nätfiskemeddelande (phishing) om du fick ett?",
        "help_text": "Nätfiske är när någon försöker lura dig att klicka på en länk eller lämna ut uppgifter genom att utge sig för att vara någon annan.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "awareness_04",
        "section": "awareness",
        "text": "Vet ledningen på din enhet varför informationssäkerhet är viktigt?",
        "help_text": "Tänk på om din chef aktivt pratar om säkerhet, efterfrågar åtgärder eller prioriterar det i verksamhetsplaneringen.",
        "standard": True,
        "profile_tags": [],
    },

    # ── INFORMATIONSHANTERING ─────────────────────────────────────────
    {
        "id": "info_01",
        "section": "information_handling",
        "text": "Vet du vilken information som är viktigast att skydda i ditt dagliga arbete?",
        "help_text": "Olika information har olika skyddsvärde. Ekonomiska prognoser, hyresgästuppgifter och byggritningar kräver olika skydd.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "info_02",
        "section": "information_handling",
        "text": "Finns det tydliga rutiner för hur du sparar, delar och gallrar dokument?",
        "help_text": "Det handlar om var du sparar filer (delad mapp, molntjänst, lokalt), hur du delar dem med kollegor eller externa och när de ska tas bort.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "info_03",
        "section": "information_handling",
        "text": "Har din enhet gjort en inventering av vilken information ni hanterar?",
        "help_text": "En inventering innebär att ni kartlagt vilka informationsmängder som finns, var de lagras och hur skyddsvärda de är.",
        "standard": False,
        "profile_tags": ["handles_financial_data", "handles_personal_data", "handles_classified_info"],
    },
    {
        "id": "info_04",
        "section": "information_handling",
        "text": "Används informationsklassning för att bestämma rätt skyddsnivå?",
        "help_text": "Informationsklassning innebär att man bedömer konsekvensen om information röjs, ändras eller blir otillgänglig — och väljer skyddsåtgärder efter det.",
        "standard": False,
        "profile_tags": ["handles_financial_data", "handles_personal_data", "handles_classified_info", "manages_it_systems"],
    },
    {
        "id": "info_05",
        "section": "information_handling",
        "text": "Hanterar du offentliga handlingar och vet du vad som gäller kring sekretess?",
        "help_text": "Som kommunalt bolag omfattas HFAB av offentlighetsprincipen. Vissa handlingar kan begäras ut av allmänheten.",
        "standard": False,
        "profile_tags": ["handles_public_records"],
    },

    # ── INCIDENTER OCH AVVIKELSER ─────────────────────────────────────
    {
        "id": "incident_01",
        "section": "incident",
        "text": "Vet du hur du rapporterar en informationssäkerhetsincident?",
        "help_text": "En incident kan vara ett borttappat USB-minne, ett mejl skickat till fel person, ett intrångsförsök eller ett system som slutat fungera.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "incident_02",
        "section": "incident",
        "text": "Vet du vem du ska kontakta om du misstänker en IT-säkerhetsincident?",
        "help_text": "Det ska finnas en tydlig kontaktväg — till exempel en person, ett telefonnummer eller ett ärendehanteringssystem.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "incident_03",
        "section": "incident",
        "text": "Finns det en dokumenterad process för hur incidenter hanteras på din enhet?",
        "help_text": "En process beskriver stegen: upptäcka, rapportera, åtgärda, utreda och lära av det som hänt.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "incident_04",
        "section": "incident",
        "text": "Genomförs incidentövningar eller scenarioträning på din enhet?",
        "help_text": "Övningar kan vara allt från en skrivbordsövning ('vad gör vi om...') till simulerade attacker.",
        "standard": False,
        "profile_tags": ["manages_it_systems", "handles_classified_info", "handles_building_systems"],
    },

    # ── BEHÖRIGHETER OCH ÅTKOMST ──────────────────────────────────────
    {
        "id": "access_01",
        "section": "access",
        "text": "Har du bara tillgång till de system och den information du behöver för ditt arbete?",
        "help_text": "Principen om minsta behörighet innebär att du inte ska ha åtkomst till mer än vad din roll kräver.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "access_02",
        "section": "access",
        "text": "Använder du unika lösenord och flerfaktorsautentisering (MFA) där det krävs?",
        "help_text": "MFA innebär att du utöver lösenord även verifierar dig med t.ex. en app eller SMS-kod.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "access_03",
        "section": "access",
        "text": "Finns det rutiner för att ta bort behörigheter när någon slutar eller byter roll?",
        "help_text": "Om behörigheter inte tas bort i tid kan obehöriga komma åt system och information.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "access_04",
        "section": "access",
        "text": "Granskas behörigheter regelbundet för att säkerställa att de fortfarande är rätt?",
        "help_text": "Med tiden kan behörigheter ackumuleras. Regelbunden granskning säkerställer att ingen har mer åtkomst än nödvändigt.",
        "standard": False,
        "profile_tags": ["manages_it_systems", "handles_financial_data", "handles_sensitive_personal_data"],
    },

    # ── LEVERANTÖRER OCH EXTERNA PARTER ───────────────────────────────
    {
        "id": "supplier_01",
        "section": "suppliers",
        "text": "Vet du vilka leverantörer din enhet är beroende av för att kunna fungera?",
        "help_text": "Tänk på IT-leverantörer, entreprenörer, molntjänster och andra som har tillgång till era system eller information.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "supplier_02",
        "section": "suppliers",
        "text": "Ställs det krav på informationssäkerhet i avtal med leverantörer?",
        "help_text": "Avtal bör innehålla krav på hur leverantören skyddar er information, rapporterar incidenter och hanterar personuppgifter.",
        "standard": False,
        "profile_tags": ["handles_contracts", "handles_supplier_data", "manages_it_systems"],
    },
    {
        "id": "supplier_03",
        "section": "suppliers",
        "text": "Följs leverantörernas säkerhetskrav upp regelbundet?",
        "help_text": "Uppföljning kan vara revisioner, rapportering eller möten där ni granskar att leverantören lever upp till kraven.",
        "standard": False,
        "profile_tags": ["handles_contracts", "handles_supplier_data", "manages_it_systems"],
    },

    # ── KONTINUITET OCH BEREDSKAP ─────────────────────────────────────
    {
        "id": "continuity_01",
        "section": "continuity",
        "text": "Vet du vad du ska göra om systemen du använder slutar fungera?",
        "help_text": "Tänk på ditt viktigaste arbetsverktyg — vad gör du om det inte fungerar i en dag? Finns det en plan B?",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "continuity_02",
        "section": "continuity",
        "text": "Finns det en plan för hur din enhet ska hantera längre avbrott?",
        "help_text": "En kontinuitetsplan beskriver hur verksamheten ska fortsätta fungera vid allvarliga störningar, t.ex. en cyberattack eller en brand.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "continuity_03",
        "section": "continuity",
        "text": "Testas och övas kontinuitetsplanerna regelbundet?",
        "help_text": "En plan som aldrig testats ger falsk trygghet. Övningar visar om planen fungerar i praktiken.",
        "standard": False,
        "profile_tags": ["manages_it_systems", "handles_building_systems", "handles_classified_info"],
    },
    {
        "id": "continuity_04",
        "section": "continuity",
        "text": "Säkerhetskopieras viktig information och har ni testat att den kan återställas?",
        "help_text": "Backup som aldrig testats kan visa sig vara obrukbar. Det viktiga är inte bara att backup görs utan att den fungerar.",
        "standard": False,
        "profile_tags": ["manages_it_systems", "handles_financial_data"],
    },

    # ── FYSISK SÄKERHET ───────────────────────────────────────────────
    {
        "id": "physical_01",
        "section": "physical",
        "text": "Är tillgången till dina arbetslokaler styrd så att obehöriga inte kommer in?",
        "help_text": "Passerkort, låsta dörrar och besöksrutiner är grundläggande fysisk säkerhet.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "physical_02",
        "section": "physical",
        "text": "Låser du din dator och förvarar känsliga dokument säkert när du lämnar arbetsplatsen?",
        "help_text": "Clean desk-principen innebär att känslig information inte lämnas synlig. Lås datorn med Windows+L.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "physical_03",
        "section": "physical",
        "text": "Är tekniska utrymmen (serverrum, driftcentraler) skyddade mot obehörig åtkomst?",
        "help_text": "Tekniska utrymmen ska ha extra skydd — passerkort, loggning och begränsat antal behöriga.",
        "standard": False,
        "profile_tags": ["manages_it_systems", "handles_building_systems"],
    },
    {
        "id": "physical_04",
        "section": "physical",
        "text": "Hanterar du nycklar, passerkort eller passersystem och finns det rutiner för detta?",
        "help_text": "Nyckelhantering är kritiskt i fastighetsförvaltning — borttappade nycklar kan ge obehörig tillgång till många lägenheter.",
        "standard": False,
        "profile_tags": ["handles_keys_access", "handles_building_systems"],
    },

    # ── PERSONUPPGIFTER OCH GDPR ──────────────────────────────────────
    {
        "id": "gdpr_01",
        "section": "gdpr",
        "text": "Vet du vad en personuppgift är och vilka regler som gäller för hanteringen?",
        "help_text": "En personuppgift är allt som kan kopplas till en levande person — namn, personnummer, adress, telefonnummer, foto, IP-adress m.m.",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "gdpr_02",
        "section": "gdpr",
        "text": "Vet du vilka personuppgifter din enhet hanterar och varför?",
        "help_text": "Varje behandling av personuppgifter ska ha ett tydligt syfte och en laglig grund (t.ex. avtal, samtycke eller rättslig förpliktelse).",
        "standard": True,
        "profile_tags": [],
    },
    {
        "id": "gdpr_03",
        "section": "gdpr",
        "text": "Finns det en registerförteckning över personuppgiftsbehandlingar på din enhet?",
        "help_text": "GDPR kräver att organisationer dokumenterar alla behandlingar av personuppgifter i ett register (artikel 30).",
        "standard": False,
        "profile_tags": ["handles_personal_data", "handles_sensitive_personal_data", "handles_customer_data"],
    },
    {
        "id": "gdpr_04",
        "section": "gdpr",
        "text": "Hanterar din enhet särskilt känsliga personuppgifter (t.ex. hälsa, skyddade identiteter)?",
        "help_text": "Känsliga personuppgifter kräver extra skydd. Bostadssociala enheten hanterar t.ex. skyddade identiteter.",
        "standard": False,
        "profile_tags": ["handles_sensitive_personal_data"],
    },
    {
        "id": "gdpr_05",
        "section": "gdpr",
        "text": "Vet du vad du ska göra om personuppgifter röjs eller hamnar hos obehöriga?",
        "help_text": "En personuppgiftsincident ska rapporteras till dataskyddsombudet och i allvarliga fall till Integritetsskyddsmyndigheten (IMY) inom 72 timmar.",
        "standard": True,
        "profile_tags": [],
    },
]

# ── HFAB units → profile mapping ─────────────────────────────────────
# Each actual HFAB unit maps to exactly one profile.

UNIT_TO_PROFILE: dict[str, str] = {
    "HR": "office_admin",
    "Affärsstöd": "office_admin",
    "Ekonomi och verksamhetsstöd": "office_admin",
    "IT och informationssäkerhet": "it_security",
    "Kommunikation": "office_admin",
    "Bostadssociala": "social_work",
    "Framtidsakademin": "field_operations",
    "Fastighetsutveckling": "property_mgmt",
    "Marknad": "customer_facing",
    "Produkt": "customer_facing",
    "Kundcenter": "customer_facing",
    "Fastighet": "property_mgmt",
    "Fastighetsstab": "property_mgmt",
    "Affärsområden": "property_mgmt",
    "Egen regi": "field_operations",
}

HFAB_UNITS = list(UNIT_TO_PROFILE.keys())

# ── Helper: get questions for a profile ──────────────────────────────

def get_questions_for_profile(profile_key: str) -> list[dict]:
    """Return all questions applicable to a given unit profile."""
    profile = UNIT_PROFILES.get(profile_key)
    if not profile:
        # Unknown profile — return only standard questions
        return [q for q in SURVEY_QUESTIONS if q["standard"]]

    profile_tags = set(profile["tags"])
    result = []
    for q in SURVEY_QUESTIONS:
        if q["standard"]:
            result.append(q)
        elif set(q["profile_tags"]) & profile_tags:  # Any overlap
            result.append(q)
    return result
