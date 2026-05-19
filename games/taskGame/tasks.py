# Each task has:
#   title       -- short name printed in large text on the receipt
#   description -- the rule or challenge text
#   players     -- how many players are picked: 1, 2, N, or "all"
#                  1 targets the drawing player themselves
#   drinks      -- fixed drink amount (int), or None if outcome is open-ended
#   drinkType   -- "take"    drawer takes drinks
#                  "give"    drawer gives drinks to a chosen player
#                  "social"  outcome determined in play, user logs drinks manually
#                  "link"    creates a persistent link between players, no immediate drinks
#                  "special" no drink tracking (ongoing effects)
TASKS = [
    {
        "title": "Juo 3",
        "description": "Juo 3.",
        "players": 1,
        "drinks": 3,
        "drinkType": "take",
    },
    {
        "title": "Jaa 3",
        "description": "Jaa 3 juomaa.",
        "players": 1,
        "drinks": 3,
        "drinkType": "give",
    },
    {
        "title": "Juo 3,6,9...",
        "description": "1. juo 3, 2. juo 6, 3. juo 9 jne.",
        "players": 1,
        "drinks": 3,
        "drinkType": "take",
    },
    {
        "title": "Kuolema",
        "description": "Aloita juomisluuppi. Pelaajat juovat vuorotellen yhtä enemman kuin edellinen, kunnes joku kieltaytyy.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
    },
    {
        "title": "Luuppi",
        "description": "Huuda luuppi, viimeinen joka sanoi 'luuppi' juo 3",
        "players": "all",
        "drinks": 3,
        "drinkType": "social",
    },
    {
        "title": "Riimi",
        "description": "Sano sana. Viimeinen joka ei keksi sanaa joka rimmaa aiemmin sanot sanan kanssa juo 3.",
        "players": 1,
        "drinks": 3,
        "drinkType": "social",
    },
    {
        "title": "Vesiputous",
        "description": "Kaikki alkavat juomaan yhtaikaa. Kukaan ei saa lopettaa ennen kuin oikealla puolella oleva lopettaa.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
    },
    {
        "title": "Kategoria",
        "description": "Valitse kategoria (esim. automerkit). Muut nimeävat kategorian asioita vuorotellen. Joka epäonnistuu tai toistaa, juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "social",
    },
    {
        "title": "Kysymysmestari",
        "description": "Olet kysymysmestari kunnes joku nostaa uuden kysymysmestarikortin. Jokainen joka vastaa kysymykseesi jotain muuta kuin 'haista vittu' juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
    },
    {
        "title": "Säänto",
        "description": "Tee säänto joka pätee pelin loppuun. Säännon rikkoja juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
    },
    {
        "title": "Tauko",
        "description": "Voit poistua pelipöydästä, tai kieltäytyä tehtävästä ilman, että pitää juoda",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
    },
    {
        "title": "Huora",
        "description": "Valitse huora, huora juo aina kun kortin antaja juo",
        "players": 2,
        "drinks": None,
        "drinkType": "link",
    },
    {
        "title": "Kivi-paperi-sakset",
        "description": "Haasta valittu pelaaja kivi-paperi-saksiin. Häviäjä juo 4.",
        "players": 2,
        "drinks": 4,
        "drinkType": "social",
    },
    {
        "title": "Pari",
        "description": "Teette parin. Aina kun toinen juo, toinen juo myös. Kestää kunnes seuraava parikortti nostetaan.",
        "players": 2,
        "drinks": None,
        "drinkType": "link",
    },
    {
        "title": "Tarina",
        "description": "Aloita tarina yhdellä lauseella. Muut jatkavat vuorotellen. Viimeinen joka ei sanonut koko tarinaa oikein juo.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
    },
]
