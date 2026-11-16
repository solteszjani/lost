# Találtam – Budapest roadmap

## Termékirány
Ingyenes, budapesti fókuszú, magyar nyelvű elveszett-talált közösségi webalkalmazás. A vendégek böngészhetnek; a hirdetésfeladás és az üzenetküldés bejelentkezéshez kötött.

## Megvalósítási szakaszok

### 1. Budapest-alapok (most)
- Budapest 23 kerülete strukturáltan rögzíthető hirdetésenként.
- Kerület szerinti API-szűrés és webes kereső.
- Meglévő hirdetések adatainak megőrzése: új `district` oszlop automatikus migrációval.
- Hirdetésfeladáskor kötelező kerületválasztás.

### 2. Biztonság és megbízhatóság
- Tartós képtárolás Vercel Blobbal.
- Admin/moderátor szerepkör és jelentéskezelő felület.
- Rate limiting, CSRF-védelem, jelszó-visszaállítás, e-mail ellenőrzés.
- A személyes kapcsolati adatok védelme; kommunikáció alapértelmezetten belső chaten.

### 3. Térkép és helyalapú keresés
- OpenStreetMap alapú térkép.
- Helyszín-geokódolás, koordináták és térképes szűrés.
- Pontos helyszín elrejtése publikus nézetben, ha biztonsági kockázatot jelent.

### 4. Egyezéskeresés és értesítések
- Elveszett/talált bejelentések párosítása kategória, kulcsszavak, idő és távolság szerint.
- Felhasználói megerősítés, téves egyezés visszajelzése.
- Web Push és e-mail értesítések beállítható gyakorisággal.

### 5. Budapest közösség és indulás
- Kerületi landing oldalak és megosztható bejelentések.
- Partneri kapcsolatok közlekedési, oktatási és közösségi helyszínekkel.
- Moderációs szabályzat, adatkezelési tájékoztató és visszaélés-bejelentés.

## Jelenlegi implementáció
- Vercel + FastAPI + Neon PostgreSQL.
- Kerület mező a hirdetés létrehozásánál és módosításánál.
- Kerület szerinti szűrés.
- Vendég böngészés; hirdetésfeladás és chat bejelentkezéshez kötve.
