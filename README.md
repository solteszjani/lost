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
