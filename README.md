# Android x86 Automation

**Автоматизация работы с Android x86 через ADB**

Учебный проект для автоматизации запуска Android x86, подключения через ADB и сбора логов.

---

##  Содержание

- [О проекте](#о-проекте)
- [Структура проекта](#структура-проекта)
- [Как это работает](#как-это-работает)
- [Структура кода](#структура-кода)
- [Установка](#установка)
- [Использование](#использование)
- [QEMU vs VirtualBox](#qemu-vs-virtualbox)
- [Запуск тестов](#запуск-тестов)
- [Примеры](#примеры)
- [Требования](#требования)

---

##  О проекте

Этот проект предоставляет Python-обвязку для:
-  Запуска Android x86 в QEMU
-  Подключения к Android через ADB
-  Выполнения ADB команд (версия, модель, экран)
-  Сбора и анализа логов Logcat
-  Автоматического тестирования через pytest

**Код универсален** и работает с любым эмулятором Android (QEMU, VirtualBox, Android Studio Emulator, физическое устройство).

---

##  Структура проекта

```
android_project/
├── src/
│   └── android_qemu.py          # Основной код программы
├── tests/
│   ├── test_android_qemu.py     # Тесты pytest (15 тестов)
│   └── test_cases.yaml          # Тест-кейсы в формате YAML    
├── logs/
│   └── logcat_*.log             # Собранные логи (создается автоматически)
├── Dockerfile                   # Docker конфигурация
├── docker-compose.yml    
├── requirements.txt             # Python зависимости
├── pytest.ini                   # Настройки pytest
└── README.md                    # Этот файл
```

### **Как это работает:**

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Python код    │────▶│   ADB (порт 5555)│────▶│    Android x86  │
│ android_qemu.py │     │                  │     │  (QEMU/VirtualBox)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │
         └───────▶ QEMU: Запуск/остановка через subprocess
                   VirtualBox: Только подключение к запущенной VM
```

### **Принцип работы:**

| Платформа | Запуск VM | Остановка VM | ADB команды |
|-----------|-----------|--------------|-------------|
| **QEMU** |  Да (`--launch-qemu`) |  Да (автоматически) |  Через ADB |
| **VirtualBox** |  Нет (вручную) |  Нет (вручную) |  Через ADB |
| **Физическое устройство** |  Нет |  Нет |  Через ADB |

### **Важно:**

> **QEMU:** Программа может запускать и останавливать эмулятор напрямую через `subprocess`.
> 
> **VirtualBox:** Программа только подключается к уже запущенной VM через ADB.
> 
> **ADB команды:** Работают одинаково для всех платформ через стандартный протокол ADB.

##  Структура кода

### **Файл: `src/android_qemu.py`**

| Класс/Функция | Назначение | Методы |
|---------------|------------|--------|
| **`ADBClient`** | Подключение и работа с ADB | `connect()`, `disconnect()`, `get_devices()`, `shell()`, `get_android_version()`, `get_model()`, `get_screen_size()` |
| **`LogcatCollector`** | Сбор и анализ логов | `start()`, `read_log()`, `search()`, `get_errors()`, `get_stats()` |
| **`main()`** | Точка входа, управление потоком | Парсинг аргументов, запуск QEMU, подключение ADB, сбор логов |

---

### **Класс `ADBClient`**

**Назначение:** Подключение к Android через ADB и выполнение команд.

```python
adb = ADBClient(host="127.0.0.1", port=5555)
adb.connect()                      # Подключиться
adb.get_devices()                  # Получить список устройств
adb.get_android_version()          # Версия Android
adb.get_model()                    # Модель устройства
adb.get_screen_size()              # Разрешение экрана
adb.shell("command")               # Выполнить любую shell команду
```

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `__init__(host, port)` | Инициализация клиента | - |
| `connect()` | Подключение к устройству | `bool` |
| `disconnect()` | Отключение от устройства | `bool` |
| `get_devices()` | Получить список устройств | `List[str]` |
| `shell(command)` | Выполнить shell команду | `str` или `None` |
| `get_android_version()` | Получить версию Android | `str` или `None` |
| `get_model()` | Получить модель устройства | `str` или `None` |
| `get_screen_size()` | Получить разрешение экрана | `str` или `None` |

---

### **Класс `LogcatCollector`**

**Назначение:** Сбор, сохранение и анализ логов Android (logcat).

```python
logcat = LogcatCollector(output_dir="./logs", device="127.0.0.1:5555")
logcat.start()                   # Собрать логи
logcat.get_stats()               # Статистика логов
logcat.get_errors()              # Получить ошибки
logcat.search("pattern")         # Поиск по логам
```

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `__init__(output_dir, device)` | Инициализация сборщика | - |
| `start()` | Собрать логи в файл | `str` (путь к файлу) |
| `read_log()` | Прочитать файл лога | `str` |
| `search(pattern)` | Поиск по логам | `List[str]` |
| `get_errors()` | Получить строки с ошибками (E/) | `List[str]` |
| `get_stats()` | Статистика логов | `dict` |

---

### **Функция `main()`**

**Назначение:** Главная точка входа. Управляет всем процессом:

1. Парсит аргументы командной строки
2. Запускает QEMU (если указано `--launch-qemu`)
3. Подключается к ADB
4. Получает информацию об устройстве
5. Собирает логи
6. Корректно завершает работу

---

##  Установка

### **1. Клонировать проект:**


### **2. Установить зависимости:**

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pytest>=7.0.0
pytest-cov>=4.0.0
pyyaml>=6.0
```

### **3. Проверить установку:**

```bash
pytest --version
adb version
```

---

##  Использование

### **Базовые команды:**

| Команда | Описание |
|---------|----------|
| `python src/android_qemu.py` | Подключиться к запущенному Android |
| `python src/android_qemu.py --help` | Показать справку |
| `python src/android_qemu.py --no-logcat` | Без сбора логов |
| `python src/android_qemu.py --port 5555` | Свой порт ADB |

---

### **Запуск с QEMU:**

```bash
python src/android_qemu.py --launch-qemu --iso "путь/к/android.iso" --disk "путь/к/disk.img"
```

**Параметры:**

| Параметр | Обязательный | Описание |
|----------|--------------|----------|
| `--launch-qemu` |  Да | Запустить QEMU |
| `--iso` |  Да | Путь к ISO образу Android-x86 |
| `--disk` |  Да | Путь к виртуальному диску |
| `--memory` |  Нет | RAM в MB (по умолчанию 2048) |

**Пример:**
```bash
python src/android_qemu.py --launch-qemu \
  --iso "C:/android_iso/android-x86_64-8.1-r6.iso" \
  --disk "C:/android/android.img" \
  --memory 4096
```

---

### **Запуск с VirtualBox:**

```bash
# 1. Запустить VM вручную в VirtualBox
# 2. Убедиться что проброс портов настроен (5555→5555)
# 3. Подключиться через скрипт:

python src/android_qemu.py
```

**VirtualBox уже запущен - скрипт автоматически подключится!**

---

##  QEMU vs VirtualBox

### **В чем разница?**

| Характеристика | QEMU | VirtualBox |
|----------------|------|------------|
| **Запуск через скрипт** |  Да (`--launch-qemu`) |  Нет (вручную) |
| **ADB подключение** |  Работает |  Работает |
| **Производительность** |  Медленнее |  Быстрее |


### **Важно:**

> **Код написан для QEMU** (по заданию), но **протестирован на VirtualBox** из-за проблем со стабильностью графики в QEMU. **ADB клиент универсален** и работает одинаково с любой платформой!


---

##  Запуск тестов

### **1. Запустить все тесты:**

```bash
cd C:\Users\Alena\projects\kasperski_prject
pytest tests/ -v
```

### **2. Запустить с отчетом:**

```bash
pytest tests/ -v --tb=short > test_report.txt
```

### **3. Запустить с покрытием:**

```bash
pytest tests/ -v --cov=src --cov-report=html
```

### **4. Запустить конкретный тест:**

```bash
pytest tests/test_android_qemu.py::TestADBClient::test_adb_client_init -v
```

### **5. Запустить по классу:**

```bash
pytest tests/test_android_qemu.py::TestLogcatCollector -v
```

---

### **Структура тестов:**

| Класс тестов | Описание | Количество |
|--------------|----------|------------|
| `TestToolsInstalled` | Проверка установки QEMU, ADB, qemu-img | 3 теста |
| `TestADBClient` | Тесты ADB клиента | 4 теста |
| `TestLogcatCollector` | Тесты сборщика логов | 6 тестов |
| `TestScriptExecution` | Тесты запуска скрипта | 2 теста |
| **Итого** | | **15 тестов** |

---

### **Ожидаемый результат:**

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2
collected 15 items

tests/test_android_qemu.py::TestToolsInstalled::test_qemu_installed PASSED
tests/test_android_qemu.py::TestToolsInstalled::test_adb_installed PASSED
tests/test_android_qemu.py::TestToolsInstalled::test_qemu_img_installed PASSED
tests/test_android_qemu.py::TestADBClient::test_adb_client_init PASSED
tests/test_android_qemu.py::TestADBClient::test_adb_client_init_default PASSED
tests/test_android_qemu.py::TestADBClient::test_adb_devices_command PASSED
tests/test_android_qemu.py::TestADBClient::test_adb_version_command PASSED
tests/test_android_qemu.py::TestLogcatCollector::test_logcat_init PASSED
tests/test_android_qemu.py::TestLogcatCollector::test_logcat_init_with_device PASSED
tests/test_android_qemu.py::TestLogcatCollector::test_logcat_directory_created PASSED
tests/test_android_qemu.py::TestLogcatCollector::test_logcat_search_empty PASSED
tests/test_android_qemu.py::TestLogcatCollector::test_logcat_get_errors_empty PASSED
tests/test_android_qemu.py::TestLogcatCollector::test_logcat_get_stats_empty PASSED
tests/test_android_qemu.py::TestScriptExecution::test_script_help PASSED
tests/test_android_qemu.py::TestScriptExecution::test_script_no_args PASSED

============================= 15 passed in 0.58s ==============================
```

---

##  Примеры использования

### **Пример 1: Подключение к запущенному Android**

```bash
# Android уже запущен в VirtualBox
python src/android_qemu.py
```

**Вывод:**
```
======================================================================
Android x86 Automation
Время: 2026-03-13 00:00:00.000000
======================================================================

🔌 Подключение к ADB на порт 5555...
✓ ADB подключен к 127.0.0.1:5555

======================================================================
ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ
======================================================================

✓ Найдено устройств: 1
  1. 127.0.0.1:5555

📱 Устройство: 127.0.0.1:5555
   • Android: 8.1.0
   • Модель: VirtualBox
   • Экран: Physical size: 1024x768

======================================================================
СБОР LOGCAT
======================================================================
✓ Лог сохранен: ./logs\logcat_20260313_000000.log
  Размер: 709156 байт

📊 Статистика:
   • Всего строк: 5889
   • Ошибок: 358
   • Предупреждений: 1684

======================================================================
✓ РАБОТА ЗАВЕРШЕНА УСПЕШНО
======================================================================
```

---

### **Пример 2: Запуск QEMU**

```bash
python src/android_qemu.py --launch-qemu \
  --iso "C:/android_iso/android-x86_64-8.1-r6.iso" \
  --disk "C:/android/android.img"
```

---

### **Пример 3: Без сбора логов**

```bash
python src/android_qemu.py --no-logcat
```

---

### **Пример 4: Свой порт ADB**

```bash
python src/android_qemu.py --port 5555
```

---

## 📋 Требования

### **Обязательные:**

| Компонент | Версия | Проверка |
|-----------|--------|----------|
| Python | 3.8+ | `python --version` |
| ADB | Любая | `adb version` |
| pytest | 7.0+ | `pytest --version` |

### **Для QEMU:**

| Компонент | Версия | Проверка |
|-----------|--------|----------|
| QEMU | 6.0+ | `qemu-system-x86_64 --version` |
| qemu-img | 6.0+ | `qemu-img --version` |

### **Для VirtualBox:**

| Компонент | Версия | Проверка |
|-----------|--------|----------|
| VirtualBox | 6.0+ | `VBoxManage --version` |
| Проброс портов | 5555→5555 | Настройки сети VM |

---
##  **Запуск в Docker**

### **Быстрый старт:**

```bash
# 1. Собрать и запустить
docker compose up

# 2. Запустить тесты
docker compose run --rm app pytest tests/ -v

# 3. Пересобрать (если менял код)
docker compose build --no-cache
docker compose up
```

---

### **Что покажет Docker:**

**При запуске `docker compose up`:**

```
======================================================================
Android x86 Automation
Время: 2026-03-13 00:00:00.000000
======================================================================

🔌 Подключение к ADB на порт 5555...
⚠ ADB не подключен

======================================================================
✓ РАБОТА ЗАВЕРШЕНА УСПЕШНО
======================================================================
app-1 exited with code 0
```

---

### **Что это значит:**

| Вывод | Значение |
|-------|----------|
| `Android x86 Automation` |  Скрипт запустился |
| `⚠ ADB не подключен` |  В Docker нет Android |
| `✓ РАБОТА ЗАВЕРШЕНА УСПЕШНО` |  Скрипт отработал без ошибок |
| `exited with code 0` |  Успешное завершение |

---

### **Доступные команды:**

```bash
# Показать справку
docker compose run --rm app python src/android_qemu.py --help

# Запустить без logcat
docker compose run --rm app python src/android_qemu.py --no-logcat

# Запустить тесты
docker compose run --rm app pytest tests/ -v

# Запустить с покрытием
docker compose run --rm app pytest tests/ -v --cov=src
```


##  Известные проблемы

### **1. QEMU: Графические артефакты**

**Проблема:** Android-x86 может не загрузиться в QEMU из-за проблем с графикой.

**Решение:** Использовать VirtualBox для стабильной работы.

---

### **2. ADB: Multiple devices**

**Проблема:** `error: more than one device/emulator`

**Решение:** Код автоматически выбирает первое устройство. Для явного указания:
```python
adb.device = "127.0.0.1:5555"  # Конкретное устройство
```

---

### **3. Logcat: Кодировка**

**Проблема:** Ошибки декодирования в логах.

**Решение:** Код использует `encoding='utf-8', errors='replace'` для обработки.

---