# Используем Ubuntu 22.04 как базовый образ
FROM ubuntu:22.04

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    qemu-system-x86 \
    qemu-utils \
    android-tools-adb \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Создаем symlink python -> python3 (чтобы работала команда "python")
RUN ln -s /usr/bin/python3 /usr/bin/python

# Рабочая директория
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src/ ./src/
COPY tests/ ./tests/

# Копируем конфигурационные файлы
COPY pytest.ini .
COPY .gitignore .

# Создаем директории для логов и данных
RUN mkdir -p /app/logs /app/android_iso /app/android

# Команда по умолчанию (можно переопределить при запуске)
CMD ["python", "src/android_qemu.py", "--help"]
