import  pypyodbc

DB_PATH="DRIVER={SQL Server};SERVER=DESKTOP-EMPIGDT;DATABASE=CarGallery;Trusted_Connection=yes;"
con=pypyodbc.connect(DB_PATH)
cursor=con.cursor()
cursor.execute("Select * From Cars")
values=cursor.fetchall()

for item in values:
    print(item)

con.close()
