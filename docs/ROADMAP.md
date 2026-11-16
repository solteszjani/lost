# Találtam – Budapest fejlesztési állapot

## Budapest V2-ben elkészült
- Leaflet / OpenStreetMap térkép, kerületi és típus szerinti szűrés, helyzet alapú sugárszűrés.
- Koordináta mentése a bejelentésekhez.
- Szabályalapú automatikus egyezéskeresés és értesítések.
- Belső értesítési központ, böngészőértesítés.
- Chat képfeltöltéssel, olvasási állapottal, archiválással, tiltással.
- Profil, visszaadási statisztika, értékelési API és opcionális telefonszám mentés.
- Sikeres visszaadás lezárása.
- Nyilvános kontaktadatok eltávolítva a hirdetés JSON-ból.

## Éles indulás előtt szükséges
1. Vercel Blob vagy más tartós képtárhely.
2. Web Push VAPID kulcsok és push subscription tárolás a háttérértesítésekhez.
3. SMS-szolgáltató az OTP-s telefonszám-ellenőrzéshez.
4. Képfelismerő/vision szolgáltatás a fotók vizuális összehasonlításához.
5. Moderátori/admin felület, rate limit, spam- és visszaélésvédelem, adatvédelmi/jogi szövegek.
6. Éles Neon adatbázison végzett migrációs és terhelési teszt.
