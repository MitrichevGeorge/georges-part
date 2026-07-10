import asyncio
import atexit
import sqlite3
from typing import List, Optional
from pydantic import BaseModel, Field

DB_FILE = "db.sqlite"


class User(BaseModel):
    login: str
    email: str
    password: str

    def check_password(self, password_to_check: str) -> bool:
        return self.password == password_to_check

    def update_email(self, new_email: str):
        self.email = new_email
        initedDB.trigger_save()

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "User":
        return cls.model_validate_json(json_str)


class AppDB(BaseModel):
    name: str = "MySqliteDB"
    users: List[User] = Field(default_factory=list)

    def get_user_by_login(self, login: str) -> Optional[User]:
        for user in self.users:
            if user.login == login:
                return user
        return None

    def del_user_by_login(self, login: str) -> None:
        user = self.get_user_by_login(login)
        if user in self.users:
            self.users.remove(user)

    def add_new_user(self, user: User) -> bool:
        if self.get_user_by_login(user.login):
            return False
        self.users.append(user)
        initedDB.trigger_save()
        return True


class AsyncSqliteDBEngine:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._lock = asyncio.Lock()
        self._save_task: Optional[asyncio.Task] = None
        self._loop = None
        
        self._init_db_structure()
        self.data: AppDB = self._load_from_sql()
        atexit.register(self._sync_save_on_exit)

    def _init_db_structure(self):
        with sqlite3.connect(self.filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def _load_from_sql(self) -> AppDB:
        with sqlite3.connect(self.filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM kv_store WHERE key = 'root'")
            row = cursor.fetchone()
            if row:
                try:
                    return AppDB.model_validate_json(row[0])
                except Exception as e:
                    print(f"[DB Error] Ошибка парсинга SQL данных: {e}")
        return AppDB()

    def trigger_save(self):
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        if self._save_task and not self._save_task.done():
            self._save_task.cancel()
        
        self._save_task = self._loop.create_task(self._debounced_save(delay=2.0))

    async def _debounced_save(self, delay: float):
        try:
            await asyncio.sleep(delay)
            async with self._lock:
                await self._write_to_sql_async()
        except asyncio.CancelledError:
            pass

    async def _write_to_sql_async(self):
        import aiosqlite
        payload = self.data.model_dump_json()
        async with aiosqlite.connect(self.filepath) as db:
            await db.execute(
                "INSERT OR REPLACE INTO kv_store (key, value) VALUES ('root', ?)", 
                (payload,)
            )
            await db.commit()

    def _sync_save_on_exit(self):
        payload = self.data.model_dump_json()
        with sqlite3.connect(self.filepath) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO kv_store (key, value) VALUES ('root', ?)", 
                (payload,)
            )
            conn.commit()

    def __getattr__(self, name):
        return getattr(self.data, name)


initedDB = AsyncSqliteDBEngine(DB_FILE)
