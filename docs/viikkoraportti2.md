# Viikkoraportti 2
**Mitä olen tehnyt tällä viikolla?** 

Perehdyin valitsemiini algoritmeihin syvällisemmin, ja kertasin shakin säännöt varmistuakseni siitä, että toteutan pelilogiikan oikein. 
Tämän jälkeen aloin toteuttamaan shakkia. Pyrin parhaani mukaan toteuttamaan shakin kokonaisuudessaan, mutta jätin toistuvaan asemaan perustuva tasapelin toteutettavaksi seuraavalle viikolle. 

Lisäksi toteutin negamax-algoritmin alpha-beta-karsinnalla ja testit pelilogiikalle.

Pelasin pelin tekoälyä vastaan ja käytännössä hävisin. Jos olisin lisännyt PST taulun kuninkaan loppupelistä, olisin todennäköisesti hävinnyt oikeasti. Koska en lisännyt kyseistä taulua, tekoäly jäi jumiin silmukkaan, jossa se liikutti kuningastaan a8 ja b8 välillä samalla, kun minulla oli jäljellä enää oma kuninkaani.

**Miten ohjelma on edistynyt?**

Pelilogiikka on hyvällä mallilla, ja täysin pelattavissa. Tekoäly on alkeellinen, mutta toimii.

**Mitä opin tällä viikolla?**

Piece-Square Tables ja niiden käyttö.

Negamax + alpha-beta -haun toteutus pythonilla.

**Mitä teen seuraavaksi?**

Seuraavaksi toteutan toistuvaan asemaan perustuva tasapelin. Tämän jälkeen siirryn transpositiotaulun toteutukseen ja siirtojen järjestämiseen alpha-beta-karsinnalle.
