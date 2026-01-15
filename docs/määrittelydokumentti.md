# Määrittelydokumentti
Tämä dokumentti määrittelee Helsingin Yliopiston Tietojenkäsittelytieteen kandiohjelman Aineopintojen harjoitustyö: Algoritmit ja tekoäly -kurssin projekti.

## Aihe

Projektin aiheena on shakille toteutettava tekoäly. Toteutan Pythonilla shakkipelin sovelluslogiikan sekä tekoälyn, joka käyttää negamax + alpha‑beta ‑hakua ja transpositiotaulua.

## Ohjelmointikielet
Toteutan projektin Pythonilla.

Vertaisarvioinnissa voin arvioida ainakin Java, JavaScript, C++, C# kieliä.

## Projektin kieli

Projektin dokumentaatio kirjoitetaan suomeksi. Lähtökohtasesti kaikki muu projektissa tulee olemaan englanniksi.

## Käyttö

Harjoitustyössä käytän kurssin tarjoamaa tekoälyalustaa shakin pelaamiseen. Tekoälyni ei kommunikoi suoraan graafisen käyttöliittymän kanssa, vaan saa syötteet alustalta standard inputin kautta. Syötteet sisältävät kulloisenkin pelitilan (esim. tehdyt siirrot tai FEN-kuvauksen), ja ohjelma päivittää sisäisen shakkilaudan tilan näiden perusteella sekä palauttaa alustalle laskemansa siirron merkkijonona.

## Aika- ja tilavaativuudet

Negamax + alpha‑beta ‑haun pahimman tapauksen aikavaativuus on O(b^d), missä b on haarautuvuus ja d haun syvyys. Alpha‑beta‑karsinnan parhaassa tapauksessa (hyvä siirtojärjestys) tutkittavien solmujen määrä pienenee likimain O(b^{d/2})‑luokkaan, mikä mahdollistaa syvemmän haun samalla ajankäytöllä.

Tilavaativuus ilman transpositiotaulua on pääosin rekursion syvyyden verran pinoa, eli O(d), sekä shakkilaudan tilan esitys. Transpositiotaulu toteutetaan hash‑tauluna, jonka koko on ennalta määritetty, sen tilavaativuus on O(N), missä N on tauluun varattujen alkioiden määrä. Transpositiotaulu ei muuta pahimman tapauksen O(b^d)‑aikavaativuutta, mutta vähentää käytännössä tutkittavien solmujen määrää, kun jo arvioituja asemia ei tarvitse käsitellä uudelleen. 

## Lähteet

Projektissa käytän seuraavia lähteitä:

[Negamax](https://en.wikipedia.org/wiki/Negamax)

[Alpha–beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)

[Transposition table](https://en.wikipedia.org/wiki/Transposition_table)
