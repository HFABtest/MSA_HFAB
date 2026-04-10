"""
Fixed reference data for the Mognadsdialog model (MSB/MCF).

These are NOT configurable — they define the model itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Perspective:
    key: str
    name_sv: str
    name_en: str
    description_sv: str


@dataclass(frozen=True)
class Dimension:
    key: str
    name_sv: str
    name_en: str
    description_sv: str


@dataclass(frozen=True)
class MaturityLevel:
    level: int
    name_sv: str
    name_en: str
    description_sv: str


# ── Six fixed perspectives ──────────────────────────────────────────

PERSPECTIVES: list[Perspective] = [
    Perspective(
        key="risk_management",
        name_sv="Riskhantering",
        name_en="Risk Management",
        description_sv="Hur organisationen identifierar, analyserar och hanterar informationssäkerhetsrisker.",
    ),
    Perspective(
        key="information_classification",
        name_sv="Informationsklassning",
        name_en="Information Classification",
        description_sv="Hur organisationen klassificerar och skyddar sin information.",
    ),
    Perspective(
        key="incident_management",
        name_sv="Incidenthantering",
        name_en="Incident Management",
        description_sv="Hur organisationen förebygger, upptäcker och hanterar incidenter.",
    ),
    Perspective(
        key="procurement",
        name_sv="Anskaffning",
        name_en="Procurement",
        description_sv="Hur informationssäkerhet beaktas vid anskaffning av varor och tjänster.",
    ),
    Perspective(
        key="competence",
        name_sv="Kompetens",
        name_en="Competence",
        description_sv="Hur organisationen säkerställer rätt kompetens inom informationssäkerhet.",
    ),
    Perspective(
        key="follow_up",
        name_sv="Uppföljning",
        name_en="Follow-up",
        description_sv="Hur organisationen följer upp sitt informationssäkerhetsarbete.",
    ),
]

# ── Four fixed dimensions (same for every perspective) ──────────────

DIMENSIONS: list[Dimension] = [
    Dimension(
        key="ways_of_working",
        name_sv="Arbetssätt",
        name_en="Ways of Working",
        description_sv="Finns det definierade processer, rutiner och riktlinjer?",
    ),
    Dimension(
        key="application",
        name_sv="Tillämpning",
        name_en="Application",
        description_sv="Tillämpas arbetssätten i praktiken och i vilken omfattning?",
    ),
    Dimension(
        key="results",
        name_sv="Resultat",
        name_en="Results",
        description_sv="Vilka resultat uppnås och hur mäts de?",
    ),
    Dimension(
        key="follow_up_learn_improve",
        name_sv="Följa upp, lära och förbättra",
        name_en="Follow-up, Learn and Improve",
        description_sv="Hur följs arbetet upp och hur används lärdomar för förbättring?",
    ),
]

# ── Four maturity levels ────────────────────────────────────────────

MATURITY_LEVELS: list[MaturityLevel] = [
    MaturityLevel(
        level=1,
        name_sv="Nivå 1 – Ej etablerat",
        name_en="Level 1 – Not established",
        description_sv="Låg medvetenhet. Arbetet sker ad hoc utan systematik.",
    ),
    MaturityLevel(
        level=2,
        name_sv="Nivå 2 – Påbörjat",
        name_en="Level 2 – Emerging",
        description_sv="Viss medvetenhet finns. Systematik börjar växa fram.",
    ),
    MaturityLevel(
        level=3,
        name_sv="Nivå 3 – Etablerat",
        name_en="Level 3 – Established",
        description_sv="Etablerat och systematiskt. Kontinuerlig förbättring pågår.",
    ),
    MaturityLevel(
        level=4,
        name_sv="Nivå 4 – Föredömligt",
        name_en="Level 4 – Proactive/Exemplary",
        description_sv="Proaktivt, resilient och med framstående resultat.",
    ),
]

# ── Dialogue prompt questions per dimension (guidance for facilitator) ──

DIMENSION_PROMPTS: dict[str, list[str]] = {
    "ways_of_working": [
        "Finns det dokumenterade processer och rutiner?",
        "Är roller och ansvar tydligt definierade?",
        "Finns det policyer och riktlinjer som stödjer arbetet?",
    ],
    "application": [
        "I vilken utsträckning tillämpas de definierade arbetssätten?",
        "Är tillämpningen konsekvent över hela organisationen?",
        "Finns det undantag eller områden där tillämpningen brister?",
    ],
    "results": [
        "Vilka konkreta resultat kan organisationen visa upp?",
        "Hur mäts och följs resultaten upp?",
        "Finns det trender som visar förbättring eller försämring?",
    ],
    "follow_up_learn_improve": [
        "Hur följs arbetet upp systematiskt?",
        "Hur tas lärdomar tillvara och sprids i organisationen?",
        "Leder uppföljningen till konkreta förbättringsåtgärder?",
    ],
}

# ── Next-level guidance (directional, not prescriptive) ─────────────
# Key: (perspective_key, current_level) → list of guidance strings
# These describe what is typically needed to move FROM current_level TO current_level+1.
# They are conversation starters, NOT checklists.

NEXT_LEVEL_GUIDANCE: dict[tuple[str, int], list[str]] = {
    # Risk Management
    ("risk_management", 1): [
        "Börja med att identifiera vilka informationstillgångar som finns och vilka risker de utsätts för.",
        "Etablera en enkel process för riskidentifiering, även om den inte är heltäckande.",
        "Utse en ansvarig för att driva riskhanteringsarbetet framåt.",
    ],
    ("risk_management", 2): [
        "Formalisera riskhanteringsprocessen med dokumenterade rutiner och tydliga roller.",
        "Integrera riskbedömningar i verksamhetsplanering och beslut.",
        "Säkerställ att riskbedömningar genomförs regelbundet, inte bara vid behov.",
    ],
    ("risk_management", 3): [
        "Utveckla proaktiva metoder för att identifiera nya och framväxande risker.",
        "Koppla riskhanteringen till strategisk planering och omvärldsbevakning.",
        "Dela erfarenheter och lärdomar systematiskt mellan verksamhetsdelar.",
    ],

    # Information Classification
    ("information_classification", 1): [
        "Skapa en grundläggande klassningsmodell med tydliga nivåer.",
        "Börja med att klassificera de mest kritiska informationstillgångarna.",
        "Kommunicera varför klassning behövs och vad det innebär i praktiken.",
    ],
    ("information_classification", 2): [
        "Utvidga klassningen till att omfatta alla väsentliga informationstillgångar.",
        "Säkerställ att klassningen faktiskt styr hanteringen av informationen.",
        "Inför regelbunden översyn av gjorda klassningar.",
    ],
    ("information_classification", 3): [
        "Integrera klassningsprocessen i verksamhetens alla led och systemstöd.",
        "Utveckla automatiserade kontroller som säkerställer att klassning efterlevs.",
        "Använd klassningsdata proaktivt för att förutse och förebygga risker.",
    ],

    # Incident Management
    ("incident_management", 1): [
        "Etablera en enkel rapporteringsväg för incidenter.",
        "Definiera vad som räknas som en incident i er verksamhet.",
        "Utse någon som tar emot och samordnar hanteringen av rapporterade incidenter.",
    ],
    ("incident_management", 2): [
        "Dokumentera en formell incidenthanteringsprocess med eskaleringsvägar.",
        "Inför uppföljning och analys av inträffade incidenter.",
        "Genomför övningar för att testa incidenthanteringen.",
    ],
    ("incident_management", 3): [
        "Utveckla prediktiva förmågor – identifiera mönster innan de blir incidenter.",
        "Automatisera delar av detektions- och hanteringsprocessen.",
        "Dela lärdomar strukturerat med andra organisationer eller sektorer.",
    ],

    # Procurement
    ("procurement", 1): [
        "Identifiera vilka upphandlingar och avtal som har informationssäkerhetsrelevans.",
        "Börja ställa grundläggande säkerhetskrav i nya upphandlingar.",
        "Involvera informationssäkerhetskompetens tidigt i anskaffningsprocesser.",
    ],
    ("procurement", 2): [
        "Standardisera säkerhetskrav i upphandlingsmallar och avtal.",
        "Inför uppföljning av att leverantörer uppfyller ställda säkerhetskrav.",
        "Säkerställ att riskbedömning genomförs vid alla väsentliga anskaffningar.",
    ],
    ("procurement", 3): [
        "Integrera leverantörsuppföljning i den löpande riskhanteringen.",
        "Utveckla samarbetsformer med leverantörer för gemensam säkerhetshöjning.",
        "Proaktivt identifiera leverantörskedjans risker och beroenden.",
    ],

    # Competence
    ("competence", 1): [
        "Kartlägg vilken informationssäkerhetskompetens som finns och vad som saknas.",
        "Genomför grundläggande medvetandehöjning för alla medarbetare.",
        "Identifiera nyckelroller som behöver fördjupad kompetens.",
    ],
    ("competence", 2): [
        "Upprätta en utbildningsplan kopplad till roller och ansvar.",
        "Mät och följ upp kompetensutvecklingens effekt.",
        "Säkerställ att ny personal får introduktion i informationssäkerhet.",
    ],
    ("competence", 3): [
        "Integrera informationssäkerhetskompetens i karriärutveckling och befattningsbeskrivningar.",
        "Utveckla interna experter som kan driva kunskapsspridning.",
        "Skapa en lärande kultur där medarbetare aktivt delar erfarenheter.",
    ],

    # Follow-up
    ("follow_up", 1): [
        "Bestäm vad som ska följas upp och hur ofta.",
        "Samla in grunddata om nuläget som kan jämföras över tid.",
        "Rapportera resultat till ledningen, även om underlaget är begränsat.",
    ],
    ("follow_up", 2): [
        "Formalisera uppföljningsprocessen med definierade nyckeltal.",
        "Koppla uppföljningsresultat till förbättringsåtgärder.",
        "Säkerställ att uppföljning sker regelbundet och systematiskt.",
    ],
    ("follow_up", 3): [
        "Använd uppföljningsdata proaktivt för strategiska beslut.",
        "Benchmarka mot tidigare perioder för att visa utvecklingstrender.",
        "Integrera informationssäkerhetsuppföljning med övrig verksamhetsuppföljning.",
    ],
}

# ── Lookup helpers ──────────────────────────────────────────────────

PERSPECTIVE_KEYS = [p.key for p in PERSPECTIVES]
DIMENSION_KEYS = [d.key for d in DIMENSIONS]

PERSPECTIVE_BY_KEY = {p.key: p for p in PERSPECTIVES}
DIMENSION_BY_KEY = {d.key: d for d in DIMENSIONS}
MATURITY_BY_LEVEL = {m.level: m for m in MATURITY_LEVELS}
