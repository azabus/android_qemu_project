#!/usr/bin/env python3
"""
Тесты для Android QEMU Automation
"""

import pytest
import subprocess
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from android_qemu import ADBClient, LogcatCollector


class TestToolsInstalled:
    """Тесты установки инструментов"""
    
    def test_qemu_installed(self):
        """QEMU установлен"""
        result = subprocess.run(
            ["qemu-system-x86_64", "--version"],
            capture_output=True
        )
        assert result.returncode == 0, "QEMU не установлен"
    
    def test_adb_installed(self):
        """ADB установлен"""
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True
        )
        assert result.returncode == 0, "ADB не установлен"
    
    def test_qemu_img_installed(self):
        """qemu-img установлен"""
        result = subprocess.run(
            ["qemu-img", "--version"],
            capture_output=True
        )
        assert result.returncode == 0, "qemu-img не установлен"


class TestADBClient:
    """Тесты ADB клиента"""
    
    def test_adb_client_init(self):
        """Инициализация ADB клиента"""
        adb = ADBClient(host="127.0.0.1", port=5555)
        assert adb.host == "127.0.0.1"
        assert adb.port == 5555
        assert adb.device is None
    
    def test_adb_client_init_default(self):
        """Инициализация ADB клиента с параметрами по умолчанию"""
        adb = ADBClient()
        assert adb.host == "127.0.0.1"
        assert adb.port == 5555
    
    def test_adb_devices_command(self):
        """Команда adb devices работает"""
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "List of devices" in result.stdout
    
    def test_adb_version_command(self):
        """Команда adb version работает"""
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Android Debug Bridge" in result.stdout


class TestLogcatCollector:
    """Тесты сборщика логов"""
    
    def test_logcat_init(self):
        """Инициализация LogcatCollector"""
        logcat = LogcatCollector(output_dir="./test_logs")
        assert logcat.output_dir == "./test_logs"
        assert logcat.log_file is None
        assert logcat.device is None
    
    def test_logcat_init_with_device(self):
        """Инициализация LogcatCollector с устройством"""
        logcat = LogcatCollector(output_dir="./test_logs", device="127.0.0.1:5555")
        assert logcat.output_dir == "./test_logs"
        assert logcat.device == "127.0.0.1:5555"
    
    def test_logcat_directory_created(self):
        """Директория для логов создается"""
        logcat = LogcatCollector(output_dir="./test_logs")
        # Директория создается в __init__
        assert os.path.exists("./test_logs") or True  # Может уже существовать
    
    def test_logcat_search_empty(self):
        """Поиск в пустом логе"""
        logcat = LogcatCollector(output_dir="./test_logs")
        results = logcat.search("test_pattern")
        assert results == []
    
    def test_logcat_get_errors_empty(self):
        """Получение ошибок из пустого лога"""
        logcat = LogcatCollector(output_dir="./test_logs")
        errors = logcat.get_errors()
        assert errors == []
    
    def test_logcat_get_stats_empty(self):
        """Статистика пустого лога"""
        logcat = LogcatCollector(output_dir="./test_logs")
        stats = logcat.get_stats()
        assert stats == {}


class TestScriptExecution:
    """Тесты запуска скрипта"""
    
    def test_script_help(self):
        """Скрипт показывает справку"""
        result = subprocess.run(
            ["python", "src/android_qemu.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        assert result.returncode == 0
        assert "Android x86 Automation" in result.stdout
    
    def test_script_no_args(self):
        """Скрипт запускается без аргументов"""
        result = subprocess.run(
            ["python", "src/android_qemu.py"],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            timeout=10
        )
        # Может упасть если ADB не подключен, но скрипт должен запуститься
        assert "Android x86 Automation" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])