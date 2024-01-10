import sqlite3

def find_card(id):
    try:
        sqliteConnection = sqlite3.connect('YFM.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"SELECT CardID, CardName, CardType, Attack, Defense FROM Cards WHERE CardID='{id}'")
        for row in cursor:
            print("CardID =", row[0])
            print("CardName =", row[1])
            print("CardType =", row[2])
            print("Attack =", row[3])
            print("Defense =", row[4], "\n")
        cursor.close()

    except sqlite3.Error as error:
        print("Error:", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

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
