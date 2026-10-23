# English for the children

Vocabulaire anglais essentiel pour un élève de 3ème : 1 328 mots et expressions en 21 thèmes (courant, corps, océan, surf, maison, sport, verbes, mots de liaison, et plus).

## Contenu

- `index.html` : l'application d'exercices **Word Rider**. Elle fonctionne hors ligne une fois installée.
- `pdf/mots_anglais_3eme.pdf` : la liste de vocabulaire en 15 pages, colonnes colorées en alternance.
- `sources/` : les données et les scripts qui génèrent le PDF et l'application.
- `manifest.webmanifest`, `sw.js`, `icons/`, `fonts/` : ce qui rend l'application installable et utilisable sans connexion.

## Installer sur iPhone (hors ligne)

1. Dans les réglages du dépôt : Settings, Pages, Source « Deploy from a branch », branche `main`, dossier `/ (root)`.
2. Sur l'iPhone, ouvrir l'adresse `https://courpatas.github.io/English-for-the-children/` **dans Safari**. Attendre que la page s'affiche entièrement (connexion nécessaire cette fois-là seulement).
3. Appuyer sur Partager, puis « Sur l'écran d'accueil », puis Ajouter.
4. Lancer l'application depuis son icône. Elle marche ensuite en mode avion.

La progression (XP, mots acquis) est enregistrée sur l'appareil. L'application installée et Safari ont chacun leur propre sauvegarde : le bouton « Ma progression » donne un code pour transférer.

## Mettre à jour

Après toute modification, régénérer puis changer le numéro de version pour que les téléphones rechargent le cache :

```
python3 sources/gen.py sources/app_fragment.html
python3 sources/make_pwa.py sources/app_fragment.html v3
python3 sources/build.py pdf/mots_anglais_3eme.pdf    # PDF (reportlab)
```

`sources/cx.txt` contient les phrases à trous : une ligne par mot, au format `thème:mot|phrase avec ___`.
