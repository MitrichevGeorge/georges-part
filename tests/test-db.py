import asyncio
from db import initedDB, User

async def main():
    print(f"App name: {initedDB.name}")
    for i in initedDB.users:
        print(f"login: {i.login} email: {i.email}")
    p1 = User(login="p1", email="q@a.ru", password="123")
    initedDB.add_new_user(p1)

    user = initedDB.get_user_by_login("p1")
    print(f"Correct pw:{user.check_password('123')}")
    jtext = user.to_json()
    u2 = User.from_json(jtext)
    print(f"Login:{u2.login} Correct pw:{u2.check_password('123')}")
    initedDB.del_user_by_login("p1")


if __name__ == "__main__":
    asyncio.run(main())
