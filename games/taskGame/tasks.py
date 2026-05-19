# Each task has:
#   title       -- short name printed in large text on the receipt
#   description -- the rule or challenge text
#   players     -- how many players are picked: 1, 2, N, or "all"
#                  1 targets the drawing player themselves
TASKS = [
    {
        "title": "Juo 3",
        "description": "Juo 3.",
        "players": 1,
    },
    {
        "title": "Jaa 3",
        "description": "Jaa 3 juomaa.",
        "players": 1,
    },
    {
        "title": "Juo 3,6,9...",
        "description": "1. juo 3, 2. juo 6, 3. juo 9 jne.",
        "players": 1,
    },
    {
        "title": "Kuolema",
        "description": "Aloita juomisluuppi. Pelaajat juovat vuorotellen yhtä enemman kuin edellinen, kunnes joku kieltaytyy.",
        "players": "all",
    },
    {
        "title": "Luuppi",
        "description": "Huuda luuppi, viimeinen joka sanoi 'luuppi' juo 3",
        "players": "all",
    },
    {
        "title": "Riimi",
        "description": "Sano sana. Viimeinen joka ei keksi sanaa joka rimmaa aiemmin sanot sanan kanssa juo 3.",
        "players": 1,
    },
    {
        "title": "Vesiputous",
        "description": "Kaikki alkavat juomaan yhtaikaa. Kukaan ei saa lopettaa ennen kuin oikealla puolella oleva lopettaa.",
        "players": "all",
    },
    {
        "title": "Kategoria",
        "description": "Valitse kategoria (esim. automerkit). Muut nimeävat kategorian asioita vuorotellen. Joka epäonnistuu tai toistaa, juo.",
        "players": 1,
    },
    {
        "title": "Kysymysmestari",
        "description": "Olet kysymysmestari kunnes joku nostaa uuden kysymysmestarikortin. Jokainen joka vastaa kysymykseesi jotain muuta kuin 'haista vittu' juo.",
        "players": 1,
    },
    {
        "title": "Saanto",
        "description": "Tee saanto joka patee pelin loppuun. Saannon rikkoja juo.",
        "players": 1,
    },
    {
        "title": "Tauko",
        "description": "Voit poistua pelipöydästä, tai kieltäytyä tehtävästä ilman, että pitää juoda",
        "players": 1,
    },
    {
        "title": "Huora",
        "description": "Valitse huora, huora juo aina kun kortin antaja juo",
        "players": 2,
    },
    {
        "title": "Kivi-paperi-sakset",
        "description": "Haasta valittu pelaaja kivi-paperi-saksiin. Häviäjä juo 4.",
        "players": 2,
    },
    {
        "title": "Pari",
        "description": "Teette parin. Aina kun toinen juo, toinen juo myös. Kestää kunnes seuraava parikortti nostetaan.",
        "players": 2,
    },
    {
        "title": "Tarina",
        "description": "Aloita tarina yhdellä lauseella. Muut jatkavat vuorotellen. Viimeinen joka ei sanonut koko tarinaa oikein juo.",
        "players": "all",
    },
]
