import json
import aiosqlite
import time
from datetime import datetime
current_date = datetime.utcnow()
new_time = current_date.strftime('%Y-%m-%d')
def load_json(path):
    with open(path) as f:
        return json.load(f)


async def connect_database():
   return await aiosqlite.connect("./database.db")

async def create_db():
    db = await connect_database()
    await db.execute("CREATE TABLE IF NOT EXISTS huiswerk (time INTEGER, vak TEXT, opdracth TEXT, url TEXT)")
    await db.commit()
    try:
        await db.close()
    except ValueError:
        pass

async def check_huiswerk_vandaag():
    db = await connect_database()
    check =  await db.execute(f"SELECT * FROM huiswerk WHERE time = {new_time} ")
    check_result = await check.fetchall()
    if check_result:
        return check_result
    else:
        return None