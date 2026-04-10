"""
MCF Mognadsdialog – Complete maturity descriptions.

Source: MSB workshopmaterial-mognadsdialogen.pdf (MSB1996, juni 2022)

Structure:
  PERSPECTIVE_MATURITY[perspective_key][dimension_key][level] = description text
  PERSPECTIVE_CULTURE[perspective_key][level] = culture/characteristic label
  PERSPECTIVE_SUBPROCESSES[perspective_key] = list of subprocess dicts
"""

# ── Subprocess definitions per perspective ────────────────────────────

PERSPECTIVE_SUBPROCESSES: dict[str, list[dict]] = {
    "risk_management": [
        {"name": "Identifiera", "description": "Upptäcka och kartlägga eller beskriva risker"},
        {"name": "Analys/Bedöma", "description": "När riskanalyser? Risknivåer, kriterier. Ansvar och roller. Jämför riskkriterier för att avgöra om risken kan förändras eller accepteras"},
        {"name": "Riskbehandla", "description": "Beslut om att förändra eller acceptera risken"},
        {"name": "Övervaka", "description": "Uppföljning av enskild riskanalys. Roll – riskägare"},
        {"name": "Riskuppföljning", "description": "Verksamhetens övergripande bild över risker. Riskregister"},
    ],
    "information_classification": [
        {"name": "Identifiera informationstillgångar", "description": "Vilken information finns och var"},
        {"name": "Värdera och klassa", "description": "Informationsklassningsmodell. Värdera och klassa information och systemstöd. Konsekvensbedöma: Konfidentialitet, Riktighet, Tillgänglighet"},
        {"name": "Ge rätt skydd utifrån klassning", "description": "Riskbedömning. Krav på säkerhetsåtgärder. Införa säkerhetsåtgärder"},
        {"name": "Uppföljning", "description": "Ges informationen adekvat skydd. Resultat av säkerhetsåtgärder"},
        {"name": "Omvärdera/omklassa", "description": "Förändra skyddet, säkerhetsåtgärder"},
    ],
    "incident_management": [
        {"name": "Upptäcka", "description": "Identifiera händelse. Rapportera"},
        {"name": "Hantera", "description": "Bedöma. Åtgärda och hantera konsekvenser. Eskalera. Kommunicera till berörda"},
        {"name": "Utreda", "description": "Fastställa grundorsaker. Bedöma. Föreslå förbättring"},
        {"name": "Förbättra", "description": "Prioritera och genomföra förbättring. Kommunicera förändringen. Följa upp förändringen"},
    ],
    "procurement": [
        {"name": "Förbereda", "description": "Planera. Behov. Risker. Infosäkkrav"},
        {"name": "Upphandla", "description": "Utvärdera anbud. Tilldela avtal"},
        {"name": "Realisera", "description": "Starta samarbetet. Kommunicera"},
        {"name": "Förvalta", "description": "Uppföljning av krav och avtal"},
    ],
    "competence": [
        {"name": "Behov", "description": "Inventering av risker. Kompetensbehov"},
        {"name": "Utforma", "description": "Prioritera behov. Metodval. Skapa utbildning, övning, träning"},
        {"name": "Utbilda", "description": "Organisera. Genomföra"},
        {"name": "Utvärdera", "description": "Resultat. Utbildningseffekt"},
    ],
    "follow_up": [
        {"name": "Behov", "description": "Vilka processer och arbetssätt bör följas upp utifrån risk och mål? Hur? Vad? När?"},
        {"name": "Planera", "description": "Resurser/utbilda. Utforma underlag. Utforma detaljerad plan. Kommunicera"},
        {"name": "Genomföra", "description": "Genomföra planen. Resurser, kompetens. Samla in information, efterarbete, dokumentera"},
        {"name": "Följa upp", "description": "Sammanställa resultat, erfarenheter. Analysera resultatet. Rapportera och kommunicera resultaten till berörda/ledning"},
        {"name": "Förbättra", "description": "Analysera processens alla delar och förbättra. Beslut om ev justera och förbättra arbetssätten"},
    ],
}

# ── Culture/characteristic labels per perspective per level ───────────

