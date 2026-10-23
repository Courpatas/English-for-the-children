# English for the children

Vocabulaire anglais essentiel pour un élève de 3ème : 1 328 mots et expressions en 21 thèmes (courant, corps, océan, surf, maison, sport, verbes, mots de liaison, et plus).

## Contenu

- `index.html` : application d'exercices interactifs (Word Rider). Un seul fichier, il s'ouvre dans un navigateur, sans connexion. Activité en plusieurs formats, avec retour après chaque réponse, par thème ou sur tous les mots.
- `pdf/mots_anglais_3eme.pdf` : la liste de vocabulaire en 15 pages, avec colonnes colorées en alternance.
- `sources/` : les données et les scripts qui génèrent le PDF et l'application.

## Utiliser l'application

Ouvrir `index.html` dans un navigateur. Avec GitHub Pages activé (Settings, Pages, branche `main`, dossier racine), elle est aussi en ligne à l'adresse du dépôt.

## Régénérer

Les scripts de `sources/` attendent leurs fichiers dans `/tmp/work`.

```
python3 sources/gen.py index.html            # application
python3 sources/build.py pdf/mots_anglais_3eme.pdf   # PDF (reportlab)
```

`cx.txt` contient les phrases à trous : une ligne par mot, au format `thème:mot|phrase avec ___`.
