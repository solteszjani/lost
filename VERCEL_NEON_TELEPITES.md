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
