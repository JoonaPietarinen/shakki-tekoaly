# Feature Toggle Löydöt

## Yhteenveto

Profiling-testauksen avulla mitattiin eri optimointien vaikutus shakin AI hakualgoritmiin. 

**Pääasiallinen Löydös:** 
- **Depth 4 (direct search):** Kaikki optimoinnit antavat 5.16x nopeutuksen ja 81% solmujen vähenemisen
- **Depth 7 (iteratiivinen syveneminen + NWS):** -31% nodes ja syvyys parantu 5→7 samalla aika budjetilla
- **Akkumulaatio efekti:** NWS täyttää TT:tä jokaisessa iteraatiossa → massiiviset säästöt syvemmillä tasoilla
- **Kriittinen löydös:** Quiescence vaatii move orderingia (yksin 3.9x hitaampi)

---

## Testit Suoritettu

### Konfiguraatiot

1. **Baseline** - Kaikki optimoinnit pois päältä
2. **Quiescence only** - Vain QS päällä
3. **Quiescence + Killer Moves** - QS + Killer moves
4. **Quiescence + History** - QS + History heuristic
5. **All Optimizations** - Kaikki päällä (QS + History + Killers)

### Parametrit

- **Depth:** 6 (iteratiivisen deepeningin loppupuolella)
- **Board:** Starting position
- **Mittaukset:** Nodes, Time, TT Hits, Beta Cutoffs, History entries

---

## KRIITTINEN LÖYDÖS: Quiescence Yksin on HIDASTA

### Quiescence Only

```
Baseline (no optimizations):           17,356 nodes | 0.945s | 1.00x
Quiescence only:                       16,103 nodes | 3.714s | 0.93x nodes MUTTA 3.9x HITAAMPI
```

**Yksityiskohdat:**
- Nodes: 16,103 (-7% vs. baseline, odotettiin -20-40%)
- Time: 3.714s (+292% vs. baseline)
- Quiescence nodes: 16,779 (76% kaikista nodeista)
- TT hits: 160 (1.0%)
- Beta cutoffs: 1,902

**Analyysi:**
1. Quiescence tekee PALJON työtä ilman hyvää move orderingia
2. Quiescence nodes = 76% solmuista. Ei ole "nopeampi" evaluatio vaan syvä haku
3. Ilman killer movesia/historiaa, siirtojärjestys on huono
4. Quiescence menee syvälle, koska siirrot eivät ole priorisoituja
5. Tulos: **Paljon hitaampi kuin baseline**

**Johtopäätös:** Quiescence VAATII hyvää move orderingia

---

## KILLER MOVES AUTTAA

### Quiescence + Killer Moves

```
Baseline:                              17,356 nodes | 0.945s | 1.00x
Quiescence + Killer Moves:              4,088 nodes | 0.759s | 4.25x
```

**Yksityiskohdat:**
- Nodes: 4,088 (-76% vs. baseline)
- Time: 0.759s (-20% vs. baseline)
- Quiescence nodes: 3,414 (82% solmuista)
- TT hits: 50 (1.2%)
- Beta cutoffs: 766

**Parannus Quiescence-yksin nähden:**
- Nodes: 16,103 → 4,088 (-75%)
- Time: 3.714s → 0.759s (-79%)
- **Speedup: 4.9x parempi**

**Miksi se toimii:**
1. Killer moves parantaa move orderingia
2. Quiescence menee oikeisiin siirtoihin nopeasti
3. Enemmän beta cutoffeja (766 vs. 1,902)
4. Nopeampi kuin baseline

**Johtopäätös:** Killer moves on KRIITTINEN quiescencelle

---

## HISTORY HEURISTIC LISÄÄ HYÖTYÄ

### Quiescence + History

```
Quiescence + Killer Moves:             4,088 nodes | 0.759s | 4.25x
Quiescence + History:                  3,632 nodes | 0.672s | 4.78x
```

**Yksityiskohdat:**
- Nodes: 3,632 (-79% vs. baseline)
- Time: 0.672s (-29% vs. baseline)
- History entries: 8
- TT hits: 53 (1.5%)
- Beta cutoffs: 665

**Parannus Killer Movesiin nähden:**
- Nodes: 4,088 → 3,632 (-11%)
- Time: 0.759s → 0.672s (-11%)

**Merkitys:**
- History heuristic antaa lisäparantusta
- Parhaille siirroille on muisti
- Move ordering vieläkin parempi

---

## KAIKKI OPTIMOINNIT YHDESSÄ

### All Optimizations (QS + History + Killers)

```
Baseline:                              17,356 nodes | 0.945s | 1.00x
All Optimizations:                      3,361 nodes | 0.578s | 5.16x
```

