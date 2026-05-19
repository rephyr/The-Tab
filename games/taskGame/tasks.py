# Each task has:
#   title       -- short name printed in large text on the receipt
#   description -- the rule or challenge text
#   players     -- how many players are picked: 1, 2, N, or "all"
#                  1 targets the drawing player themselves
#   drinks      -- fixed drink amount (int), or None if outcome is open-ended
#   drinkType   -- "take"     drawer takes drinks
#                  "give"     drawer gives drinks to a chosen player
#                  "social"   outcome determined in play, user logs drinks manually
#                  "link"     creates a persistent link between players, no immediate drinks
#                  "special"  no drink tracking (ongoing effects)
#                  "roulette" sequential pulls, guaranteed one hit, stops on first hit
#   count       -- how many copies go into the deck (higher = more common)
TASKS = [
    {
        "title": "Juo 3",
        "description": "Juo 3.",
        "players": 1,
        "drinks": 3,
        "drinkType": "take",
        "count": 4,
    },
    {
        "title": "Jaa 3",
        "description": "Jaa 3 juomaa.",
        "players": 1,
        "drinks": 3,
        "drinkType": "give",
        "count": 4,
    },
    {
        "title": "Juo 3,6,9...",
        "description": "1. juo 3, 2. juo 6, 3. juo 9 jne.",
        "players": 1,
        "drinks": 3,
        "drinkType": "take",
        "count": 4,
    },
    {
        "title": "Kuolema",
        "description": "Aloita juomisluuppi. Pelaajat juovat vuorotellen yhtä enemman kuin edellinen, kunnes joku kieltaytyy.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
        "count": 2,
    },
    {
        "title": "Luuppi",
        "description": "Huuda luuppi, viimeinen joka sanoi 'luuppi' juo 3",
        "players": "all",
        "drinks": 3,
        "drinkType": "social",
        "count": 4,
    },
    {
        "title": "Riimi",
        "description": "Sano sana. Viimeinen joka ei keksi sanaa joka rimmaa aiemmin sanot sanan kanssa juo 3.",
        "players": 1,
        "drinks": 3,
        "drinkType": "social",
        "count": 4,
    },
    {
        "title": "Vesiputous",
        "description": "Kaikki alkavat juomaan yhtäikaa. Kukaan ei saa lopettaa ennen kuin oikealla puolella oleva lopettaa.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
        "count": 4,
    },
    {
        "title": "Kategoria",
        "description": "Valitse kategoria (esim. automerkit). Muut nimeävat kategorian asioita vuorotellen. Joka epäonnistuu tai toistaa, juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "social",
        "count": 4,
    },
    {
        "title": "Kysymysmestari",
        "description": "Olet kysymysmestari kunnes joku nostaa uuden kysymysmestarikortin. Jokainen joka vastaa kysymykseesi jotain muuta kuin 'haista vittu' juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "count": 4,
    },
    {
        "title": "Säänto",
        "description": "Tee säänto joka pätee pelin loppuun. Säännön rikkoja juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "count": 4,
    },
    {
        "title": "Tauko",
        "description": "Voit poistua pelipöydästä, tai kieltäytyä tehtävästä ilman, että pitää juoda",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "count": 3,
    },
    {
        "title": "Huora",
        "description": "Valitse huora, huora juo aina kun kortin antaja juo",
        "players": 2,
        "drinks": None,
        "drinkType": "link",
        "count": 4,
    },
    {
        "title": "Kivi-paperi-sakset",
        "description": "Haasta valittu pelaaja kivi-paperi-saksiin. Häviäjä juo 4.",
        "players": 2,
        "drinks": 4,
        "drinkType": "social",
        "count": 4,
    },
    {
        "title": "Pari",
        "description": "Teette parin. Aina kun toinen juo, toinen juo myös. Kestää kunnes seuraava parikortti nostetaan.",
        "players": 2,
        "drinks": None,
        "drinkType": "link",
        "count": 4,
    },
    {
        "title": "Tarina",
        "description": "Aloita tarina yhdellä lauseella. Muut jatkavat vuorotellen. Viimeinen joka ei sanonut koko tarinaa oikein juo.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
        "count": 4,
    },
    {
        "title": "Venäläinen ruletti",
        "description": "Jokainen vetää liipaisinta vuorollaan. Osuma: juo 10. Todennäköisyys 1/pelaajamäärä.",
        "players": "all",
        "drinks": 10,
        "drinkType": "roulette",
        "count": 2,
    },
]
