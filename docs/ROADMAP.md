# Találtam – fejlesztési terv

## MVP-ben megvalósított
- Bejelentések listázása, keresése és kategóriaszűrése
- Elveszett/talált bejelentés rögzítése
- PNG/JPG/WEBP képfeltöltés valódi fájltartalom-ellenőrzéssel
- Részletek és jelentés küldése
- FastAPI + SQLite fejlesztői backend

## Éles indulás előtt kötelezően befejezendő
1. Felhasználói regisztráció, bejelentkezés és e-mail/telefon ellenőrzés.
2. A bejelentésekhez tulajdonosi jogosultság; jelenleg a létrehozás nyilvános és nincs felhasználói fiók.
3. Admin hitelesítés, moderációs felület és jelentések kezelése.
4. Képtárolás tartós, biztonságos tárhelyen; helyi uploads mappa nem alkalmas több példányos/ingyenes hosztingra.
5. Helyadatok pontosítása térképen úgy, hogy a nyilvános adat csak hozzávetőleges legyen.
6. Chat / kapcsolatfelvétel beépített, adatvédelmi szempontból biztonságos módon.
7. Rate limit, spam elleni védelem, fájlméret- és képtartalom-ellenőrzés, naplózás.
8. Adatvédelmi tájékoztató, felhasználási feltételek, bejelentések és fiókok törlése.
9. iOS jogosultságok és Xcode build tesztelése.
10. Android/iOS eszközökön való végponttól végpontig tesztelés.

## Költségmentes fejlesztés
A forráskód és helyi fejlesztés ingyenes. A publikus, állandóan elérhető szerver és áruházi publikálás nem garantálható teljesen ingyenesen. Teszteléshez futtasd saját számítógépeden.