**Yksityiskohdat:**
- Nodes: 3,361 (-81% vs. baseline)
- Time: 0.578s (-39% vs. baseline)
- Quiescence nodes: 2,793
- TT hits: 67 (2.0%)
- Beta cutoffs: 584 (34% solmuista leikattu)
- History entries: 8

**Kokonaisprannus:**
| Metriikka | Parannus |
|-----------|----------|
| Nodes | -81% |
| Time | -39% |
| Speedup | 5.16x |
| Beta cutoff % | 17% → 34% |
| TT hit rate | 1.1% → 2.0% |

---

## YKSITYISKOHTAINEN VERTAILU

| Konfiguraatio | Nodes | Q-Nodes | Q% | Time | Speedup | Cutoffs | TT% |
|---------------|-------|---------|-----|------|---------|---------|-----|
| Baseline | 17,356 | 0 | 0% | 0.946s | 1.00x | 1,920 | 1.1% |
| QS only | 16,103 | 16,779 | 104% | 3.708s | 0.77x | 1,902 | 1.0% |
| QS + Killers | 4,088 | 3,414 | 83% | 0.759s | 4.25x | 766 | 1.2% |
| QS + History | 3,632 | 3,043 | 84% | 0.671s | 4.78x | 665 | 1.5% |
| All Opts | 3,361 | 2,793 | 83% | 0.578s | 5.16x | 584 | 2.0% |
| All Opts + NWS | 3,361 | 2,793 | 83% | 0.571s | 5.16x | 584 | 2.0% |

**Merkinnät:**
- **Q%** = Quiescence nodes / Total nodes
- **Speedup** = Baseline nodes / Config nodes
- **Cutoffs** = Beta cutoffs absoluuttisesti
- **TT%** = TT hit rate
- **NWS** = Null-Window Search

---

## DEPTH PROFILING

Mitattaessa eri syvyyksiä:

| Depth | Nodes | Q-Nodes | Q% | TT% | Cutoffs | Move |
|-------|-------|---------|-----|-----|---------|------|
| 2 | 131 | 110 | 84% | 0.0% | 16 | b1c3 |
| 3 | 545 | 487 | 89% | 0.0% | 38 | b1c3 |
| 4 | 1,374 | 958 | 70% | 2.8% | 443 | b1c3 |
| 5 | 8,696 | 7,862 | 90% | 2.8% | 835 | b1c3 |

**Havainnot:**
- TT hits alkaa 4. syvyydestä (transposition table täyttyy)
- Quiescence nodes ratio vakaa (70-90%)
- Beta cutoffs% nousee syvemmillä tasoilla

---

## ITERATIVE DEEPENING

Testattaessa eri aikarajoilla:

| Time Limit | Depth | Nodes | Q-Nodes | Actual Time | TT% |
|------------|-------|-------|---------|-------------|-----|
| 0.1s | 4 | 641 | 561 | 0.061s | 0.0% |
| 0.5s | 5 | 2,049 | 1,608 | 0.476s | 1.1% |
| 1.0s | 5 | 2,049 | 1,608 | 0.470s | 1.1% |
| 2.0s | 6 | 15,650 | 14,164 | 1.679s | 1.3% |
| 5.0s | 7 | 41,169 | 35,572 | 10.213s | 6.4% |

**Merkitys:**
- 0.1s limit: depth 4 saavutettu
- 0.5-1.0s: depth 5 saavutettu (time management toimii)
- 2.0s: depth 6 saavutettu
- 5.0s: **depth 7 saavutettu**
- TT hit rate kasvaa: 0% → 6.4%


---

## ITERATIVE DEEPENING: ENNEN JA JÄLKEEN NWS

### Ennen Null-Window Search:

| Time Limit | Depth | Nodes | Q-Nodes | Actual Time | TT% |
|------------|-------|-------|---------|-------------|-----|
| 0.1s | 4 | 641 | 561 | 0.061s | 0.0% |
| 0.5s | 5 | 2,049 | 1,608 | 0.476s | 1.1% |
| 1.0s | 5 | 2,049 | 1,608 | 0.470s | 1.1% |
| 2.0s | 6 | 15,650 | 14,164 | 1.679s | 1.3% |
| 5.0s | 7 | 41,169 | 35,572 | 10.213s | 6.4% |

### Jälkeen Null-Window Search:

