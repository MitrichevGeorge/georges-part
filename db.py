import asyncio
import atexit
import sqlite3
from typing import List, Optional, Any
from pydantic import BaseModel, Field

DB_FILE = "db.sqlite"

_save_callback = None

def _trigger_global_save():
    if _save_callback:
        _save_callback()

class AutoSaveModel(BaseModel):
    model_config = {"validate_assignment": True}

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if not name.startswith('_'):
            _trigger_global_save()

class User(AutoSaveModel):
    login: str
    email: str
    password: str

    def check_password(self, password_to_check: str) -> bool:
        return self.password == password_to_check

class AppDB(AutoSaveModel):
    name: str = "MySqliteDB"
    users: List[User] = Field(default_factory=list)

    def get_user_by_login(self, login: str) -> Optional[User]:
        return next((user for user in self.users if user.login == login), None)

    def del_user_by_login(self, login: str) -> None:
        user = self.get_user_by_login(login)
        if user:
            self.users.remove(user)
            _trigger_global_save()

    def add_new_user(self, user: User) -> bool:
        if self.get_user_by_login(user.login):
            return False
        self.users.append(user)
        _trigger_global_save()
        return True

class AsyncSqliteDocumentORM:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._lock = asyncio.Lock()
        self._save_task: Optional[asyncio.Task] = None
        self._pending_save = False
        
        self._init_db_structure()
        self.data: AppDB = self._load_from_sql()
        
        global _save_callback
        _save_callback = self.trigger_save
        
        atexit.register(self._sync_save_on_exit)

    def _init_db_structure(self) -> None:
        with sqlite3.connect(self.filepath) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_store (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def _load_from_sql(self) -> AppDB:
        with sqlite3.connect(self.filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM document_store WHERE key = 'root'")
            row = cursor.fetchone()
            if row:
                try:
                    return AppDB.model_validate_json(row[0])
                except Exception as e:
                    print(f"[DB Warning] Ошибка парсинга или структура изменена: {e}. Создан чистый стейт.")
        return AppDB()

    def trigger_save(self) -> None:
        self._pending_save = True
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        if self._save_task and not self._save_task.done():
            self._save_task.cancel()
        
        self._save_task = loop.create_task(self._debounced_save(delay=1.5))

    async def _debounced_save(self, delay: float) -> None:
        try:
            await asyncio.sleep(delay)
            async with self._lock:
                if self._pending_save:
                    await asyncio.to_thread(self._write_to_sql_sync)
        except asyncio.CancelledError:
            pass

    def _write_to_sql_sync(self) -> None:
        payload = self.data.model_dump_json()
        with sqlite3.connect(self.filepath) as conn:
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute(
                "INSERT OR REPLACE INTO document_store (key, value) VALUES ('root', ?)", 
                (payload,)
            )
            conn.commit()
        self._pending_save = False

    def _sync_save_on_exit(self) -> None:
        if self._pending_save:
            self._write_to_sql_sync()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.data, name)

initedDB = AsyncSqliteDocumentORM(DB_FILE)

async def main():
    print(f"App name: {initedDB.name}")
    
    p1 = User(login="p1", email="q@a.ru", password="123")
    initedDB.add_new_user(p1)

    user = initedDB.get_user_by_login("p1")
    
    print("Меняем email на лету...")
    user.email = "new_magic_email@test.com"
    print(f"Новый email: {user.email}")
    
    await asyncio.sleep(2.0)
    print("Успешно сохранено.")

if __name__ == "__main__":
    asyncio.run(main())