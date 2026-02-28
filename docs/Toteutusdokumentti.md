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
- Null-window search

Shakin pelilogiikka on toteutettu `board.py` sekä `moves.py` tiedostoihin. `moves.py` keskittyy laillisten siirtojen generointiin, sekä shakkimatin että patin(stalemate) tunnistamiseen. `board.py` käsittelee kaiken muun pelilogiikan.
# Aika- ja Tilavaativuusanalyysi

## Teoreettinen analyysi

Uusimmat mittaukset on suoritettu viikolla 5 ennen Null-Window Search optimointia. NWS mittaukset löytyvät `docs\Feature_Toggle_Löydöt.md` tiedostosta, josta löytyy myös analyysi eri optimointien vaikutuksesta.

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

| Depth | Brute Force | Mitattu | Nopeutus | QS Nodes | TT Hits | Beta Cutoffs | Score |
|-------|-------------|---------|----------|----------|---------|--------------|-------|
| 2 | 1,225 | 131 | **9.4x** | 110 | 0% | 16 | -160 |
| 3 | 42,875 | 545 | **78.7x** | 487 | 0% | 38 | -110 |
| 4 | 1,500,625 | 1,374 | **1,092x** | 958 | 2.8% | 443 | -130 |
| 5 | 52,521,875 | 8,696 | **6,038x** | 7,862 | 2.8% | 835 | -90 |

**Huomio:** TT säilytetään kaikille syvyyksille → TT osumat ja tehokkuus kasvaa syvemmillä tasoilla

Feature toggle (Depth 5):

| Scenario | Negamax Nodes | QS Nodes | Time | Speedup | TT Hits | Score |
|----------|---------------|----------|------|---------|---------|-------|
| Baseline (no optimizations) | 237,203 | 0 | 12.698s | 1.00x | 1.7% | -70 |
| Quiescence only | 164,632 | 169,267 | 23.022s | 1.44x | 2.1% | -90 |
| QS + Killer Moves | 26,981 | 25,099 | 3.884s | **8.79x** | 1.4% | -90 |
| QS + History | 18,997 | 19,909 | 3.900s | **12.49x** | 2.8% | -90 |
| All Optimizations | 16,340 | 15,054 | 2.907s | **14.52x** | 2.1% | -90 |
| All + Null-Window | 16,340 | 15,054 | 2.916s | **14.52x** | 2.1% | -90 |

**Huomio:** Speedup viittaa solmujen vähennykseen, ei suoraan aikaan (baseline nodes/scenario nodes = 237203/x).

Iteratiivinen syveneminen (kaikki optimoinnit):

| Time Limit | Actual Time | Reached Depth | Negamax Nodes | QS Nodes | TT Hits | Score | Best Move |
|------------|----------------|----------------|---------------|----------|---------|-------|-----------|
| 0.1s | 0.090s | 4 | 871 | 771 | 2.5% | -110 | b1c3 |
| 0.5s | 0.463s | 5 | 1,759 | 1,369 | 3.9% | -110 | b1c3 |
| 1.0s | 0.468s | 5 | 1,759 | 1,369 | 3.9% | -110 | b1c3 |
| 2.0s | 1.938s | 6 | 14,270 | 12,753 | 5.2% | -90 | b1c3 |
| 5.0s | 7.993s | 7 | 28,603 | 24,060 | 10.4% | -90 | b1c3 |

**Huomio:** Time Limit voi ylittyä, jos uudella iteraatiolla aikaa on vielä yli 40% jäljellä. Toisaalta se voi myös alittua, jos aikaa on alle 40% jäljellä, jolloin iteraatio keskeytetään.
Voimme myös huomata, että vaikka paras siirto on b1c3 kaikilla syvyyksillä, pistearvio ei kuitenkaan ole identtinen. Syvemmillä hauilla siirto arvioidaan huonommaksi, mutta silti parhaaksi.


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
- Depth 4: 1,374 solmua (hyötyy depth 2-3 TT:stä)
- Depth 5: 8,696 solmua (hyötyy depth 2-4 TT:stä)

**Iteratiivinen syveneminen aika-rajoituksella (TT säilytetään):**
- Depth 4 (0.1s): 871 solmua
- Depth 5 (0.5s): 1,759 solmua
- Depth 6 (2.0s): 14,270 solmua
- Depth 7 (5.0s): 28,603 solmua
- TT hit rate nousee: 2.5% → 3.9% → 5.2% → 10.4%

**Huomio:** Iteratiivinen syveneminen tuottaa merkittävästi vähemmän solmuja kuin suora haku syvään, koska transpositiotaulu kerää osumia jokaisen iteraation välillä. Esimerkiksi depth 5:ssä iteratiivinen (1,759 solmua) löytää neljä kertaa vähemmän solmuja kuin suora haku (8,696 solmua). Tämä johtuu kumulatiivisesta hyödystä alempien tasojen TT:stä.

## Johtopäätökset

- Kaikilla optimoinneilla (Killer moves + History + Quiescence) saavutetaan **14.52x nopeutus** depth 5:llä
- Null-Window Search säilyttää saman nopeutuksen, mutta parantaa TT hyötyjä syvemmillä hauilla
- Move ordering (killer moves + history heuristic) on kriittinen alpha-beta tehokkuudelle
- Quiescence search vähentää solmuja merkittävästi, mutta on kallista ilman killer moves -optimointia
- Transposition taulu säilyy iteraatioiden välillä, jolloin:
  - Iteratiivinen syveneminen tuottaa 4-5x vähemmän solmuja kuin suora haku
  - TT hit rate nousee 2.5% → 10.4% syvyyksien 4-7 välillä
  - Kumulatiivinen hyöty keräytyy jokaisen iteraation välillä
- Kaiken kaikkiaan, optimointiyhdistelmä (QS + Killer + History + NWS) mahdollistaa depth 7 haun 8 sekunnissa.
# Lähteeet

https://en.wikipedia.org/wiki/Minimax
https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
https://en.wikipedia.org/wiki/Transposition_table
https://www.chessprogramming.org/Simplified_Evaluation_Function
https://www.chessprogramming.org/Killer_Move
https://www.chessprogramming.org/Quiescence_Search
https://www.chessprogramming.org/History_Heuristic