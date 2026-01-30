# Toteutusdokumentti
Työssä ei ole käytetty laajoja kielimalleja
## Ohjelman rakenne
Kyseessä on shakkitekoäly, jota vastaan voi pelata [AI-platform alustalla](https://github.com/game-ai-platform-team/tira-ai-local?tab=readme-ov-file). Tekoäly käyttää negamax-algoritmilla alpha-beta-haun ja transpositiotaulun kanssa. 
Shakin pelilogiikka on toteutettu `board.py` sekä `moves.py` tiedostoihin. `moves.py` keskittyy laillisten siirtojen generointiin, sekä shakkimatin että patin(stalemate) tunnistamiseen. `board.py` käsittelee kaiken muun pelilogiikan. Tällä hetkellä 50 siirron sääntöä ei ole toteutettum kaikki muu pelilogiikka on.

# Aika- ja Tilavaativuusanalyysi

## Teoreettinen analyysi

### Brute Force Negamax
- **Kaava:** O(b^d)
- b = 35 (branching factor shakissa)
- d = hakusyvyys

**Teoreettinen solmujen lukumäärä:**
- Depth 2: 35² = 1,225 solmua
- Depth 3: 35³ = 42,875 solmua
- Depth 4: 35⁴ = 1,500,625 solmua

### Alpha-Beta Haulla (teoria)
- **Kaava:** O(b^(d/2)) parhaassa tapauksessa
- Teoreettinen nopeutus: ~86% vähemmän solmuja

## Mitatut tulokset

Profiling-tulokset (src/profile.py):

| Depth | Brute Force | Mitattu | Nopeutus |
|-------|-------------|---------|----------|
| 2 | 1,225 | 172 | 7.1x |
| 3 | 42,875 | 759 | 56.5x |
| 4 | 1,500,625 | 2,043 | 735x |

**Toteutus:** Negamax + Alpha-Beta + Move Ordering + Transposition Table

## Miksi mitattu on paljon pienempi kuin teoria?

1. **Move Ordering** - TT-siirto tutkitaan ensin, parantaa hakua
2. **Transposition Table** - Vältetään saman aseman uudelleenlaskentaa
3. **Alpha-Beta haulla** - Teoria olettaa ideaalisen siirtojärjestyksen; move ordering lähestyy sitä

## Tilavaativuudet

| Komponentti | Tila |
|------------|------|
| Transposition Table (Depth 4) | O(2,043) solmua |
| Board copy per node | O(1) = 64 ruutua |
| Call stack | O(d) = depth 4 |
| Zobrist Hash -laskenta | O(1) = 64 XOR-operaatiota |
| Piece-square tables | O(1) = 768 satunnaislukua |

## Johtopäätökset

- Alpha-Beta haulla + move ordering saavutetaan **735x nopeutus** depth 4:llä
- Transpositiotaulun hit rate: 3.8% (depth 4) - kasvaa move orderingilla
- Mitatut tulokset osoittavat teoriaa paljon paremman tuloksen käytännössä


# Puutteet

Koen että tämän hetken ainoa varsinainen puute on Simplified Evaluation Function:in käyttö. Koen että PeSTO's Evaluation Function olisi hyödyllisempi ja tuottaisi huomattavasti parempaa tulosta.

# Lähteeet

https://en.wikipedia.org/wiki/Minimax
https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
https://en.wikipedia.org/wiki/Transposition_table
https://www.chessprogramming.org/Simplified_Evaluation_Function