PERSPECTIVE_CULTURE: dict[str, dict[int, str]] = {
    "risk_management": {
        1: "Saknar förståelse för risker",
        2: "Oj, mer jobb",
        3: "Fångar risken…",
        4: "Letar risker = förbättringsmöjlighet",
    },
    "information_classification": {
        1: "Information, vad då?",
        2: "Informationen behöver skyddas",
        3: "Informationen är värdefull",
        4: "Styr verksamheten utifrån info om tillgångarnas värde",
    },
    "incident_management": {
        1: "Snabba lösningar premieras",
        2: "Få inrapporterade = bra",
        3: "Uppmuntrar att rapportera",
        4: "Letar ständigt efter",
    },
    "procurement": {
        1: "Naiv",
        2: "Godtrogen",
        3: "Kravställare",
        4: "Dialog med leverantör",
    },
    "competence": {
        1: "Okunnig",
        2: "Informerad",
        3: "Engagerad",
        4: "Motiverad",
    },
    "follow_up": {
        1: "Utan spaning ingen aning",
        2: "Göra saker",
        3: "Göra rätt saker",
        4: "Göra rätt saker på rätt sätt",
    },
}

# ── Maturity descriptions: [perspective][dimension][level] ───────────

PERSPECTIVE_MATURITY: dict[str, dict[str, dict[int, str]]] = {

    # ── RISKHANTERING ─────────────────────────────────────────────────
    "risk_management": {
        "ways_of_working": {
            1: "Saknar i huvudsak medvetet valda arbetssätt inom riskhantering – identifiering, analys, behandling, övervakning, riskuppföljning.",
            2: "Har medvetet valt arbetssätt och metod för riskanalys, men saknar i övrigt samordning inom riskhantering. Har risknivåer men nivåerna är inte tydliga vad de innebär i praktiken.",
            3: "Har tydliga och samordnade arbetssätt inom riskhantering. Risknivåerna är tydliga och begripliga. Tydliga arbetssätt för hur risker och åtgärder ska följas upp.",
            4: "Har logiska och väl samordnade arbetssätt inom riskhantering. Risknivåerna är tydliga och stödjer verksamheten.",
        },
        "application": {
            1: "Hanterar risker reaktivt, ad hoc. Dokumenterar sällan med en gemensam metod. Resonerar om risker när nåt har hänt. Åtgärder genomförs utifrån \"köper in\", men överväger inte om investeringen är rätt. Känslomässiga beslut dominerar.",
            2: "Riskanalyser görs i begränsad omfattning. Få efterfrågar riskanalyser. Oklart NÄR de ska göras. Enstaka personer har kompetens att leda riskanalyser. Ledningen har låg insikt om riskhantering. Beslutar att åtgärda risker utifrån begränsat beslutsunderlag och beslut saknas när risker accepteras.",
            3: "Arbetssätten används i de flesta relevanta processerna och situationer. Riskanalyser görs ofta och medvetet. Det är tydligt när riskanalyser ska göras. Flera personer har kompetens att leda riskanalyser. Ledningen har god insikt om riskhantering. Beslutar om åtgärder utifrån resultatet av riskanalysen. Beslut att acceptera risker tas medvetet och motiveras. Följer upp de flesta riskanalyser över tid och att åtgärder får avsedd effekt.",
            4: "Arbetssätten används i alla relevanta processer och situationer. Säkerställer kompetensen. Hög riskkompetens hos alla. Ledningen är pådrivande inom riskhantering. Använder riskanalysernas resultat för att införa åtgärder som får avsedd effekt i enlighet med fastställda mål. Beslutar om åtgärder eller riskacceptans görs utifrån fakta.",
        },
        "results": {
            1: "Saknar mål med riskhanteringen. Inga resultat samlas in och jämförs över tid.",
            2: "Enstaka mål med riskhanteringen. Svag koppling mellan riskanalys och resultat.",
            3: "Några mål finns avseende riskhanteringen och några relevanta resultat samlas in för området. Enstaka resultat som följs över tid.",
            4: "Flera relevanta resultat som visar positiva trender. Ex riskutveckling över tid, påverkat sårbarheter.",
        },
        "follow_up_learn_improve": {
            1: "Har hänt att man pratat om hur man arbetar men brister i att omsätta det till lärande och förbättring.",
            2: "Följer upp och förbättrar arbetssättet för riskanalys. Tar inte lärdom, återanvänder inte genomförda riskanalyser. Saknar överblick över alla analyserade risker.",
            3: "Börjar styra infosäkarbetet utifrån risker. Tar lärdom av genomförda analyserade risker. Sammanställer alla genomförda riskanalyser och följer upp dem över tid. Utvärderar och förbättrar arbetssätten regelbundet.",
            4: "Proaktivt arbete. Styr infosäkarbetet utifrån risk. Följer noga riskbilden över tid. Utvärderar och förbättrar arbetssätten och riskmetoder i syfte att skapa än bättre effektivitet.",
        },
    },

    # ── INFORMATIONSKLASSNING ─────────────────────────────────────────
    "information_classification": {
        "ways_of_working": {
            1: "Saknar medvetet valda arbetssätt för att identifiera och värdera information. Enstaka arbetssätt finns men hänger inte ihop, värderar inte informationen.",
            2: "Har några medvetet valda arbetssätt för att identifiera, värdera information samt att införa säkerhetsåtgärder. De är inte samordnade. Har klassningsmodell men nivåerna är inte tydliga vad de innebär i praktiken.",
            3: "Har flera medvetet valda arbetssätt för att identifiera, värdera information samt införa säkerhetsåtgärder som är samordnade. Klassningsmodellen har tydliga kriterier och nivåer som värderingen ska göras utifrån.",
            4: "Har genomtänkta medvetet valda arbetssätt för att identifiera, värdera info tillgångar, som är väl samordnade och logiska.",
        },
        "application": {
            1: "Medvetenhet finns om att informationen måste hanteras utifrån olika lagkrav. Värderingen av information har fokus på it-systemen. Betoning på konfidentialitet. It anses var ansvarig för informationen.",
            2: "Använder klassningsmodellen i liten skala eller har påbörjat arbetet där behov uppstår. Stort personberoende. Klassningen styr inte alltid val av säkerhetsåtgärder. Betoning på konfidentialitet och tillgänglighet. Ansvaret för informationen utgår delvis från informationsägarens krav.",
            3: "Använder klassningsmodellen i de flesta relevanta processerna. Klassning och risk styr val av säkerhetsåtgärder. Arbetssätten är kända och efterfrågas. Verksamheten har ansvar för informationen och kraven utgår från informationsägaren. Medvetenhet finns på de tre aspekterna KRT.",
            4: "Använder alla arbetssätten strukturerat i alla relevanta processer. Utgår från informationsägarens krav som utgår från organisationens mål. Beslutar om säkerhetsåtgärder och förändrar skydd vid behov. Omklassning sker vid externa förändringar (lagkrav) eller vid förändringar i info tillgångar (tillägg borttag). God balans mellan de tre aspekterna KRT.",
        },
        "results": {
            1: "Svag koppling mellan säkerhetsåtgärder (i praktiken) och informationens värde. Mål saknas.",
            2: "Har identifierat, värderat information i liten omfattning. Införda säkerhetsåtgärder har viss koppling till resultatet av klassningen. Enstaka mål finns.",
            3: "Har tydliga mål och plan att all information ska värderas. Har identifierat, värderat huvuddelen av informationstillgångarna. Införda säkerhetsåtgärder har stark koppling till resultatet av klassningen.",
            4: "Införda säkerhetsåtgärder stödjer uthålligt verksamhetens mål. Säkerhetsnivåerna kan härledas till konsekvensnivåer.",
        },
        "follow_up_learn_improve": {
            1: "Pratas mycket och man är frustrerad. Har hänt att man följt upp som kan leda till enstaka lärande och förbättring.",
            2: "Förbättrar arbetssätten så att metoden för värderingen av informationen kan ske effektivare. Införda säkerhetsåtgärder utvärderas sporadiskt med fokus på följsamhet till rutinen.",
            3: "Förbättrar kriterier och nivåer för värdering av information utifrån organisationens behov. Delvis systematiskt uppföljning av säkerhetsåtgärdernas ändamålsenlighet.",
            4: "Förbättrar kriterier och nivåer utifrån förändrade krav och förutsättningar på både kort och lång sikt. Systematisk uppföljning och av säkerhetsåtgärdernas ändamålsenlighet, tillämplighet och effektivitet kopplat till verksamhetens mål.",
        },
    },

    # ── INCIDENTHANTERING ─────────────────────────────────────────────
    "incident_management": {
        "ways_of_working": {
            1: "Saknar tydliga arbetssätt för att rapportera eller hantera inrapporterade incidenter och utreda dessa.",
            2: "Har tydliga arbetssätt för hur incidenter ska rapporteras och åtgärdas.",
            3: "Tydliga logiska arbetssätt. Hög medvetenhet om betydelsen av att fånga upp och utreda incidenter.",
            4: "Tydliga logiska väl samordnade arbetssätt. Hög medvetenhet om betydelsen av att fånga upp incidenter, utreda och följa upp att åtgärderna får avsedd effekt.",
        },
        "application": {
            1: "Rapporterar incidenter utifrån personligt engagemang. Resonerar om incidenter när nåt hänt.",
            2: "Otydligt vad som ÄR en incident, dvs viktiga incidenter rapporteras inte alltid. Analyserar inte grundorsakerna till incidenter utan tar enklaste lösningen (kategorin styr).",
            3: "Många rapporterar incidenter. Uppmuntrar alla att hitta och rapportera. Börjar analysera grundorsaken till de flesta incidenter för att hitta samband och orsaker inom infosäk. Åtgärdar oftast grundorsaken.",
            4: "Alla rapporterar incidenter och även riskhändelser. Lyhörd och ser samband. Analyserar grundorsaker genom att samla rätt kompetens. Åtgärdar alltid grundorsaken.",
        },
        "results": {
            1: "Negativa händelser upprepas lätt eftersom överblick saknas. Incidenter upprepas. Få incidenter rapporteras vilket tolkas positivt.",
            2: "Svag koppling mellan incidenter och minskad risk för upprepning. Mäter antalet incidenter. Ofta frustration av att infosäk inte fångas upp via andra rapporterade avvikelser.",
            3: "Flera resultat finns om effektiv hantering. Mäter och börjar prioritera incidenter inom viktiga riskområden med behov av förbättring.",
            4: "Använder incidenter proaktivt, följer upp åtgärder så att de stödjer verksamhetens mål. Kan visa positiva resultat och trender. Leder till handling och riskhantering.",
        },
        "follow_up_learn_improve": {
            1: "Utreder inte utan löser snabbt och \"köper in\", utan att veta det blir rätt.",
            2: "Man löser \"problemet\". Följer upp antalet rapporter och prioriterar uppmuntrar att rapportera fler. Har mindre fokus på att skapa effektiv hantering.",
            3: "Följer upp flera incidenter så att de inte ska upprepas. Analyserar inte andra rapporterade incidenter för att hitta infosäkrisker. Analyserar incidenterhanteringen för att öka effektiviteten och förbättringsmöjligheter tas tillvara.",
            4: "Analyserar andra kategorier av avvikelser för att hitta infosäkrisker. Fokus på förbättringar av processen. Analyserar och förbättrar ständigt A/I hanteringen så att förbättringsmöjligheter tas tillvara i förhållande till verksamhets behov.",
        },
    },

    # ── UPPHANDLING ───────────────────────────────────────────────────
    "procurement": {
        "ways_of_working": {
            1: "Saknar arbetssätt för att ställa krav på informationssäkerhet vid upphandlingar.",
            2: "Har beslutade arbetssätt om hur upphandlingsprocessen ska ske, men otydligt hur/när infosäk ska beaktas. Enstaka krav ställs på infosäk under avtalsperioden.",
            3: "Tydliga arbetssätt för hur infosäk ska beaktas i upphandlingsprocessen och under avtalsperioden.",
            4: "Tydliga arbetssätt för hur infosäk ska beaktas i upphandlingsprocessen. Har standardiserade krav som ger stöd i hela processen.",
        },
        "application": {
            1: "Ad hoc, den som skriker högst medverkar i upphandlingsprocessen. Har huvudsakligen fokus på kostnader.",
            2: "Infosäk medverkar i inledningsskedet och vissa säkerhetskrav tas fram. Ställer några infosäkkrav i avtalen med leverantören. Uppföljning av leverantörer görs huvudsakligen på SLA/tillgänglighet.",
            3: "Infosäkkompetens medverkar vid större upphandlingar i hela processen. Ställer krav på leverantören både avseende informationssäkerhetsarbete och på enskilda säkerhetsåtgärder och på säkerhetsarkitektur. Leverantörer följs upp och att arbetssätten tillämpas i de flesta upphandlingar/avtal.",
            4: "Infosäkkompetens säkerställs i upphandlingsprocessens alla relevanta processer och situationer. Tillämpar standardiserade arbetssätt för uppföljning av leverantören utifrån risker.",
        },
        "results": {
            1: "Har inte några krav på uppföljning i avtalen. Saknar mål och resultat.",
            2: "Bevis saknas att informationen skyddas tillräckligt. Leverantörens egen uppföljning kan rapporteras in som bevis exempelvis it-incidenter och SLA. Enstaka mål.",
            3: "Flera bevis finns för att leverantören skyddar informationen tillräckligt enligt KRT. Det innebär att beställaren eller tredje part följer upp leverantören uppfyller ställda krav. Några mål finns.",
            4: "Bevis finns att leveranserna i avtalen bidrar till verksamhetens mål. Nya risker hanteras och följs upp över tid.",
        },
        "follow_up_learn_improve": {
            1: "Har hänt att man följer upp arbetssätten. Svårt att omsätta till lärande och förbättring.",
            2: "Följer upp enstaka genomförda upphandlingar för att förbättra processen. Viss dialog om hur leverantörens uppföljning kan förbättras.",
            3: "Följer upp resultat av enstaka tjänster. Identifierar nya risker. Förbättrar arbetssätten för hela upphandlingsprocessen för att bli en bättre beställare.",
            4: "Följer upp resultat, nya risker hanteras och förbättrar ständigt utifrån info säkerhet. Utvärderar genomförda upphandlingar, lär och förbättrar processen.",
        },
    },

    # ── KOMPETENS ─────────────────────────────────────────────────────
    "competence": {
        "ways_of_working": {
            1: "Inga utbildningar finns framtagna. Köper in.",
            2: "Enstaka arbetssätt för utbildning och träning finns.",
            3: "Mestadels genomtänkta arbetssätt för att utbilda olika målgrupper. I huvudsak logiska och samordnade ex utgår i huvudsak från verksamhetens krav och behov.",
            4: "Arbetssätten för utbildning och träning sker enligt plan och utifrån identifierade behov.",
        },
        "application": {
            1: "Informerar om viktiga områden vid behov. Enstaka utbildningar genomförs, köps in.",
            2: "Insikt finns om utbildningsbehov. Enkla standardutbildning genomförs ex nyanställda. Utbildningsplanen följs inte eller ändras ofta. Få personer kan utbilda.",
            3: "Genomför olika standardutbildningar regelbundet enligt plan. Använder olika former för eller metoder kompetenshöjande insatser. Flera kan utbilda.",
            4: "Olika metoder för kompetensutveckling används. Utbildning och träning genomförs i alla relevanta processer. Inget personberoende.",
        },
        "results": {
            1: "Nöjd med att utbildningen är genomförd.",
            2: "Effekten är oklar. Resultaten har fokus på antalet att utbildningstillfällen ökar.",
            3: "Resultaten har fokus på att mäta antal deltagande, målgrupper. Enstaka resultat finns på effekt.",
            4: "Mäter och följer upp både deltagande och effekt. Positiva trender och ökad säkerhet i verksamheten.",
        },
        "follow_up_learn_improve": {
            1: "Pratar, vi borde göra detta regelbundet.",
            2: "Följer upp hur utbildningarnas praktiska delar, för att underlätta att flera ska gå utbildningen.",
            3: "Följer upp och analyserar utbildningsprocessen utifrån målgruppernas synpunkter och behov. Förbättrar genomförs för att öka utbildningseffekt.",
            4: "Följer upp och förbättrar utbildningsprocessen utifrån verksamhetens behov och för att nå målen.",
        },
    },

    # ── UPPFÖLJNING ───────────────────────────────────────────────────
    "follow_up": {
        "ways_of_working": {
            1: "Saknar arbetssätt för uppföljning förutom enstaka viktiga egenkontroller.",
            2: "Några olika arbetssätt för uppföljning finns men de brister i samordning och systematik. Har enstaka planer för uppföljning.",
            3: "Medvetet valda arbetssätt uppföljning finns som delvis stödjer verksamhetens utveckling. Utgår inte fullt från risker/behov/krav.",
            4: "Tydlig medvetet valda arbetssätt för uppföljning. De är väl samordnade och stödjer verksamhetens mål. De utgår från risker/behov/krav.",
        },
        "application": {
            1: "Enstaka egenkontroller genomförs. I övrigt utifrån egna personers initiativ. Granskningar köps in eller genomförs av en=personberoende.",
            2: "Planerna genomförs inte alltid. Enstaka internrevisioner, eller granskningar görs, men brister i efterarbetet. Kompetens och resursbrist.",
            3: "Genomför planerad uppföljning, ex internrevisioner och använder och analyserar resultatet. Ledningen efterfrågar info. Högt engagemang. Planerar för resurser.",
            4: "Uppföljning sker på alla nivåer och processer av vikt. Delaktig och drivande ledning. Kompetens och resurser planeras.",
        },
        "results": {
            1: "Enstaka rapporter kan sammanställas men inga specifika resultat finns.",
            2: "Enstaka resultat sammanställs men oklart om resultatet ger bättre informationssäkerhet. Har fokus på att vi GÖR uppföljning och följa planen.",
            3: "Uppföljningen visar flera resultat, enstaka positiva resultat, men oklart om de stödjer verksamhetens mål. Har fokus på har vi fått med allt i uppföljningen?! Uppföljningen visar flera bevis på hur infosäkarbetet går på olika nivåer.",
            4: "Uppföljningen visar flertalet positiva resultat över tid. Uppföljningen visar flera bevis på hur infosäkarbetet utvecklas och att det stödjer verksamhetens mål.",
        },
        "follow_up_learn_improve": {
            1: "Egenkontroller diskuteras och större problem fixas till på enklaste sätt.",
            2: "Följer upp några arbetssätten vissa resultat av uppföljningen som leder till enstaka förbättringar.",
            3: "Arbetssätten för uppföljning följs huvudsakligen upp och förbättringar/justeringar görs delvis utifrån verksamhetens behov risker.",
            4: "Arbetssätten för uppföljning följa upp och justeras agilt=snabba reaktioner, utifrån verksamhetens utveckling, risker, mål- och handlingsplaner. Förbättringar görs för att effektivisera uppföljningen.",
        },
    },
}

