import pypyodbc

DB_PATH = "DRIVER={SQL Server};SERVER=DESKTOP-EMPIGDT;DATABASE=CarGallery;Trusted_Connection=yes;"
con = pypyodbc.connect(DB_PATH)
cursor = con.cursor()


def Get_all():
    cursor.execute("Select * from Cars")
    values = cursor.fetchall()
    for item in values:
        print(item)
    con.close()



