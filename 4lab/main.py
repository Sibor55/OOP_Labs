# https://en.wikipedia.org/wiki/Observer_pattern !!!
from abc import abstractmethod
from typing import Any, List, Protocol, TypeVar

T = TypeVar("T") # Тип объекта, за которым следят слушатели


# 1. Протокол слушателя изменений свойства (после изменения) 
# (Observer Pattern - слушатель получает уведомления об изменениях)
class PropertyChangedListenerProtocol(Protocol):
    @abstractmethod
    def on_property_changed(self, obj: T, property_name: str) -> None:
        """
        Вызывается после изменения свойства объекта.

        Args:
            obj: Объект, свойство которого изменилось
            property_name: Имя измененного свойства
        """
        ...


# 2. Протокол для управления слушателями изменений 
class DataChangedProtocol(Protocol):
    @abstractmethod
    def add_property_changed_listener(
        self, listener: PropertyChangedListenerProtocol
    ) -> None:
        """
        Добавляет слушателя изменений свойств.

        Args:
            listener: Экземпляр слушателя
        """
        ...

    @abstractmethod
    def remove_property_changed_listener(
        self, listener: PropertyChangedListenerProtocol
    ) -> None:
        """
        Удаляет слушателя изменений свойств.

        Args:
            listener: Экземпляр слушателя
        """
        ...


# 3. Базовый класс с поддержкой уведомлений об изменениях 
# (Observable - объект, за которым можно наблюдать)
class ObservableModel(DataChangedProtocol):
    def __init__(self) -> None:
        # Список слушателей
        self._listeners: List[PropertyChangedListenerProtocol] = []

    def add_property_changed_listener(
        self, listener: PropertyChangedListenerProtocol
    ) -> None:
        # Проверка на уникальность
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_property_changed_listener(
        self, listener: PropertyChangedListenerProtocol
    ) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_property_changed(self, property_name: str) -> None:
        """Уведомляет всех слушателей об изменении свойства"""
        #Итерация по копии списка при изменении во время уведомления
        for listener in self._listeners:
            listener.on_property_changed(self, property_name)


# 4. Протокол слушателя валидации изменений (до изменения) 
# (Валидатор - проверяет допустимость изменений ДО их применения)
class PropertyChangingListenerProtocol(Protocol):
    @abstractmethod
    def on_property_changing(
        self, obj: T, property_name: str, old_value: Any, new_value: Any
    ) -> bool:
        """
        Вызывается перед изменением свойства для валидации.

        Args:
            obj: Целевой объект
            property_name: Имя изменяемого свойства
            old_value: Текущее значение свойства
            new_value: Предлагаемое новое значение

        Returns:
            bool: True если изменение разрешено, False для отмены
        """
        ...


# 5. Протокол для управления валидаторами изменений
class DataChangingProtocol(Protocol):
    @abstractmethod
    def add_property_changing_listener(
        self, listener: PropertyChangingListenerProtocol
    ) -> None: ...

    @abstractmethod
    def remove_property_changing_listener(
        self, listener: PropertyChangingListenerProtocol
    ) -> None: ...


# 6. Класс с поддержкой валидации изменений и уведомлений
class ValidatableModel(ObservableModel, DataChangingProtocol):
    def __init__(self) -> None:
        super().__init__()
        self._validators: List[PropertyChangingListenerProtocol] = []

    def add_property_changing_listener(
        self, listener: PropertyChangingListenerProtocol
    ) -> None:
        if listener not in self._validators:
            self._validators.append(listener)

    def remove_property_changing_listener(
        self, listener: PropertyChangingListenerProtocol
    ) -> None:
        if listener in self._validators:
            self._validators.remove(listener)

    def _validate_property_change(
        self, property_name: str, old_value: Any, new_value: Any
    ) -> bool:
        """Проверяет изменение через всех валидаторов"""
        for validator in self._validators:
            if not validator.on_property_changing(
                self, property_name, old_value, new_value
            ):
                return False
        return True

    def _set_property(
        self, property_name: str, current_value: Any, new_value: Any
    ) -> bool:
        """
        Безопасное обновление свойства с валидацией и уведомлением

        Args:
            property_name: Имя свойства
            current_value: Текущее значение
            new_value: Новое значение

        Returns:
            bool: Успешность изменения
        """
        # Проверка необходимости изменений
        if current_value == new_value:
            return False

        # Валидация изменения
        if not self._validate_property_change(property_name, current_value, new_value):
            return False

        # Применение изменения (защищенные свойства используют префикс '_')
        setattr(self, f"_{property_name}", new_value)
        self._notify_property_changed(property_name)
        return True


# 7. Пример бизнес-модели с наблюдаемыми свойствами
class Person(ValidatableModel):
    def __init__(self, name: str, age: int) -> None:
        super().__init__()
        self._name = name
        self._age = age
# Свойства с контролируемым доступом
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._set_property("name", self._name, value)

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        self._set_property("age", self._age, value)


# 8. Реализация слушателей и валидаторов 
class Logger(PropertyChangedListenerProtocol):
    def on_property_changed(self, obj: Any, property_name: str) -> None:
        print(
            f"[Изменение] {obj.__class__.__name__}.{property_name} = {getattr(obj, property_name)}"
        )


class AgeValidator(PropertyChangingListenerProtocol):
    def on_property_changing(
        self, obj: Any, property_name: str, old_value: Any, new_value: Any
    ) -> bool:
        if property_name == "age":
            if not isinstance(new_value, int):
                print("Ошибка: Возраст должен быть целым числом")
                return False
            if new_value < 0:
                print("Ошибка: Возраст не может быть отрицательным")
                return False
            if new_value > 120:
                print("Ошибка: Недопустимый возраст (>120)")
                return False
        return True


class NameValidator(PropertyChangingListenerProtocol):
    def on_property_changing(
        self, obj: Any, property_name: str, old_value: Any, new_value: Any
    ) -> bool:
        if property_name == "name":
            if not isinstance(new_value, str):
                print("Ошибка: Имя должно быть строкой")
                return False
            if len(new_value.strip()) == 0:
                print("Ошибка: Имя не может быть пустым")
                return False
            if len(new_value) > 50:
                print("Ошибка: Слишком длинное имя (>50 символов)")
                return False
        return True


# 9. Демонстрация работы системы
if __name__ == "__main__":
    # Создаем экземпляр модели
    person = Person("Иван", 30)

    # Создаем и регистрируем слушателей
    logger = Logger()
    age_validator = AgeValidator()
    name_validator = NameValidator()

    person.add_property_changed_listener(logger)
    person.add_property_changing_listener(age_validator)
    person.add_property_changing_listener(name_validator)

    print("---- Корректные изменения ----")
    person.name = "Мария"  # Успешное изменение
    person.age = 25  # Успешное изменение

    print("\n---- Некорректные изменения ----")
    person.name = ""  # Пустое имя (блокировка)
    person.age = -5  # Отрицательный возраст (блокировка)
    person.age = "старый"  # Неверный тип (блокировка)

    print("\n---- Проверка текущих значений ----")
    print(f"Имя: {person.name}, Возраст: {person.age}")

    # Удаление валидатора и повторная попытка
    person.remove_property_changing_listener(name_validator)
    print("\n---- Изменение после удаления валидатора ----")
    person.name = ""  # Проходит, т.к. валидатор удален
