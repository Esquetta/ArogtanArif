import  pypyodbc

DB_PATH="DRIVER={SQL Server};SERVER=DESKTOP-EMPIGDT;DATABASE=CarGallery;Trusted_Connection=yes;"
    #"Data Source=DESKTOP-EMPIGDT;Initial Catalog=CarGallery;Integrated Security=True;Connect Timeout=30;Encrypt=False;TrustServerCertificate=False;ApplicationIntent=ReadWrite;MultiSubnetFailover=False"
con=pypyodbc.connect(DB_PATH)
cursor=con.cursor()
cursor.execute("Select * From Cars")
values=cursor.fetchall()

for item in values:
    print(item)

con.close()