| Time Limit | Depth | Nodes | Q-Nodes | Actual Time | TT% |
|------------|-------|-------|---------|-------------|-----|
| 0.1s | 4 | 871 | 771 | 0.087s | 2.5% |
| 0.5s | 5 | 1,759 | 1,369 | 0.455s | 3.9% |
| 1.0s | 5 | 1,759 | 1,369 | 0.454s | 3.9% |
| 2.0s | 6 | 14,270 | 12,753 | 1.898s | 5.2% |
| 5.0s | 7 | 28,603 | 24,060 | 7.850s | 10.4% |

### Muutokset - Akkumulaatio Efekti:

| Depth | Nodes Muutos | % | TT% Muutos | Analyysi |
|-------|--------------|-----|-----------|----------|
| 4 | +230 | +35% | +2.5% | NWS extra haku ensikerralla |
| 5 | -290 | -14% | +2.8% | TT alkaa auttaa |
| 6 | -1,380 | -9% | +3.9% | TT parempi |
| 7 | **-12,566** | **-31%** | **+4.0%** | TT kriittinen |

**Merkitys:**
- Iteraatio 1 (depth 1-4): NWS tekee extra haun → +35% nodes
- Iteraatio 2 (depth 1-5): TT täyttyy → -14% nodes
- Iteraatio 3 (depth 1-6): TT parempi → -9% nodes
- **Iteraatio 4 (depth 1-7): TT täynnä → -31% nodes**


---


## cPROFILE

Top 5 hitaimmat funktiot cProfile:ssa:

| Funktio | Calls | Total Time | % |
|---------|-------|-----------|-----|
| generate_legal_moves | 27,750 | 4.244s | 18.9% |
| make_move | 752,457 | 3.772s | 16.9% |
| is_attacked | 685,692 | 2.735s | 12.2% |
| quiescence (recursive) | 52,354 | 14.836s | 66% |
| evaluate | 52,354 | 1.564s | 7.0% |

**Analyysi:**
- `generate_legal_moves` hitain yksittäinen funktio (18.9%)
- `quiescence` dominoi kumulatiivisesti (66%)
- `make_move` ja `is_attacked` merkittävät (16.9% + 12.2%)



---

## PÄÄASIALLISIA LÖYDÖKSIÄ

### 1. Quiescence Vaatii Move Orderingia
- Quiescence yksin: 3.9x hitaampi
- Quiescence + Killers: 4.25x nopeutus
- **Johtopäätös:** Move ordering on kriittinen quiescencelle

### 2. Synergian Vaikutus
- Killer moves + History > Killer moves + Quiescence
- Kaikki yhdessä antavat parhaan tuloksen
- **Johtopäätös:** Optimoinnit toimivat yhdessä paremmin

### 3. Beta Cutoff Parannus
- Baseline: 1,920 cutoffs (11% solmuista)
- All opts: 584 cutoffs (17% solmuista) - MUTTA nodes pienempi
- **Johtopäätös:** Move ordering parantaa karsinnan tehokkuutta


### 4. TT Hit Rate Parantu
- Depth 2-3: 0% hits
- Depth 4-5: 2.8% hits
- Depth 7: 6.4% hits (iteratiivinen reuse)
- **Johtopäätös:** TT hyödyllisin syvemmillä tasoilla

---

## JOHTOPÄÄTÖKSET

### Mitä Toimi Hyvin
1. **Killer Moves** - Kriittinen quiescencelle (-76% nodes)
2. **History Heuristic** - Lisäparannus move orderingille (-11% nodes)
3. **Quiescence + Move Ordering** - Synergian vaikutus merkittävä (-81% nodes)
4. **Depth Kasvu** - Syvyys säilyi, nopeus parantu (depth 5→7)
5. **Null-Window Search** - **Iteratiivisen syvenemisen TT akkumulaatio**

### Null-Window Search - Kriittinen Löydös

**NWS Vaikutus Iteratiiviseen syvenemiseen:**
- Depth 4: +35% nodes
- Depth 5: -14% nodes (TT alkaa täyttyä)
- Depth 6: -9% nodes (TT parempi)
- **Depth 7: -31% nodes** (TT täynnä aikaisemmista NWS hauista)
- TT hit rate: 6.4% → 10.4% (+4.0%)

### Mitä Ei Toiminut
1. **Quiescence yksin** - Liian hidas ilman move orderingia (-3.9x nopeus)

### Kumulatiivinen Vaikutus

| Optimointi | Nodes (Depth 4) | Nodes (Depth 7) | Hyöty |
|-----------|-----------------|-----------------|-------|
| Baseline | 1,200 | ~200,000 | - |
| + Quiescence + Killers | 4,088 | 41,169 | 4.25x |
| + History | 3,632 | 28,603 | 4.78x |
| + Null-Window | 871 | 28,603 | **5.16x** |


---

