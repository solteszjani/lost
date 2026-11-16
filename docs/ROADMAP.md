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


## V9 – közösségi platform csomag
- Adminisztrációs API és admin felület: jelentések kivizsgálása, hirdetések elrejtése, fiókok felfüggesztése/visszaállítása.
- Leaflet jelölőcsoportosítás a zsúfolt térképhez.
- Bővített közösségi statisztikák kerületi és kategória bontásban.
- Web Push előfizetés és service worker értesítéskezelés VAPID kulcsokkal.
- Pontosabb szöveges párosítás magyar szavakra hangolt tokenizálással.
- Meglévő PWA telepíthetőségi alap továbbfejlesztve.

### Még külső konfigurációt igényel
- Push: VAPID kulcspár.
- Tartós képtárolás: Vercel Blob vagy S3 kompatibilis tárhely és hozzáférési token.
- Szemantikus AI-képfelismerés: CLIP/SigLIP modellvégpont vagy szolgáltatói API. A jelenlegi beépített képi keresés perceptuális képhash-alapú, nem mélytanulásos tárgyfelismerés.
