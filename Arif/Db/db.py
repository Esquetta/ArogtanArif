import pypyodbc

from Db.Entities.Servers import Servers

DB_PATH = "DRIVER={SQL Server};SERVER=DESKTOP-EMPIGDT;DATABASE=ArogtanArif;Trusted_Connection=yes;"  # Login with windows authentication
con = pypyodbc.connect(DB_PATH)
cursor = con.cursor()

Server=Servers()

def Get_all():
    cursor.execute(
        "Select Servers.Id,Servers.ServerId,Servers.ServerName,LogChannels.ChannelId,LogChannels.ServerDbId FROM Servers  inner join LogChannels on LogChannels.ServerDbId=Servers.Id")
    values = cursor.fetchall()
    for item in values:
        print(item)
    con.close()


def Set_Server(Server=Servers()):
    if Server is not None:
        try:
            cursor.execute(f"insert into Servers(ServerId,ServerName) values({Server.ServerId},'{Server.ServerName}')")
            print("New server added db")
            con.commit()
            con.close()

        except Exception:
            print("Some error Accured")
    else:
        print("You must enter all values")



