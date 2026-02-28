# Testausdokumentti
`readme.md` sisältää [![CI](https://github.com/JoonaPietarinen/shakki-tekoaly/actions/workflows/main.yml/badge.svg)](https://github.com/JoonaPietarinen/shakki-tekoaly/actions/workflows/main.yml) [![codecov](https://codecov.io/gh/JoonaPietarinen/shakki-tekoaly/graph/badge.svg?token=LqlnGuxI5O)](https://codecov.io/gh/JoonaPietarinen/shakki-tekoaly)
CI-pipeline ajaa pytestit `src/tests` kansiosta. 

## Yksikkötestauksen kattavuus

### Testatut komponentit
- Laudan esitystapa & FEN-muunnos (src/tests/test_board.py)
- Siirtojen luonti ja tarkistus (src/tests/test_moves.py)
- AI haku algoritmi (src/tests/test_search.py)
- Transpositiotaulut (src/tests/test_transposition.py)

**Testien lukumäärä:** 56 testiä yhteensä  

**Testikattavuus:** ~99%

---

## Testattu funktiot

### Laudan esitystapa & FEN-muunnos (test_board.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_to_fen_start_position | Default Board() | "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" | Pass |
| test_fen_roundtrip | FEN → Board → FEN | Sama FEN palaajaa | Pass |
| test_to_fen_after_move | Board() + e2e4 | Pawn on e4, turn='b' | Pass |
| test_to_fen_after_capture | e4d5 capture | d5:lla pawn, halfmove=0 | Pass |
| test_to_fen_castling_rights | e2e4, e7e5, g1f3 | "KQkq" castling preserved | Pass |
| test_to_fen_promotion | a7a8q | Queen on a8, pawn gone |  Pass |
| test_start_fen | Board().set_fen("startpos") | Alkuasema asetettu oikein | Pass |
| test_attempt_to_move_non_existent_piece | e3e4 (tyhjä ruutu) | Heittää ValueError | Pass |

### Siirtojen luonti (test_moves.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_start_position | Board() | 20 laillista siirtoa | Pass |
| test_promotion | "8/P7/8/8/8/8/8/K6k w - - 0 1" | Sisältää a7a8q, a7a8r, a7a8b, a7a8n | Pass |
| test_castling | "r3k2r/8/.../8/R3K2R w KQkq - 0 1" | Sisältää e1g1 (kingside) ja e1c1 (queenside) | Pass |
| test_en_passant | "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1" | Sisältää e5d6 (en passant) | Pass |
| test_checkmate | "rk6/8/8/8/8/8/8/Kqr5 w KQkq - 0 1" | Ei liikkeitä, kuningas shakissa | Pass |
| test_stalemate | "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1" | Ei liikkeitä, kuningas ei shakissa | Pass |
| test_not_stalemate | "7k/8/8/8/8/8/8/K7 b - - 0 1" | On liikkeitä (ei pattia) | Pass |
| test_50_move_rule_not_yet_draw | Halfmove = 99 | Ei vielä draw-sääntöä | Pass |
| test_50_move_rule_is_draw_at_100 | Halfmove = 100 | On draw (100 siirtoa) | Pass |
| test_50_move_rule_is_draw_over_100 | Halfmove = 101 | On draw (yli 100 siirtoa) | Pass |
| test_castling_black | "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1" | Sisältää e8g8 ja e8c8 | Pass |
| test_black_pawn_moves | "8/pp6/8/8/8/8/8/K6k b - - 0 1" | Sisältää a7a6/a7a5, b7b6/b7b5 | Pass |
| test_black_knight_moves | "8/8/8/8/8/8/8/K5nk b - - 0 1" | Ratsu-siirtoja löytyy | Pass |
| test_pawn_attacks_white | Valkoinen sotilas e4:lla | d5 ja f5 hyökkäävät | Pass |
| test_pawn_attacks_black | Musta sotilas e5:lla | d4 ja f4 hyökkäävät | Pass |

### Transpositiotaulut (test_transposition.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_zobrist_hash_consistent | Sama asema 2x | Hash1 == Hash2 | Pass |
| test_zobrist_hash_different | Eri asemat | Hash1 != Hash2 | Pass |
| test_transposition_table_stores_result | negamax(depth=2) | Tulos tallennetaan TT:hen | Pass |
| test_transposition_table_exact_flag | negamax(-∞, +∞) | EXACT flag tallennettu | Pass |
| test_transposition_table_upper_bound | negamax alpha cutoff | UPPER flag tallennettu | Pass |
| test_transposition_table_lookup_with_bounds | Sama search 2x | Sama score ja move | Pass |
| test_transposition_table_speedup | negamax 2x samalle asemalle | Toinen kutsu on nopeampi | Pass |
| test_transposition_table_depth_cutoff | Depth 2 → Depth 3 | TT päivittyy syvempään | Pass |

### AI haku algoritmi (test_search.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_negamax_finds_move | negamax(depth=2) | Palauttaa laillisen siirron | Pass |
| test_find_best_move_returns_valid | find_best_move(depth=2) | Palauttaa laillisen siirron | Pass |
| test_ai_prefers_captures | Board() + depth=2 | Ei kaadu, palauttaa siirron | Pass |
| test_is_capture_detects_capture | Board("...e4d5..."), move="e4d5" | Palauttaa True | Pass |
| test_is_capture_detects_non_capture | Board(), move="e2e4" | Palauttaa False | Pass |
| test_is_capture_en_passant | Board en passant pos, move="e5d6" | Palauttaa False (ei capture) | Pass |
| test_quiescence_with_no_captures | Board() (alkuasema) | Palauttaa stand pat evaluaation | Pass |
| test_quiescence_with_captures | Board e4d5 pos | Tutkii sieppaukset | Pass |
| test_quiescence_stand_pat | Board() | Stand pat >= beta | Pass |
| test_quiescence_searches_captures | Board e4d5 pos | Captures tutkitaan | Pass |
| test_mvv_lva_queen_capture_better_than_pawn | MVV-LVA scoring | Palauttaa tuple (value, -attacker) | Pass |
| test_history_heuristic_updates | negamax(depth=2) | History table päivittyy | Pass |
| test_history_table_clears | clear_transposition_table() | History table tyhjä | Pass |
| test_quiescence_captures_sorted_by_mvv_lva | Board captures | Captures sorted oikein | Pass |
| test_feature_flag_quiescence_enabled | ENABLE_QUIESCENCE: True/False | Q-nodes tallennetaan vain jos QS enabled | Pass |
| test_feature_flag_history_heuristic | ENABLE_HISTORY_HEURISTIC: True/False | Historia pitäisi tallentua vain jos se on päällä | Pass |
| test_feature_flag_killer_moves | ENABLE_KILLER_MOVES: True/False | Haun pitäisi toimia myös ilman killer movesia | Pass |
| test_feature_flags_combination | 4 feature flag kombinaatiota (QS on/off, History on/off, Killers on/off) | Haun pitäisi onnistua kaikissa feature flag tapauksissa | Pass |
| test_null_window_search_enabled | ENABLE_NULL_WINDOW: True/False, depth=2 | Haun pitäisi onnistua NWS:stä riippumatta | Pass |
| test_window_search_narrower_window | ENABLE_NULL_WINDOW: True, depth=3, all flags enabled | Löytää hyvän avaus siirron | Pass |
| test_null_window_with_all_optimizations | ENABLE_NULL_WINDOW: True/False, depth=4, all optimizations | Haun pitäisi onnistua NWS+kaikki optimpoinnit yhdistelmällä | Pass |
| test_ai_checkmate_detection | "rk6/8/8/8/8/8/8/Kqr5 w KQkq - 0 1" | Palauttaa None (matissa) | Pass |
| test_ai_time_limit | depth=10, time_limit=0.1s | Palauttaa siirron ajassa | Pass |
| test_ai_time_limit_prediction | depth=10, time_limit=10s | Palauttaa siirron 10s sisällä | Pass (skipped in CI) |

---

## Testien ajaminen
Aja testit Poetry-virtuaaliympäristössä:

```bash
poetry shell
```
Tai lisäämällä poetry run -komennon:
```bash
poetry run ... 
```

### Kaikki testit
```bash
pytest src/tests/ -v
```

### Yksittäiset testitiedostot
```bash
pytest src/tests/test_board.py -v
pytest src/tests/test_moves.py -v
pytest src/tests/test_search.py -v
pytest src/tests/test_transposition.py -v
```

### Yksittäinen testi
```bash
pytest src/tests/test_moves.py::test_start_position -v
```

### Coverage
```bash
pytest src/tests/ --cov=src --cov-report=html
```

---

## Empiriiset suorituskyky-testit

### Profilointitulokset

Käytetty: src/profile.py

```bash
python src/profiling.py
```

**Tulokset:**

| Depth | Brute Force | Mitattu | Nopeutus | QS Nodes | TT Hits | Beta Cutoffs | Score |
|-------|-------------|---------|----------|----------|---------|--------------|-------|
| 2 | 1,225 | 131 | **9.4x** | 110 | 0% | 16 | -160 |
| 3 | 42,875 | 545 | **78.7x** | 487 | 0% | 38 | -110 |
| 4 | 1,500,625 | 1,374 | **1,092x** | 958 | 2.8% | 443 | -130 |
| 5 | 52,521,875 | 8,696 | **6,038x** | 7,862 | 2.8% | 835 | -90 |

Iteratiivinen syveneminen (kaikki optimoinnit):

| Time Limit | Actual Time | Reached Depth | Negamax Nodes | QS Nodes | TT Hits | Score | Best Move |
|------------|----------------|----------------|---------------|----------|---------|-------|-----------|
| 0.1s | 0.090s | 4 | 871 | 771 | 2.5% | -110 | b1c3 |
| 0.5s | 0.463s | 5 | 1,759 | 1,369 | 3.9% | -110 | b1c3 |
| 1.0s | 0.468s | 5 | 1,759 | 1,369 | 3.9% | -110 | b1c3 |
| 2.0s | 1.938s | 6 | 14,270 | 12,753 | 5.2% | -90 | b1c3 |
| 5.0s | 7.993s | 7 | 28,603 | 24,060 | 10.4% | -90 | b1c3 |

Tätä käsitellään lisää tiedostossa `Toteutusdokumentti.md`.

---

## Konkreettisia testausesimerkkejä

### Siirtojen kelpoisuus
```python
# Testattu: Alkuasemassa täsmälleen 20 laillista siirtoa
test_start_position()
# → Tulos: 20 siirtoa löydetty 
```

### Transpositiotaulujen hyöty
```python
# Testattu: Sama asema tutkitaan kaksi kertaa depth=2
# Ensimmäinen: 0 TT hits
# Toinen: 21 TT hits (2.8%)
# → TT toimii oikein 
```

### Sotilaan korotus
```python
# Testattu: FEN "8/P7/8/8/8/8/8/K6k w - - 0 1"
# Odotettu: 4 promootiosiirtoa (a7a8q, a7a8r, a7a8b, a7a8n)
# Tulos: Kaikki 4 löydetty 
```

### Linnoittautuminen
```python
# Testattu: FEN "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
# Odotettu: Sekä e1g1 (kingside) että e1c1 (queenside)
# Tulos: Molemmat löydetty 
```

### En Passant
```python
# Testattu: FEN "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1"
# Odotettu: e5d6 (en passant kaappaus)
# Tulos: En passant siirto löydetty 
```

---

## Testien syötteet

### Lauta & FEN testit
- **Alkuasema:** Oletusasema `Board()`
- **Custom FEN:** Eri pelitilanteita testaava FEN-merkintä
- **Siirto-testit:** e2e4, d7d5, e4d5 (kaappaus)
- **Erikoissäännöt:** Linnoitus (e1g1, e1c1), en passant (e5d6), ylennys (a7a8q)

### Siirron luonti testit
- **Alkuasema:** 20 siirtoa odotettu
- **Ylennys:** Asema missä sotilas on 7. rivillä
- **Castling:** Asema missä kuninkaat ja tornit ovat paikoillaan
- **En passant:** Asema missä en passant on mahdollinen

### Transpositiotaulu testit
- **Hash konsistenssi:** Sama asema → sama hash
- **Hash erilainen:** Eri asemat → eri hashit
- **TT lookup:** Saman aseman toinen tutkinta palauttaa cached tuloksen

---

## Testien toistettavuus

Kaikki testit ovat **deterministisiä:**
- Zobrist hashing käyttää fixed seed (42) → samat hashit joka kerralla
- Sama FEN → samat siirrot
- Sama depth → samat solmut

**Testit voidaan toistaa milloin tahansa:**
```bash
pytest src/tests/ -v
```

---

## Testauksen kattavuusanalyysi

### Katetut alueet
FEN parsing ja serialisaatio  
Laudan tilan muutokset  
Laillisten siirtojen luominen  
Zobrist hashing  
Transpositiotaulut  
Negamax haku  
Alpha-beta karsinta  
Mattien tunnistaminen  
Pattien tunnistaminen  
Shakin tunnistaminen  
Iteratiivinen syventäminen   
Quiescence search  
Historiaheuristiikka  
Killer moves  
Null window search  
Pawn attacks  
King attacks  
50-siirron säännön tarkistus  
En passant tarkistus  
Virheellisten siirtojen tunnistus

---

## Johtopäätökset

- **56 yksikkötestiä** kattaa ydin ominaisuudet ja optimoinnit
- **Kaikki testit menevät läpi**
- **Profilointi osoittaa** algoritmin tehokkuuden ja optimointien vaikutukset
- **Deterministiset testit** toistettavissa milloin tahansa
- **Empiriiset tulokset** validoivat teoreettisen analyysin
