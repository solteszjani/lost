# Találtam – Vercel + Neon telepítés

## 1. Neon adatbázis
1. Hozz létre egy projektet a Neon Console-ban.
2. A Connect menüben másold ki a PostgreSQL connection stringet.
3. Vercel projektben Settings → Environment Variables:
   - `DATABASE_URL` = a Neon connection string
   - `COOKIE_SECURE` = `true`
4. A connection string tartalmazza az `sslmode=require` paramétert.

## 2. Feltöltés GitHubra
A projekt gyökérmappáját (ahol a `vercel.json`, `requirements.txt`, `api/` és `public/` van) töltsd fel egy GitHub repositoryba.

## 3. Vercel
1. Vercel → Add New → Project → Import Git Repository.
2. Framework Preset: Other.
3. Root Directory: a projekt gyökere.
4. Build Command és Output Directory maradhat üresen/alapértelmezetten.
5. Add meg a fenti Environment Variables értékeket, majd Deploy.

## 4. Fontos működési korlát
A Neon tárolja a felhasználókat, munkameneteket, hirdetéseket és üzeneteket. A Vercel fájlrendszere ideiglenes, ezért a mostani kép-feltöltés `/tmp` alá kerül, és nem tekinthető tartósnak. Éles használat előtt a képeket Vercel Blob vagy más objektumtároló szolgáltatásba kell kötni. A meglévő fájl-feltöltési útvonalat ezért ne tekintsd tartós tárhelynek.

## 5. Ellenőrzés
- `/health` – API állapot
- `/docs` – API dokumentáció
- `/` – Találtam webalkalmazás

A séma első induláskor automatikusan létrejön a Neon adatbázisban.


## Felület használata
A hirdetésfeladás külön „Új hirdetés” gomb mögötti ablakban nyílik meg. Vendégként a látogatók a hirdetéseket megtekinthetik; új hirdetés feladásához és üzenetküldéshez be kell jelentkezniük. A szerveroldali végpontok is bejelentkezést követelnek meg.


## Budapest kerület szerinti hirdetések
A frissített verzió automatikusan hozzáadja a `district` oszlopot a meglévő `listings` táblához. A régi hirdetések megmaradnak, de a kerületük üres marad; ezeket a tulajdonosnak később szerkesztéssel kell kiegészítenie. Az új hirdetéshez már kötelező a 23 budapesti kerület egyikének kiválasztása.

## V2.1 – Térképes egyezések megnyitása
- A térképi jelölő megnyitásakor a rendszer automatikusan lekéri a lehetséges, ellentétes típusú egyezéseket.
- A jelölő felugró ablakában az egyező hirdetések külön listában, egyezési százalékkal és – ha kiszámítható – távolsággal jelennek meg.
- Az egyező hirdetés saját adatlapja közvetlenül a térképről megnyitható.
- A nyilvános egyezéslekérdezés csak a nyilvános hirdetési adatokat adja vissza; elérhetőséget nem tesz közzé.

## Budapest V2.2 – térkép, profil és képalapú keresés

- A térkép Budapest közelítő földrajzi határain belülre van korlátozva; a szerveroldali térképes lekérdezés is kizárja az ezen kívüli koordinátákat.
- A bejelentkezett felhasználó a **Profilom** menüben profilképet tölthet fel, módosíthatja e-mail-címét és jelszavát, illetve véglegesen törölheti a fiókját.
- A fényképes kereső a feltöltött képet a hirdetések képeivel perceptuális képhash alapján hasonlítja össze. Ez hasonló vizuális mintákat kereső előszűrés, nem mesterséges intelligenciás tárgyfelismerés; a találati százalék nem bizonyítja a tárgy azonosságát.
- A képfeldolgozáshoz a szerver `Pillow` csomagot használja, amely már szerepel a `server/requirements.txt` fájlban.
- Fontos: a profilképek és hirdetésképek jelenlegi feltöltése a szerver `uploads` könyvtárába ment. Vercel szerveren ez nem tartós tárhely; éles használathoz Vercel Blob vagy más objektumtár bekötése szükséges.


## V9 adminisztráció és push értesítések

- A Vercel Environment Variables között állítsd be az `ADMIN_EMAIL` értékét egy olyan e-mail-címre, amellyel admin fiókot regisztrálsz. Már létező felhasználónál a `users.role` mező értékét `admin`-ra kell állítani a Neon SQL Editorban.
- Web Push-hoz generálj VAPID kulcspárt, majd állítsd be a `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY` és `VAPID_SUBJECT` változókat. Ezután a felhasználó az Értesítések ablakban bekapcsolhatja a push-t.
- Az admin menü csak admin jogosultságú fióknál jelenik meg. A moderációs API minden műveletnél szerveroldalon ellenőrzi a jogosultságot.
- A képi keresés jelenlegi alapja perceptuális képhash. Ez nem szemantikus AI-tárgyfelismerés; valódi CLIP/SigLIP képi embedding szolgáltatás külön modellvégponttal és szolgáltatói hozzáféréssel kapcsolható be.
- A Vercel helyi fájlrendszere nem tartós. Éles indulás előtt a feltöltéseket tartós objektumtárba (pl. Vercel Blob vagy S3-kompatibilis tárhely) kell átállítani.


## Értesítések törlése

Az értesítések külön-külön vagy egyben törölhetők. A törlés végleges, a rekordok azonnal törlődnek a Neon adatbázisból.

## Törölt hirdetések automatikus végleges törlése

A felhasználó által törölt hirdetés 10 napig visszamarad a `listings` táblában `deleted` állapottal. A Vercel napi, 03:00 UTC időpontú Cron Job a 10 napnál régebben törölt hirdetéseket és a hozzájuk tartozó üzeneteket/értékeléseket véglegesen törli.

A Vercel Environment Variables részében állíts be egy erős, véletlenszerű `CRON_SECRET` értéket. A Vercel Cron ezt `Authorization: Bearer <CRON_SECRET>` fejléccel küldi.