# ── Generic maturity level descriptions (slide 10) ───────────────────

GENERIC_MATURITY: dict[str, dict[int, str]] = {
    "ways_of_working": {
        1: "Saknar i huvudsak gemensamma medvetet valda arbetssätt inom området. Lösryckte arbetssätt finns men ofta otydliga, okända eller hänger inte ihop. Låg insikt om behov av struktur inom området.",
        2: "Några gemensamma, medvetet valda arbetssätt inom området. Arbetssätten hänger inte alltid ihop (samordnade). Insikt om behov av struktur och systematik finns.",
        3: "Flera gemensamma, medvetet valda arbetssätt. Arbetssätten hänger ihop (samordnade). Bygger struktur och systematik. Roller och ansvar finns. Högt driv för struktur och systematik.",
        4: "Genomtänka, medvetet valda, väl samordnade arbetssätt inom området. Mycket systematiska och proaktiva. Arbetssätten utgår tydligt från intressenternas krav, behov och förväntningar. Roller och ansvar är adekvata och fungerar väl.",
    },
    "application": {
        1: "Var och en arbetar efter eget huvud och situationen styr. Vissa arbetssätt tillämpas sporadiskt.",
        2: "Arbetssätten används i begränsad omfattning, dvs inte i alla relevanta processer och situationer. Arbetssätt kan nyligen ha införts eller håller på att införas. Inte kända hos alla.",
        3: "Arbetssätten är kända. Arbetssätten används i god omfattning i de flera relevanta processer/situationer.",
        4: "Arbetssätten är välkända, används i alla relevanta processer/situationer.",
    },
    "results": {
        1: "Inga långsiktiga resultat samlas in, eller jämförs över tid. Enstaka resultat och ekonomiresultat har fokus. Saknar mål.",
        2: "Enstaka resultat samlas in och jämförs över tid men hänger ofta inte ihop med formulerade mål. Enstaka goda resultat. Resultaten kan sällan härledas till arbetssätten.",
        3: "Flertalet resultat samlas in och jämförs över tid. Vissa uthålliga positiva resultat, vilka kan kopplas till formulerade mål. Jämför inte resultat med andra. Viss osäkerhet om resultat kan härledas till arbetssätten.",
        4: "Flera relevanta resultat som visar positiva trender kopplade till formulerade mål. Positiva, uthålliga resultat, även i jämförelse med andra organisationer. Resultat kan tydligt härledas till arbetssätten. Resultatfokus.",
    },
    "follow_up_learn_improve": {
        1: "Reaktiv. Fokus på problemlösning och korrigerande åtgärder. Saknar insikt, men pratar OM uppföljning. Följer inte upp, utvärderar och lär inte över tid.",
        2: "Enstaka arbetssätt och processer följs upp, resultat (mest tillämpning) analyseras. Förbättringar sker ofta ad hoc eller genomförs inte systematiskt. Börjar få insikt – driver på samverkan och teamarbete.",
        3: "Flera arbetssätt/processer följs upp, resultaten (mest ändamålsenlighet) analyseras och leder till förbättringar. Viss osäkerhet om orsak och verkan. Lärande börjar få fokus för förbättringar. Hög insikt, nyfikenhet och ifrågasättande.",
        4: "Proaktiv. Relevanta arbetssätt/processer följs upp, analyseras och förbättringar sker, metodiskt och agilt utifrån att öka effektivitet. Högt fokus på lärande i hela organisationen.",
    },
}
