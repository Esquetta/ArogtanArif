import pypyodbc

from Db.Entities.Servers import Servers
from Db.Entities.LogChannels import LogChannels

DB_PATH = "DRIVER={SQL Server};SERVER=DESKTOP-EMPIGDT;DATABASE=ArogtanArif;Trusted_Connection=yes;"  # Login with windows authentication
con = pypyodbc.connect(DB_PATH)
cursor = con.cursor()

Server = Servers()


def Get_all():
    cursor.execute(
        "Select Servers.Id,Servers.ServerId,Servers.ServerName,LogChannels.ChannelId,LogChannels.ServerDbId FROM Servers  inner join LogChannels on LogChannels.ServerDbId=Servers.Id")
    values = cursor.fetchall()
    for item in values:
        print(item)


def Get_Server(id: int):
    cursor.execute(
        f"Select Servers.Id,Servers.ServerId,Servers.ServerName,LogChannels.ChannelId,LogChannels.ServerDbId FROM Servers  inner join LogChannels on LogChannels.ServerDbId=Servers.Id Where ServerId={id}")
    values = cursor.fetchall()

    return values


def Set_Server(Server=Servers()):
    if Server is not None:
        try:
            cursor.execute(f"insert into Servers(ServerId,ServerName) values({Server.ServerId},'{Server.ServerName}')")
            print("New server added db")
            con.commit()

        except Exception:
            print("Some error Accured")
    else:
        print("You must enter all values")


def Set_LogChannel(LogChannel=LogChannels()):
    if Server is not None:
        try:
            cursor.execute(
                f"insert into LogChannels(ChannelId,ServerDbId) values({LogChannel.ChanelId},{LogChannel.ServerDbId})")
            print("Log channel  added db")
            con.commit()

        except Exception:
            print("Some error Accured")
    else:
        print("You must enter all values")


def Get_SvInfo(svId: int):
    cursor.execute(
        f"Select * from Servers Where ServerId={svId}")
    values = cursor.fetchall()
    return values


def Get_LogChannel(ChannelId: int):
    cursor.execute(f"Select * from  LogChannels where ChannelId={ChannelId}")
    values = cursor.fetchall()
    return values


def Delete_Sv(dbId: int):
    cursor.execute(f"Delete from Servers Where Id={dbId}")
    cursor.commit()


def Delete_LogChannel(ChannelId: int):
    cursor.execute(f"Delete from LogChannels Where ChannelId={ChannelId}")
    cursor.commit()
