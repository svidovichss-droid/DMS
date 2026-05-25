# DataMatrix Quality Scanner

Профессиональный сканер качества Data Matrix кодов для промышленных линий.

## Возможности

- **Сканирование в реальном времени** - обнаружение и декодирование Data Matrix кодов с веб-камеры
- **Оценка качества по ISO 15415** - расчет параметров качества согласно международному стандарту
- **Режим конвейера** - автоматическое сканирование при смене кодов на линии
- **Статистика и отчеты** - журнал сканирований, экспорт данных, графики качества
- **Система сигнализации** - визуальные и звуковые оповещения при браке

## Требования

- Python 3.10+
- Windows 10/11
- Веб-камера с разрешением не менее 640x480
- USB 2.0 или выше

## Установка

### Из исходного кода

```bash
# Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/datamatrix-scanner.git
cd datamatrix-scanner

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python main.py
```

### Сборка EXE (Windows)

```bash
# Использование скрипта сборки (рекомендуется)
build.bat

# Или вручную:
# Установка PyInstaller
pip install -r requirements.txt

# Сборка EXE с использованием spec-файла
pyinstaller datamatrix_scanner.spec --clean

# Готовый EXE будет в папке dist/DataMatrixScanner.exe
```

#### Настройка иконки приложения

1. Создайте файл иконки `resources/icon.ico` (размер 256x256 пикселей)
2. В файле `datamatrix_scanner.spec` измените строку:
   ```python
   icon=None,  # Замените на: icon='resources/icon.ico',
   ```
3. Пересоберите приложение: `pyinstaller datamatrix_scanner.spec --clean`

## ISO 15415 Параметры качества

| Параметр | Описание | Порог |
|----------|----------|-------|
| SC | Symbol Contrast | ≥ 0.80 |
| ED | Module Edge Determinacy | ≥ 0.50 |
| AN | Axial Non-Uniformity | ≤ 0.08 |
| GN | Grid Non-Uniformity | ≤ 0.08 |
| UEC | Unused Error Correction | ≥ 0.50 |
| FPD | Fixed Pattern Damage | ≥ 0.60 |

## Оценки качества

| Оценка | Диапазон | Описание |
|--------|----------|----------|
| A | ≥ 3.5 | Отлично |
| B | ≥ 2.5 | Хорошо |
| C | ≥ 1.5 | Приемлемо |
| D | ≥ 0.5 | Плохо |
| F | < 0.5 | Брак |

## Структура проекта

```
datamatrix-scanner/
├── main.py                 # Точка входа
├── scanner/                # Модули сканера
│   ├── camera.py
│   ├── detector.py
│   ├── quality_analyzer.py
│   └── database.py
├── ui/                     # Пользовательский интерфейс
│   ├── main_window.py
│   ├── camera_panel.py
│   └── metrics_panel.py
├── utils/                  # Утилиты
│   ├── config.py
│   └── logger.py
└── resources/              # Ресурсы
    └── sounds/
```

## Лицензия

MIT License