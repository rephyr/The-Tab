from cli.utils import _clearScreen

_RULES: dict[str, str] = {
    "Mexico": """\
=== MEXICO ===

Noppapeli, jossa bluffataan heitetystä tuloksesta.

PISTEYTYS
  Normaalit heitot: kaksinumeroinen arvo (esim. 65 > 54)
  Parit: voittavat kaikki normaalit (esim. 33 > 65)
  Mexico (2-1): korkein mahdollinen arvo

KULKU
  1. Heittäjä heittää kaksi noppaa — vain pelinjohtaja näkee tuloksen.
  2. Heittäjä ilmoittaa tuloksen — rehellisesti tai valehdellen.
     Ilmoitetun on oltava enemmän kuin edellinen väite.
  3. Seuraava pelaaja joko:
       Hyväksyy → ottaa nopat ja pitää väitteen ylitettävänä
       Haastaa → paljastetaan totuus

HAASTE
  Heittäjä valehteli → heittäjä juo
  Heittäjä sanoi totta → haastaja juo
  Mexico mukana → juodaan tuplasti

VOITTAJA
  Peli jatkuu kunnes lopetetaan. Ei varsinaista voittajaa.
""",

    "Buja": """\
=== BUJA ===

Korttipeli neljällä arvauskierroksella ja yhteisellä lautavaiheella.

ARVAUSKIERROKSET (jokainen pelaaja vuorollaan)
  1. Mikä maa?       Punainen (r) vai musta (b)?
  2. Isompi/pienempi? Onko seuraava kortti isompi (h) vai pienempi (l)?
  3. Välistä/ulkoa?  Osuuko seuraava kortti kahden edellisen väliin (i) vai ulkopuolelle (o)?
  4. Mikä maa?       Hertta (h), ruutu (d), risti (c) vai pata (s)?

  Oikein → saat antaa juoman
  Väärin → juo itse
  Sama arvo tai rajoilla → juo tuplasti

LAUTA
  Kortit paljastetaan rivi kerrallaan. Jokaisella rivillä on toiminto:
    JUO     — matchaava pelaaja juo
    JAA     — matchaava pelaaja antaa juoman haluamalleen
    KIPPISTÄ — matchaava pelaaja kippistää jonkun kanssa, molemmat juo

  Rivit kasvavat: esim. 2, 4, 6 juomaa
  Viimeinen kortti on aina KIPPISTÄ ja arvoltaan tuplasti viimeinen rivi.

MATCHAUS
  Pelaaja matchaa lautakorttiin jos hänellä on sama arvo kädessään.
""",

    "TaskGame": """\
=== TASKGAME ===

Vuoropohjainen tehtäväkorttipeli. Pelaajat nostavat vuorotellen kortin pakasta.

KORTTITYYPIT
  Ota       — nostaja juo
  Anna      — nostaja antaa juoman valitsemalleen pelaajalle
  Sosiaalinen — avoimen haasteen voittaja/häviäjä kirjataan käsin
  Linkki    — luo pysyvän linkin pelaajien välille:
                Pari  = molemmat juovat yhdessä
                Huora = toinen juo aina kun mestari juo
  Erikoinen — pysyvä efekti ilman välittömiä juomia
                (Sääntö, Kysymysmestari, Immunitetti, Tupla)
  Ruletti   — peräkkäisiä vetoja, yksi osuu ja juo

KOMENNOT
  d → näytä pakassa jäljellä olevat kortit
  q → lopeta peli ja tulosta tulos

PELI LOPPUU
  Kun pakka on tyhjä tai pelaajat lopettavat.
""",

    "Ravit": """\
=== RAVIT ===

Hevoskilpailu, jossa pelaajat lyövät vetoa hevosista ennen starttia.

HEVOSET
  Jokaisella hevosella on tilastot: nopeus, kestävyys, tuuri.
  Jokaisella hevosella on jockey, jolla on uniikki bonus.

VEDONLYÖNTI
  Jokainen pelaaja valitsee hevosen ja panoksen (1–N juomaa).

KILPAILU
  Joka kierros hevoset liikkuvat nopeuden ja satunnaisen heiton perusteella.
  Satunnaisia tapahtumia voivat olla:
    + Boosti, motivoitunut, ohitus
    - Kuolema, DNF, taaksepäin, kompastuminen, kaatuminen, sekaannus, salama

  Taistelu: kun kaksi hevosta on ≤1 ruutua erillään, ne voivat alkaa tapella.
  Tappelun häviäjä kuolee. Voittaja loukkaantuu (kaikki tilastot -1).

TASAPELI MAALISSA
  Jos useampi hevonen ylittää maaliviivan samaan aikaan (≤1 ruutua), pelataan
  loppukamppailu: hevosilla on HP ja vahvuus, viimeinen hengissä voittaa.

JUOMARATKAISU
  Kuollut/DNF hevonen → vedonlyöjä juo 2× panos
  Voittaja             → vedonlyöjä antaa (panos × kerroin) viimeiselle
  Muut                 → vedonlyöjä juo panoksen verran
""",
}


def showRules() -> None:
    games = list(_RULES.keys())

    while True:
        _clearScreen()
        print("\n=== SÄÄNNÖT ===\n")
        for i, name in enumerate(games, 1):
            print(f"  {i}. {name}")
        print("\n  (Enter poistuaksesi)")

        raw = input("\nValinta: ").strip()
        if not raw:
            return
        if raw.isdigit() and 1 <= int(raw) <= len(games):
            _clearScreen()
            print(f"\n{_RULES[games[int(raw) - 1]]}")
            input("Paina Enter jatkaaksesi...")
        else:
            print("Virheellinen valinta.")
