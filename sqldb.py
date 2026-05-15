from kvsqlite.sync import Client as C
#from config import database_name
#انشاء
#dev = [1160471152,435009958]
db = C(f"audiobot.sqlite")
db.autocommit = True
#print(i)
#members = []
#db.delete(f"users")
#for i in open("mems.txt","r").readlines():
#	members.append(int(i.replace("\n","")))
#	db.set(f"users",members)
#	print(len(members))
#print(len(db.get(f"users")))
#print(members)
