import json
import os
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Protocol, Sequence, TypeVar

T = TypeVar("T")


# 1. Класс пользователя с поддержкой сортировки
@dataclass(order=True)
class User:
    id: int
    name: str
    login: str
    password: str = field(repr=False)
    email: Optional[str] = None
    address: Optional[str] = None

    def __post_init__(self):
        """Проверка обязательных полей"""
        if not self.name or not self.login or not self.password:
            raise ValueError("Name, login and password are required")


# 2. Протоколы репозитория
class DataRepositoryProtocol(Protocol[T]):
    @abstractmethod
    def get_all(self) -> Sequence[T]: ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]: ...

    @abstractmethod
    def add(self, item: T) -> None: ...

    @abstractmethod
    def update(self, item: T) -> None: ...

    @abstractmethod
    def delete(self, item: T) -> None: ...


class UserRepositoryProtocol(DataRepositoryProtocol[User]):
    @abstractmethod
    def get_by_login(self, login: str) -> Optional[User]: ...


# 3. Базовая реализация репозитория (JSON-хранилище)
class JsonRepository(DataRepositoryProtocol[T]):
    def __init__(self, file_path: str, entity_type: type):
        self.file_path = file_path
        self.entity_type = entity_type
        self.data: Dict[int, T] = {}
        self._load()

    def _load(self) -> None:
        """Загрузка данных из файла"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    raw_data = json.load(f)
                    self.data = {
                        int(k): self.entity_type(**v) for k, v in raw_data.items()
                    }
            except (json.JSONDecodeError, FileNotFoundError):
                self.data = {}

    def _save(self) -> None:
        """Сохранение данных в файл"""
        with open(self.file_path, "w") as f:
            json_data = {str(k): asdict(v) for k, v in self.data.items()}
            json.dump(json_data, f, indent=2)

    def get_all(self) -> Sequence[T]:
        return list(self.data.values())

    def get_by_id(self, id: int) -> Optional[T]:
        return self.data.get(id)

    def add(self, item: T) -> None:
        if not hasattr(item, "id"):
            raise ValueError("Entity must have 'id' attribute")

        if item.id in self.data:
            raise ValueError(f"Entity with id {item.id} already exists")

        self.data[item.id] = item
        self._save()

    def update(self, item: T) -> None:
        if item.id not in self.data:
            raise ValueError(f"Entity with id {item.id} not found")

        self.data[item.id] = item
        self._save()

    def delete(self, item: T) -> None:
        if item.id not in self.data:
            raise ValueError(f"Entity with id {item.id} not found")

        del self.data[item.id]
        self._save()


# 4. Специализированный репозиторий пользователей
class UserRepository(JsonRepository, UserRepositoryProtocol):
    def __init__(self, file_path: str):
        super().__init__(file_path, User)

    def get_by_login(self, login: str) -> Optional[User]:
        for user in self.data.values():
            if user.login == login:
                return user
        return None


# 5. Протокол сервиса авторизации
class AuthServiceProtocol(Protocol):
    @abstractmethod
    def sign_in(self, user: User) -> None: ...

    @abstractmethod
    def sign_out(self) -> None: ...

    @property
    @abstractmethod
    def is_authorized(self) -> bool: ...

    @property
    @abstractmethod
    def current_user(self) -> Optional[User]: ...


# 6. Реализация сервиса авторизации с автоматическим сохранением сессии
class FileAuthService(AuthServiceProtocol):
    SESSION_FILE = "current_session.json"

    def __init__(self, user_repo: UserRepositoryProtocol):
        self.user_repo = user_repo
        self._current_user: Optional[User] = None
        self._restore_session()

    def _restore_session(self) -> None:
        """Восстановление сессии из файла"""
        if os.path.exists(self.SESSION_FILE):
            try:
                with open(self.SESSION_FILE, "r") as f:
                    session_data = json.load(f)
                    user_id = session_data.get("user_id")

                    if user_id is not None:
                        user = self.user_repo.get_by_id(user_id)
                        if user:
                            self._current_user = user
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    def _save_session(self) -> None:
        """Сохранение текущей сессии в файл"""
        session_data = {
            "user_id": self._current_user.id if self._current_user else None
        }

        with open(self.SESSION_FILE, "w") as f:
            json.dump(session_data, f)

    def sign_in(self, user: User) -> None:
        """Авторизация пользователя"""
        # Проверка существования пользователя в репозитории
        db_user = self.user_repo.get_by_id(user.id)
        if not db_user:
            raise ValueError("User not found in repository")

        # Проверка совпадения логина и пароля
        if db_user.login != user.login or db_user.password != user.password:
            raise ValueError("Invalid login or password")

        self._current_user = db_user
        self._save_session()

    def sign_out(self) -> None:
        """Завершение сеанса"""
        self._current_user = None
        # Удаляем файл сессии
        if os.path.exists(self.SESSION_FILE):
            os.remove(self.SESSION_FILE)

    @property
    def is_authorized(self) -> bool:
        return self._current_user is not None

    @property
    def current_user(self) -> Optional[User]:
        return self._current_user


# 7. Демонстрация работы системы
if __name__ == "__main__":
    # Инициализация репозитория
    USER_DB_FILE = "users.json"
    user_repo = UserRepository(USER_DB_FILE)

    # Очистка БД для демонстрации
    if os.path.exists(USER_DB_FILE):
        os.remove(USER_DB_FILE)

    # Создание пользователей
    admin = User(
        id=1,
        name="Admin User",
        login="admin",
        password="secure123",
        email="admin@example.com",
    )

    manager = User(
        id=2,
        name="Manager User",
        login="manager",
        password="pass123",
        address="City Center, 123",
    )

    # Добавление пользователей в репозиторий
    user_repo.add(admin)
    user_repo.add(manager)

    # Инициализация сервиса авторизации
    auth_service = FileAuthService(user_repo)

    print("===== Демонстрация системы авторизации =====")

    # Попытка авторизации
    print("\n1. Авторизация администратора")
    try:
        auth_service.sign_in(admin)
        print(f"Успешная авторизация: {auth_service.current_user.name}")
        print(f"Статус авторизации: {auth_service.is_authorized}")
    except Exception as e:
        print(f"Ошибка авторизации: {str(e)}")

    # Выход из системы
    print("\n2. Выход из системы")
    auth_service.sign_out()
    print(f"Текущий пользователь: {auth_service.current_user}")
    print(f"Статус авторизации: {auth_service.is_authorized}")

    # Автоматическая авторизация при повторном запуске
    print("\n3. Автоматическая авторизация (имитация перезапуска)")
    new_auth_service = FileAuthService(user_repo)
    if new_auth_service.is_authorized:
        print(f"Автоматическая авторизация: {new_auth_service.current_user.name}")
    else:
        print("Автоматическая авторизация не выполнена")

    # Смена пользователя
    print("\n4. Смена пользователя")
    try:
        new_auth_service.sign_in(manager)
        print(f"Новый пользователь: {new_auth_service.current_user.name}")
    except Exception as e:
        print(f"Ошибка авторизации: {str(e)}")

    # Редактирование пользователя
    print("\n5. Редактирование пользователя")
    updated_admin = User(
        id=1,
        name="Updated Admin",
        login="admin_updated",
        password="new_secure_password",
        email="updated_admin@example.com",
    )

    user_repo.update(updated_admin)
    print("Данные администратора обновлены")

    # Попытка авторизации с обновленными данными
    print("\n6. Авторизация с обновленными данными")
    try:
        new_auth_service.sign_in(updated_admin)
        print(f"Успешная авторизация: {new_auth_service.current_user.name}")
        print(f"Email: {new_auth_service.current_user.email}")
    except Exception as e:
        print(f"Ошибка авторизации: {str(e)}")

    # Просмотр всех пользователей
    print("\n7. Список всех пользователей (отсортированный по имени):")
    users = sorted(user_repo.get_all())  # Используем встроенную сортировку
    for user in users:
        print(f"{user.id}: {user.name} ({user.login})")
