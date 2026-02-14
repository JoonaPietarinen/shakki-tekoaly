# Toteutusdokumentti
Työssä ei ole käytetty laajoja kielimalleja
## Ohjelman rakenne
Kyseessä on shakkitekoäly, jota vastaan voi pelata [AI-platform alustalla](https://github.com/game-ai-platform-team/tira-ai-local?tab=readme-ov-file). Tekoäly käyttää negamax-hakua alpha-beta-karsinnan ja transpositiotaulun kanssa. 

**Implementoidut optimoinnit:**
- Negamax + Alpha-Beta karsinta
- Transpositiotaulu (Zobrist hash)
- Evaluointifunktio (materiaali + piece-square tables)
- Killer move heurestiikka (move ordering)
- Iteratiivinen syveneminen
- Inkrementaalinen Zobrist hash päivitys
- Optimoitu board copy (list comprehension)
- Quiescence search
- History heuristic (move ordering)
- MVV-LVA (Most Valuable Victim - Least Valuable Aggressor) (move ordering)

Shakin pelilogiikka on toteutettu `board.py` sekä `moves.py` tiedostoihin. `moves.py` keskittyy laillisten siirtojen generointiin, sekä shakkimatin että patin(stalemate) tunnistamiseen. `board.py` käsittelee kaiken muun pelilogiikan.
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
- Depth 5: 35⁵ = 52,521,875 solmua

### Alpha-Beta Haulla (teoria)
- **Kaava:** O(b^(d/2)) parhaassa tapauksessa
- Teoreettinen nopeutus: ~86% vähemmän solmuja

## Mitatut tulokset

Profiling-tulokset (src/profiling.py):

`profile_search()`:

| Depth | Brute Force | Mitattu | Nopeutus | TT Hits | Beta Cutoffs |
|-------|-------------|---------|----------|---------|--------------|
| 2 | 1,225 | 131 | **9.4x** | 0% | 16 |
| 3 | 42,875 | 545 | **78.7x** | 0% | 38 |
| 4 | 1,500,625 | 1,386 | **1,083x** | 2.8% | 443 |
| 5 | 52,521,875 | 18,771 | **2,797x** | 1.3% | 1,795 |

**Huomio:** TT säilytetään kaikille syvyyksille → TT osumat kasvaa syvemmillä tasoilla

`profile_iterative_deepening()` ennen viikon 5 optimointeja (Quiescence search ja MVV-LVA):

| Time Limit | Actual Time | Reached Depth | Nodes | TT Hits | Best Move |
|------------|----------------|----------------|-------|---------|-----------|
| 0.1s | 0.205s | 5 | 2,044 | 1.1% | b1c3 |
| 0.5s | 0.205s | 5 | 2,044 | 1.1% | b1c3 |
| 1.0s | 1.759s | 6 | 22,260 | 1.3% | e2e4 |
| 2.0s | 1.759s | 6 | 22,260 | 1.3% | e2e4 |
| 5.0s | 10.061s | 7 | 121,914 | 3.2% | b1c3 |

Viikon 5 optimointien jälkeen (Quiescence search ja MVV-LVA):
| Time Limit | Actual Time | Reached Depth | Nodes | Quiescence Nodes | TT Hits | Best Move |
|------------|----------------|----------------|-------|----------------|---------|-----------|
| 0.1s | 0.062s | 4 | 641 | 561 | 0% | b1c3 |
| 0.5s | 0.475s | 5 | 2,049 | 1,608 | 1.1% | b1c3 |
| 1.0s | 0.472s | 5 | 2,049 | 1,608 | 1.1% | b1c3 |
| 2.0s | 1.706s | 6 | 15,650 | 14,164 | 1.3% | b1c3 |
| 5.0s | 10.326s | 7 | 41,169 | 35,572 | 6.4% | b1c3 |

**Huomio:** Time Limit voi ylittyä, jos uudella iteraatiolla aikaa on vielä yli 40% jäljellä. Toisaalta se voi myös alittua, jos aikaa on alle 40% jäljellä, jolloin iteraatio keskeytetään.


## Miksi mitattu on paljon pienempi kuin teoria?

1. **Move Ordering** - Killer moves + TT-siirto tutkitaan ensin, parantaa hakua huomattavasti
2. **Transposition Table** - Vältetään saman aseman uudelleenlaskentaa, säilytetään kaikille syvyyksille
3. **Beta Cutoffs** - Korkea määrä solmuha leikataan pois
4. **Alpha-Beta haulla** - Killer moves lähestyy ideaalista siirtojärjestystä
5. **Kumulatiivinen hyöty** - Alempien tasojen TT-osumia hyödynnetään syvemmillä hauilla

## Tilavaativuudet

| Komponentti | Tila |
|------------|------|
| Transposition Table (Depth 5) | O(22,260) solmua × 4 arvoa ≈ 89KB |
| Board copy per node | O(1) = 64 ruutua × 2 tavua = 128 tavua |
| Call stack | O(d) = depth 5 |
| Zobrist Hash -laskenta | O(1) = inkrementaalinen päivitys |
| Killer moves table | O(depth) = 100 × 2 siirtoa = 200 siirtoa |
| History table | O(siirtojen määrä) ≈ 5-16 siirtoa per depth |
| Quiescence tracking | O(1) = erillinen laskuri |
| Piece-square tables | O(1) = 768 arvoa |

## Suorituskyvyn vertailu

**Suora haku per syvyys (TT säilytetään):**
- Depth 2: 131 solmua (TT tyhjä)
- Depth 3: 545 solmua (hyötyy depth 2 TT:stä)
- Depth 4: 1,386 solmua (hyötyy depth 2-3 TT:stä)
- Depth 5: 18,771 solmua (hyötyy depth 2-4 TT:stä)

**Iteratiivinen syveneminen aika-rajoituksella (TT säilytetään):**
- Depth 5 (0.1s): 2,044 solmua
- Depth 6 (1.0s): 22,260 solmua
- Depth 7 (5.0s): 121,914 solmua
- TT hit rate nousee: 1.1% → 1.3% → 3.2%

**Huomio:** Molemmissa TT säilytetään, joten hyödyt ovat samankaltaiset. Erona on aika-rajoituksen myötä mahdollinen syvempi haku.

**Iteratiivinen syveneminen viikon 5 jälkeen:**
- Depth 5 (0.5s): 2,049 negamax solmua
- Depth 6 (2.0s): 15,650 negamax solmua
- Depth 7 (5.0s): 41,169 negamax solmua
- Quiescence nodes: 1,608 → 14,164 → 35,572
- TT hit rate: 1.1% → 1.3% → 6.4%

syvyydellä 7 tt hit rate tuplaantui. Aikavaatimukset pysyvät melko samana. Quiescence search ja MVV-LVA optimoinnit näyttävät esim. sen, että syvyyksillä 5 ja 6 aiemmin saatu tulos e2e4 ei ollutkaan paras siirto.
## Johtopäätökset

- Alpha-Beta haulla + killer move orderingilla saavutetaan **2,797x nopeutus** depth 5:llä
- Beta cutoffien määrä (1,795 / 18,771 = 9.6%) osoittaa tehokkaan alpha-beta karsinnan
- Transposition taulu säilyy iteraatioiden välillä, mikä antaa:
  - Osumia syvemmillä hauilla (depth 4-5)
  - Paremman move orderingin (aiemmilta tasoilta)
  - Kumulatiivisen hyödyn iteraatioissa
- Move ordering (killer moves + TT) on kriittinen alpha-beta tehokkuudelle
- Viikon 5 move ordering optimoinnit (Quiescence search + MVV-LVA) tuottivat merkittäviä hyötyjä syvemmillä hauilla, erityisesti TT hit rate nousi huomattavasti ja karsinta oli tehokkaampaa.
# Lähteeet

https://en.wikipedia.org/wiki/Minimax
https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
https://en.wikipedia.org/wiki/Transposition_table
https://www.chessprogramming.org/Simplified_Evaluation_Function
https://www.chessprogramming.org/Killer_Move
https://www.chessprogramming.org/Quiescence_Search
https://www.chessprogramming.org/History_Heuristic