# Találtam – elveszett és talált tárgyak

Flutter iOS/Android kliens + FastAPI backend MVP.

## Fontos
- A mobilprojekt natív Flutter-forráskód, nem előre lefordított APK/IPA.
- Android APK Windows alatt is készíthető Flutter + Android SDK telepítése után.
- iOS buildhez macOS + Xcode szükséges.
- A backend helyben ingyen futtatható. Nyilvános, folyamatos működéshez tárhely és adatbázis szükséges; az ingyenes szolgáltatói csomagok korlátozottak és változhatnak.
- A jelenlegi MVP-ben nincs fizetés, hirdetés vagy előfizetés.

## Funkciók
- Elveszett / talált bejelentések
- Kategóriák, keresés és szűrés
- Bejelentés részletei, helyszín és dátum
- Képfeltöltés
- Bejelentés létrehozása és saját bejelentések törlése
- Kapcsolatfelvételi mód (telefon/e-mail elrejtés helyett csak a bejelentésben megadott kapcsolat jelenik meg)
- Moderációs jelentés végpont
- Admin státusz és bejelentések moderálásának alapja

## Indítás Windows alatt

### 1. Backend
PowerShell:
```powershell
cd "...\talaltam_project\server"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Böngészős alkalmazás: `http://127.0.0.1:8000`
API dokumentáció: `http://127.0.0.1:8000/docs`
Állapotellenőrzés: `http://127.0.0.1:8000/health`

A böngészős felületen kereshetsz, szűrhetsz, megnyithatod a bejelentések részleteit, és új elveszett/talált bejelentést adhatsz fel képpel együtt.

### 2. Flutter
Telepítsd a Flutter SDK-t és Android Studio-t (Android SDK-val).
```powershell
cd "...\talaltam_project\mobile"
flutter pub get
flutter run
```
A mobil emulátorból a `localhost` helyett `10.0.2.2` kell Android emulátoron. Fizikai telefon esetén a számítógép helyi IP-címét add meg.

Az API-címet a `mobile/lib/services/api_service.dart` fájlban módosítsd.

### 3. Android APK
```powershell
flutter build apk --release
```
Az APK helye:
`mobile/build/app/outputs/flutter-apk/app-release.apk`

## Adatvédelem és biztonság
Ez egy induló MVP, nem éles, nagy forgalmú rendszer. Élesítés előtt szükséges többek között:
- valódi felhasználói regisztráció és hitelesítés
- képek felhőalapú tárolása
- rate limit, spam- és csalásvédelem
- adatvédelmi tájékoztató, felhasználási feltételek, törlési folyamat
- moderációs adminfelület
- biztonsági mentések és naplózás
- pontos helyadatok védelme (a publikus bejegyzésekben csak hozzávetőleges helyet jeleníts meg)

## Licenc
Saját projektváz, szabadon módosítható.


## Webalkalmazás és telefonos nézet

A webes felület reszponzív: telefonon egyoszlopos, érintésre optimalizált elrendezést használ, nagyobb kijelzőn többoszlopos nézetet. HTTPS-en telepíthető PWA-ként is: Androidon a böngésző „Telepítés” / „Kezdőképernyőhöz adás” menüpontjával, iPhone-on Safari → Megosztás → Főképernyőhöz adás. A PWA telepítéséhez HTTPS szükséges (localhost fejlesztéskor kivétel).


## Budapest V2 – közösségi funkciók

- Interaktív OpenStreetMap/Leaflet térkép, kerület- és típusfilter, saját helyzet körüli sugárszűrés. A térképes pont megadásához a bejelentésnél a „Jelenlegi helyem megadása” gomb használható; a térképen lévő pontokra kattintva is megnyitható a hirdetés.
- Automatikus, szöveg/kategória/kerület és – ha van koordináta – távolság alapú lehetséges egyezések. Új bejelentéskor a rendszer értesítést készít az érintett fiókoknak.
- Értesítési központ és böngészőértesítés (a böngésző engedélyével, amíg az oldal fut).
- Chat képfeltöltéssel, olvasási állapottal, archiválással és tiltással.
- Profiladatok, sikeres visszaadások száma, értékelési átlag; opcionális telefonszám mentése.
- Bejelentés lezárása „Sikeresen visszakerült” állapottal és összesített statisztikával.
- A telefonszám és e-mail cím nem jelenik meg nyilvánosan a hirdetésben; a kapcsolat belső üzenetküldéssel történik.

### Fontos üzemeltetési megjegyzések

