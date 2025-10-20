# Création d’un mini moteur de base de données en Python

## Comment exécuter le projet 

1- cloner le projet
```
git clone https://github.com/julien-lair/python---SGBD
cd python\ -\ SGBD/
```

2- Créer un environnement virtuel 
```
python3 -m venv .venv
source .venv/bin/activate 
```

3- Installer les dépendances
* Avec UV:
    ```
    uv sync 
    ``` 

* Avec le fichier requirements.txt 
    ``` 
    pip install -r requirements.txt 
    ``` 

4 - Lancer le projet 

**Démarrer le serveur** 
```
python3 serveur/main.py
``` 

**Démarrer le client en ligne de commande** 
```
python3 client_cli/main.py
``` 

**Démarrer le client graphique** 
```
python3 client_gui/main.py
``` 

**Démarrer les tests unitaires** 
```
python3 serveur/test.py
``` 

## Caractéristiques 

Création d'un moteur SQL complet, prenant en charge les commandes : 
- CREATE TABLE
- DROP TABLE
- INSERT
- SELECT
- UPDATE
- DELETE
- DESCRIBE

Pouvant gérer les types suivants : INT / FLOAT / TEXT / BOOL / SERIAL

Les conditions WHERE peuvent gérer les conditions : =, <, >, <=, >=, !=, AND, OR, (, )

Aucun projet externe n'a été utilisé pour la gestion du parseur SQL. Le tout à été fait dans ce projet.

Le serveur communique avec des socket TCP sur le port `1234`. Les clients (client_cli et client_gui) peuvent s'y connecter.

Authentification : 
Au premier lancement du serveur, il sera demandé de créer un compte pour permettre par la suite au clientzs de se connecter au serveur.

## Exemples de commandes 
``` 
CREATE TABLE users (prenom TEXT, age INT, admin Bool);

INSERT INTO users VALUES ("Julien",25, True),("Jean",23,False);
INSERT INTO users (admin,age,prenom) VALUES (False,18,"Victor");

SELECT * FROM users WHERE age > 20;
SELECT prenom FROM users WHERE (age > 20 and _id = 2) OR (age < 24 AND admin = False);

UPDATE users SET admin=True WHERE age < 24 AND prenom="Victor";

DELETE FROM table WHERE admin = False;

DESCRIBE users;

DROP TABLE users;
```

## Format fichier binaire utilisé
Pour l’enregistrement des données dans un fichier `.db`, la structure suivante a été implémentée.

Chaque fichier .db contient :

- un header, qui décrit la structure de la table,
- puis les données, encodées en binaire.

### Le header:

    1 - [size_name] -> Taille (en octets) du nom de la table
    
    2 - name -> Nom de la table, encodé en UTF-8

    3- [number_col] -> Nombre total de colonnes dans la table (entier non signé, 4 octets)

    4 - Pour chaque colonne :
        
        4.1 - [size_col] -> Taille (en octets) du nom de la colonne

        4.2 - [col] -> Nom de la colonne, encodé en UTF-8

        4.3 - [encode_type_col] -> Type de la colonne, encodé sous forme d’entier non signé
            INT -> 1
            FLOAT -> 2
            TEXT -> 3
            BOOL -> 4
            SERIAL -> 5

    5 - [number_SERIAL] -> Nombre de colonnes de type SERIAL (entier non signé)

    6 - Pour chaque colonne de type SERIAL :

        6.1 - [size_col_serial] -> Taille (en octets) du nom de la colonne

        6.2 - colSerial -> Nom de la colonne, encodé en UTF-8

        6.3 - valeur_serial -> Dernière valeur auto-incrémentée (entier non signé)
    
#### Exemple de header
`CREATE TABLE users (_id SERIAL, prenom TEXT, age INT);`

HEADER: `[5]"users"[3][3]"_id"[5][6]"prenom"[3][3]"age"[1][1][3]"_id"[0]`

### Les données

Les données sont ajoutées à la suite du header.

Pour chaque ligne de la table, la structure est la suivante :

1- Un booléen (1 octet) indiquant si la ligne est considérée comme supprimée (True) ou non (False)

2 - Puis les valeurs des colonnes, encodées dans le même ordre que celui défini dans le header.
