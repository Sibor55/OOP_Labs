# OOP\_Labs: Object-Oriented Programming Laboratory Work

## Лабораторная работа 1 (Точки и векторы)

### Класс `Point2d`

* Свойства:

  * `x: int`
  * `y: int`
* Конструктор: `(x: int, y: int)`
* Ограничения:

  * `0 <= x <= WIDTH`
  * `0 <= y <= HEIGHT`
* Методы:

  * `__eq__` — сравнение на эквивалентность
  * `__str__`, `__repr__` — строковое представление

### Класс `Vector2d`

* Свойства:

  * `x: int`
  * `y: int`
* Конструкторы:

  * `(x: int, y: int)`
  * `(start: Point2d, end: Point2d)`
* Доступ к элементам:

  * `__getitem__`, `__setitem__`
  * `__iter__`, `__len__`
* Сравнение: `__eq__`
* Представление: `__str__`, `__repr__`
* Модуль вектора: `abs()` или отдельный метод
* Операции:

  * Сложение, вычитание, умножение и деление на число
* Произведения:

  * Скалярное: метод экземпляра и `@staticmethod`
  * Векторное: метод экземпляра и `@staticmethod`
  * Смешанное произведение

## Лабораторная работа 2 (Красивая консоль)

### Класс `Printer`

* Статический метод:

  ```python
  Printer.print(text: str, color: Color, position: Tuple[int, int], symbol: str)
  ```
* Экземпляр с фиксированным стилем:

  ```python
  with Printer(color: Color, position: Tuple[int, int], symbol: str) as printer:
      printer.print('text1')
      printer.print('text2')
  ```
* Поддержка ANSI-цветов (Enum)
* Использование шаблонов псевдошрифта из файла (txt/json/xml)

## Лабораторная работа 3 (Система логирования)

### Протокол/интерфейс `ILogFilter`

* Метод `match(self, text: str)`

### Реализации фильтра:

* `SimpleLogFilter`
* `ReLogFilter`

### Протокол `ILogHandler`

* Метод `handle(self, text: str)`

### Обработчики:

* `FileHandler`
* `SocketHandler`
* `ConsoleHandler`
* `SyslogHandler`

### Класс `Logger`

* Принимает список фильтров и обработчиков
* Метод `log(self, text: str)`

## Лабораторная работа 4 (Валидация и автообновление)

### Протокол `IPropertyChangedListener`

* Метод `on_property_changed(obj: T, property_name)`

### Протокол `INotifyDataChanged`

* Методы:

  * `add_property_changed_listener`
  * `remove_property_changed_listener`

### Протокол `IPropertyChangingListener`

* Метод `on_property_changing(obj: T, property_name, old_value, new_value) -> bool`

### Протокол `INotifyDataChanging`

* Методы:

  * `add_property_changing_listener`
  * `remove_property_changing_listener`

### Демонстрация:

* Несколько слушателей и валидаторов
* Работа классов с оповещением и валидацией

## Лабораторная работа 5 (Система авторизации)

### Класс `User`

* Атрибуты:

  * `id`, `name`, `login`, `password`, `email?`, `address?`
* Сортировка по `name`
* Использование `dataclass`

### Интерфейс `IDataRepository[T]`

* CRUD методы

### Интерфейс `IUserRepository` (наследует `IDataRepository[User]`)

* Метод `get_by_login(self, login: str)`

### Реализация `DataRepository[T]`

* Сериализация: pickle/json/xml

### Реализация `UserRepository`

### Интерфейс `IAuthService`

* Методы:

  * `sign_in`, `sign_out`, `is_authorized`, `current_user`

### Реализация с хранением состояния пользователя в файле

* Демонстрация:

  * Добавление/редактирование
  * Авторизация
  * Автоавторизация

## Лабораторная работа 6\* (Виртуальная клавиатура)

### Классы:

* `Keyboard`, `KeyCommand`, `VolumeUpCommand`, `VolumeDownCommand`, `MediaPlayerCommand`, `KeyboardStateSaver`

### Команды:

* Печать символа (одним классом)
* Увеличение/уменьшение громкости
* Запуск медиаплеера
* undo/redo

### Сохранение ассоциаций:

* Паттерн Memento
* Формат хранения: JSON

### Вывод в консоль и текстовый файл

## Лабораторная работа 7 (Внедрение зависимостей)

### Класс `Injector`

* Жизненные циклы: `PerRequest`, `Scoped`, `Singleton`
* Регистрация зависимостей и фабрик
* Получение экземпляров по интерфейсу
* `with` блок для `Scoped`

### Интерфейсы:

* `interface1`, `interface2`, `interface3`
* Классы под каждый интерфейс (debug/release)

### Конфигурации:

* Две разные регистрации

### Демонстрация:

* Получение и использование экземпляров через инжектор
