# Yugioh Fusion-Friend

## Beschreibung der Funktionalität
Die Flask-Applikation ist ein einfaches Webanwendung, die es Benutzern ermöglicht, sich zu registrieren und anzumelden. 

Nach der Anmeldung kann der User ein Bild hochladen. Dieses Bild wird mit Image-Recognition analysiert um die Karten in der Hand zu erkennen. Mit den erkannten Karten wird eine Datenbankabfrage gemacht um die möglichen Fusionen zu erhalten. 

Schlussendlich wird dem User auf einer Show-Page eines Boards der analysierte Spielstand gezeigt und die möglichen Fusionen die angewendet werden könnnen.

## Prozess des Projekts

### Image-Recognition

Um die einzelnen Bilder der Karten in einem Screenshot zu erkennen habe ich die Python Library opencv-python verwendet. 

#### Template-Matching-Methode

Die erste Methode ist dazu da um 1 unser Screenshot mit einem Bild zu matchen. Also wir testen ob das Template bild in unserem Screenshot enthalten ist.

Die Methode hat Verschiedene parameter, die wir verwenden um die Image-Recongition möglich zu machen und um sie genauer zu machen:

```python
def match_template_in_thread(template_path, large_image, gray_large_image, template_size, threshold, matched_filenames):
```

Ich habe zuerst die Methode `cv2.imread` mit `IMREAD_GRAYSCALE` verwendet um das Bild in Grauskala zu lesen. 

```python
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
```
Danach habe ich das Bild in das richtige aspect ratio geresizet mit `cv2.resize`. Dies erhöht die Treffquotengenauigkeit der Bilderkennung.

Das effektive template Matching wird mit cv2.matchTemplate gemacht. Hier wird unser grauskaliges, geresiztes bild mit einem Template-Bild verglichen.

```python
result = cv2.matchTemplate(gray_large_image, template, cv2.TM_CCOEFF_NORMED)
```
#### Match images to board

In dieser Methode loopen wir über einen Ordner der unsere Template-Bilder beinhaltet. Auf die einzelnen Bilder führen wir die methode `match_template_in_thread` aus um zu schauen ob das Bild in unserem Screenshot enthalten ist. 

```python
def match_images_to_board(board, max_threads=24):
```
Die Matches die wir finden, Speichern wir in einem Array.

Da das Bild in verschiedenen Grössen überprüft wird, dauerte das Matching etwa 60 Sekunden ursprünglich. Um das matching schneller zu machen habe ich Concurrency verwendet und das Matching auf Multi-Threading verlagert. 

Mit 24 Threads wurde die Zeit auf etwa 10 Sekunden reduziert.

```python
with ThreadPoolExecutor(max_threads) as executor:
        # Iterate over each template image in the folder using threads from the pool
        for template_file in os.listdir(template_folder):
            template_path = os.path.join(template_folder, template_file)
            executor.submit(match_template_in_thread, template_path, large_image, gray_large_image, template_size, 0.80, matched_filenames)
```
### DB-Abfrage

Es wurde von einem Github-User eine DB Opensource released die alle Karten und dessen Attribute, sowie die möglichen Fusionen der Karten beinhaltet.

In der Methode `showFusions` führe ich mit den ids der gematchten Karten die Methode `findFusions` aus die effektiv die Abfrage auf die DB macht:

```python
def find_fusions(id1, id2):
    fusions = []
    try:
        sqliteConnection = sqlite3.connect('YFM.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"SELECT Material1, Material2, Result FROM Fusions WHERE Material1='{id1}' AND Material2='{id2}'")
        for row in cursor:
            fusions.append([row[0], row[1], row[2]])
        cursor.close()

    except sqlite3.Error as error:
        print("Error:", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
    return fusions
```

### Flask-Applikation

Die Webapplikation wurde mit Flask erstellt. Flask ist ein Webframework für Python das auf dem MVC-Prinzip aufbaut.

Mit der flask_login library und der bcrypt library habe ich die Login-Funktionalität erstellt. Das beim registrieren Empfange Passwort wird zuerst Client-Seitig validiert und dann auf der Server-Seite empfangen und mit bcrypt gehasht und auf dem User-Objekt abgelegt.

#### User-Model

```python
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    boards = db.relationship('Board', back_populates='user')
```

Die Uploads wurden alle über ein HTML-Upload-Form hochgeladen, dann Serverseitig empfangen, mit einem unique Filenamen versehen und schlussendlich auf einem Board-Objekt referenziert.

#### Board-Model

```python
class Board(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    filename = db.Column(db.String(250), unique=True, nullable=False)
    fusions = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', back_populates='boards')
```

### Gelernetes

Mit diesem Projekt habe ich gelerent, wie ich eine 3-Layer-Architektur in einer Webapplikation umsetzen kann und wie man Cookies und Session Handling einsetzt. Ich bin sehr zufrieden mit meinem Ergebnis

## Testcases

| Test                               | Erwartet                                                                  | Resultat                                                                  | Erfolgreich? |
|------------------------------------|---------------------------------------------------------------------------|---------------------------------------------------------------------------|--------------|
| Registrierung eines neuen Users    | Registrierung Erfolgreich und User an Login-Page weitergeleitet           | Registrierung Erfolgreich und User an Login-Page weitergeleitet           | x            |
| Login für einen registrierten User | User wird eingeloggt und auf die Root-Page weitergeleitet                 | User wird eingeloggt und auf die Root-Page weitergeleitet                 | x            |
| Upload eines Screenshots           | User kann ein Bild hochladen und es wird ein Board erstellt               | User konnte ein Bild hochladen und es wird ein Board erstellt             | x            |
| Fusionen werden angezeigt          | Bild wurde richtig analysiert und die möglichen Fusionen werden angezeigt | Bild wurde richtig analysiert und die möglichen Fusionen werden angezeigt | x            |

## Reflexion

Mit dieser Applikation konnte ich Image-Recognition mal an einem richtigen Projekt testen. Das schwierigste war, das Image-Recognition über einen grösseren Datensatz effizient zu machen. Momentan schauen wir für jede Karte die im Bild existiert ob sie vorhanden ist und dass auch noch in verschiedenen Grössen. Wenn man zuerst den Datensatz pre-selektionieren könnte, dann könnte man vielleicht den Prozess optimieren.

Als Lösung habe ich mich für Multi-Threading entschieden. Dies ist eher Brute-Forcing und braucht recht viel Rechenleistung. Es ist also eine Kompensation des ursprünglichen Problems anstatt eine Lösung.

Nächstes Mal würde ich mehr Zeit in das Optimieren der einzelnen Funktionen investieren.