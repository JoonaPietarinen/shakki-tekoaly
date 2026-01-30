# Testausdokumentti
`readme.md` sisältää [![CI](https://github.com/JoonaPietarinen/shakki-tekoaly/actions/workflows/main.yml/badge.svg)](https://github.com/JoonaPietarinen/shakki-tekoaly/actions/workflows/main.yml) [![codecov](https://codecov.io/gh/JoonaPietarinen/shakki-tekoaly/graph/badge.svg?token=LqlnGuxI5O)](https://codecov.io/gh/JoonaPietarinen/shakki-tekoaly)
CI-pipeline ajaa pytestit `src/tests` kansiosta. 

## Yksikkötestauksen kattavuus

### Testatut komponentit
- Laudan esitystapa & FEN-muunnos (src/tests/test_board.py)
- Siirtojen luonti (src/tests/test_moves.py)
- AI haku algoritmi (src/tests/test_search.py)
- Transpositiotaulut (src/tests/test_transposition.py)

**Testien lukumäärä:** 24 testiä yhteensä

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

### Siirtojen luonti (test_moves.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_start_position | Board() | 20 laillista siirtoa |  Pass |
| test_promotion | "8/P7/8/8/8/8/8/K6k w - - 0 1" | Sisältää a7a8q, a7a8r, a7a8b, a7a8n | Pass |
| test_castling | "r3k2r/8/.../8/R3K2R w KQkq - 0 1" | Sisältää e1g1 (kingside) ja e1c1 (queenside) | Pass |
| test_en_passant | "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1" | Sisältää e5d6 (en passant) | Pass |

### Transpositiotaulut (test_transposition.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_zobrist_hash_consistent | Sama asema 2x | Hash1 == Hash2 | Pass |
| test_zobrist_hash_different | Eri asemat | Hash1 != Hash2 | Pass |
| test_transposition_table_stores_result | negamax(depth=2) | Tulos tallennetaan TT:hen | Pass |
| test_transposition_table_exact_flag | negamax(-∞, +∞) | EXACT flag tallennettu | Pass |
| test_transposition_table_lookup_with_bounds | Sama search 2x | Sama score ja move | Pass |
| test_transposition_table_depth_cutoff | Depth 2 → Depth 3 | TT päivittyy syvempään | Pass |

### AI haku algoritmi (test_search.py)

| Testi | Syöte | Odotus | Tulos |
|-------|-------|--------|-------|
| test_negamax_finds_move | negamax(depth=2) | Palauttaa laillisen siirron | Pass |
| test_find_best_move_returns_valid | find_best_move(depth=2) | Palauttaa laillisen siirron | Pass |
| test_ai_prefers_captures | Board() + depth=2 | Ei kaadu, palauttaa siirron | Pass |

---

## Testien ajaminen

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
python src/profile.py
```

**Tulokset (Negamax + Alpha-Beta + Move Ordering + Transposition Table):**

| Depth | Nodes Searched | TT Hits | TT Stores | Best Move |
|-------|----------------|---------|-----------|-----------|
| 2 | 172 | 0 (0.0%) | 21 | b1c3 |
| 3 | 759 | 21 (2.8%) | 63 | b1c3 |
| 4 | 2,043 | 78 (3.8%) | 533 | b1c3 |

Tätä käsitellään lisää tiedostossa `Toteutusrapostti.md`.

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
pytest src/tests/ -v --tb=short
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

### Ei vielä katetut
Mattien tunnistaminen  
Iteratiivinen syventäminen  
Shakin tarkistus  

---

## Johtopäätökset

- **24 yksikkötestiä** kattaa ydin ominaisuudet
- **Kaikki testit menevät läpi**
- **Profilointi osoittaa** algoritmin tehokkuuden
- **Deterministiset testit** toistettavissa milloin tahansa
- **Empiriiset tulokset** validoivat teoreettisen analyysin

