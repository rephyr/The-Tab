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
#   rarity      -- "common"  appears commonCount times per deck (set in config)
#                  "special" appears specialCount times per deck (set in config)
TASKS = [
    {
        "title": "Juo 3",
        "description": "Juo 3.",
        "players": 1,
        "drinks": 3,
        "drinkType": "take",
        "rarity": "common",
    },
    {
        "title": "Jaa 3",
        "description": "Jaa 3 juomaa.",
        "players": 1,
        "drinks": 3,
        "drinkType": "give",
        "rarity": "common",
    },
    {
        "title": "Juo 3,6,9...",
        "description": "1. juo 3, 2. juo 6, 3. juo 9 jne.",
        "players": 1,
        "drinks": 3,
        "drinkType": "chain",
        "rarity": "common",
    },
    {
        "title": "Kuolema",
        "description": "Aloita juomisluuppi. Pelaajat juovat vuorotellen yhtä enemman kuin edellinen, kunnes joku kieltaytyy.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
        "rarity": "special",
        "penalty": True,
    },
    {
        "title": "Luuppi",
        "description": "Huuda luuppi, viimeinen joka sanoi 'luuppi' juo 3",
        "players": "all",
        "drinks": 3,
        "drinkType": "social",
        "rarity": "common",
    },
    {
        "title": "Riimi",
        "description": "Sano sana. Viimeinen joka ei keksi sanaa joka rimmaa aiemmin sanot sanan kanssa juo 3.",
        "players": 1,
        "drinks": 3,
        "drinkType": "social",
        "rarity": "common",
    },
    {
        "title": "Vesiputous",
        "description": "Kaikki alkavat juomaan yhtäikaa. Kukaan ei saa lopettaa ennen kuin oikealla puolella oleva lopettaa.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
        "rarity": "common",
    },
    {
        "title": "Kategoria",
        "description": "Valitse kategoria (esim. automerkit). Muut nimeävat kategorian asioita vuorotellen. Joka epäonnistuu tai toistaa, juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "social",
        "rarity": "common",
    },
    {
        "title": "Kysymysmestari",
        "description": "Olet kysymysmestari kunnes joku nostaa uuden kysymysmestarikortin. Jokainen joka vastaa kysymykseesi jotain muuta kuin 'haista vittu' juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "rarity": "common",
    },
    {
        "title": "Säänto",
        "description": "Tee säänto joka pätee pelin loppuun. Säännön rikkoja juo.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "rarity": "common",
    },
    {
        "title": "Tauko",
        "description": "Voit poistua pelipöydästä, tai kieltäytyä tehtävästä ilman, että pitää juoda",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "rarity": "special",
    },
    {
        "title": "Huora",
        "description": "Valitse huora, huora juo aina kun kortin antaja juo",
        "players": 1,
        "drinks": None,
        "drinkType": "link",
        "rarity": "common",
    },
    {
        "title": "Kivi-paperi-sakset",
        "description": "Haasta valittu pelaaja kivi-paperi-saksiin. Häviäjä juo 4.",
        "players": 2,
        "drinks": 4,
        "drinkType": "social",
        "rarity": "common",
    },
    {
        "title": "Pari",
        "description": "Teette parin. Aina kun toinen juo, toinen juo myös. Kestää kunnes seuraava parikortti nostetaan.",
        "players": 1,
        "drinks": None,
        "drinkType": "link",
        "rarity": "common",
    },
    {
        "title": "Tarina",
        "description": "Aloita tarina yhdellä lauseella. Muut jatkavat vuorotellen. Viimeinen joka ei sanonut koko tarinaa oikein juo.",
        "players": "all",
        "drinks": None,
        "drinkType": "social",
        "rarity": "common",
    },
    {
        "title": "Venäläinen ruletti",
        "description": "Jokainen vetää liipaisinta vuorollaan. Osuma: juo 10. Todennäköisyys 1/pelaajamäärä.",
        "players": "all",
        "drinks": 10,
        "drinkType": "roulette",
        "rarity": "special",
    },
    {
        "title": "Jakokortti",
        "description": "Jaa 10 juomaa miten haluat muiden pelaajien kesken.",
        "players": 1,
        "drinks": 10,
        "drinkType": "social",
        "rarity": "special",
    },
    {
        "title": "Immunitetti",
        "description": "Seuraavalla kerralla kun sinun pitäisi juoda, et juo. Muista tämä kortti.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "rarity": "special",
        "key": "immunity",
    },
    {
        "title": "Tupla",
        "description": "Seuraavan kortin juomat tuplataan.",
        "players": 1,
        "drinks": None,
        "drinkType": "special",
        "rarity": "special",
        "key": "doubleNext",
    },
]