A térképet az OpenStreetMap csempéi és a Leaflet könyvtár jeleníti meg, ezért internetkapcsolat szükséges. A koordinátákat a felhasználó engedélyével, a böngésző helymeghatározása adja. A távolságszűrés csak akkor működik, ha a bejelentéshez koordináta tartozik.

A jelenlegi egyezéskereső szabályalapú (leírás, cím, kategória, kerület, koordináták), nem képfelismerő mesterséges intelligencia. A kép feltöltése támogatott, de a fotók vizuális összehasonlítása külön képfelismerő szolgáltatást igényel.

A telefonszám menthető, de SMS-kódos ellenőrzéshez külső SMS-szolgáltató és API-kulcs szükséges; addig a profil nem kap ellenőrzött jelzést. A böngészőértesítés nem garantált, ha a böngésző/oldal teljesen be van zárva; valódi háttér pushhoz Web Push kulcsok és szolgáltatói konfiguráció szükséges.

A feltöltött képek jelenleg a szerver fájlrendszerébe kerülnek. Vercel szerveren ez nem tartós tárhely, ezért éles használat előtt Vercel Blob vagy más tartós objektumtár bekötése szükséges. Ne tölts fel éles adatot addig, amíg a tartós képtárhely és a push/SMS szolgáltatások nincsenek konfigurálva.

### V2.2 újdonságok
- Budapest területére korlátozott térkép és térképes lekérdezés.
- Profilom: profilkép feltöltése, e-mail- és jelszómódosítás, fióktörlés.
- Fénykép alapú keresés: perceptuális képhash-alapú hasonlósági előszűrés, megnyitható hirdetési találatokkal.
- A képi találatok becslések; nem garantálják, hogy ugyanaz a tárgy szerepel a képeken.


## V9 – közösségi platform fejlesztések
- Moderációs admin felület: jelentések áttekintése, kivizsgálása/elutasítása, hirdetések elrejtése, felhasználók felfüggesztése/visszaállítása.
- Admin jogosultság: állítsd be a Vercel Environment Variables között az `ADMIN_EMAIL` változót. Az e-mail címmel belépő felhasználó admin felületet kap.
- Térkép: Budapest határai, marker clustering, kerület/típus/távolság szűrők.
- Push: VAPID kulcsokkal bekapcsolható böngésző push. Kulcsok nélkül az alkalmazáson belüli értesítések továbbra is működnek.
- Közösségi statisztikák: sikeres visszaadások, aktív bejelentések, felhasználók, kerületi és kategória bontás.
- A beszélgetések automatikus frissítése rövid időközű lekérdezéssel történik; ez nem WebSocket-alapú kapcsolat.

### Éles indulás előtt szükséges külső szolgáltatások
1. Tartós képtárolás (Vercel Blob vagy S3 kompatibilis szolgáltatás). A Vercel ideiglenes fájlrendszerén tárolt feltöltések nem garantáltan maradnak meg.
2. Valódi szemantikus AI-képfelismeréshez CLIP/SigLIP modellvégpont vagy külső AI szolgáltató és API-kulcs szükséges. A beépített keresés jelenleg perceptuális képhash-alapú vizuális hasonlóságot ad, nem garantál azonos tárgy felismerést eltérő szögből készült képeken.
3. Push értesítéshez VAPID kulcspár szükséges (`VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`).

## V27 – közösségi, admin és chat fejlesztések

- Bővített adminisztrációs műveleti napló: moderációs döntések, hirdetésműveletek és fiókfelfüggesztések rögzítése.
- Nyilvános profilból értékelhető minden olyan felhasználó, akivel a bejelentkezett tag közös, lezárt ügyletben vett részt; a profil felsorolja az értékelhető lezárt ügyleteket.
- Az értékeléshez opcionális, legfeljebb 500 karakteres nyilvános vélemény tartozhat; új értékelésről értesítés készül.
- Értesítési központ: összes/olvasatlan szűrés, külön „összes olvasottnak” művelet.
- Szöveges chat: idempotens kliensüzenet-azonosító és egyszeri automatikus újrapróbálás, így hálózati megszakadáskor nem keletkezik duplikált üzenet.
- A chatüzenet és az értesítés adatbázisba mentése nem vár szinkron push-hálózati hívásra.
- Mobilon teljes képernyős chat/profil/értesítés/admin felületek, biztonságos alsó/felső margókkal.

A meglévő adatbázis megőrzésével indul. Új adatbázis-objektum: `admin_audit_logs`; a `messages` táblában új, opcionális `client_message_id` mező jön létre automatikusan.
