import pypyodbc

DB_PATH = "DRIVER={SQL Server};SERVER=DESKTOP-EMPIGDT;DATABASE=ArogtanArif;Trusted_Connection=yes;"#Login with windows authentication
con = pypyodbc.connect(DB_PATH)
cursor = con.cursor()


def Get_all():
    cursor.execute("Select Servers.Id,Servers.ServerId,Servers.ServerName,LogChannels.ChannelId,LogChannels.ServerDbId FROM Servers  inner join LogChannels on LogChannels.ServerDbId=Servers.Id")
    values = cursor.fetchall()
    for item in values:
        print(item)
    con.close()


