
"""
Android x86 Automation
Подключается к Android через ADB (порт 5555)
"""

import subprocess
import time
import os
import argparse
from datetime import datetime
from typing import Optional, List


class ADBClient:
    """Клиент для ADB команд"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5555):
        self.host = host
        self.port = port
        self.device: Optional[str] = None
    
    def connect(self) -> bool:
        """Подключиться к устройству"""
        cmd = f"adb connect {self.host}:{self.port}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if "connected" in result.stdout.lower() or "already" in result.stdout.lower():
            print(f"✓ ADB подключен к {self.host}:{self.port}")
            return True
        else:
            print(f"✗ ADB ошибка: {result.stderr}")
            return False
    
    def disconnect(self) -> bool:
        """Отключиться от устройства"""
        cmd = f"adb disconnect {self.host}:{self.port}"
        subprocess.run(cmd, shell=True, capture_output=True)
        return True
    
    def get_devices(self) -> List[str]:
        """Получить список устройств"""
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
        devices = []
        
        for line in result.stdout.split("\n")[1:]:
            if line.strip() and "\t" in line:
                parts = line.split("\t")
                serial = parts[0]
                state = parts[1] if len(parts) > 1 else ""
                if state == "device":
                    devices.append(serial)
        
        if devices:
            self.device = devices[0]
        
        return devices
    
    def shell(self, command: str) -> Optional[str]:
        """Выполнить shell команду"""
        if not self.device:
            devices = self.get_devices()
            if not devices:
                return None
        
        cmd = f"adb -s {self.device} shell {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def get_android_version(self) -> Optional[str]:
        """Получить версию Android"""
        return self.shell("getprop ro.build.version.release")
    
    def get_model(self) -> Optional[str]:
        """Получить модель устройства"""
        return self.shell("getprop ro.product.model")
    
    def get_screen_size(self) -> Optional[str]:
        """Получить разрешение экрана"""
        return self.shell("wm size")


class LogcatCollector:
    """Сбор логов Logcat"""
    
    def __init__(self, output_dir: str = "./logs", device: str = None):
        self.output_dir = output_dir
        self.device = device
        self.log_file: Optional[str] = None
        os.makedirs(output_dir, exist_ok=True)
    
    def start(self, duration: int = 10) -> Optional[str]:
        """Начать сбор логов"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.output_dir, f"logcat_{timestamp}.log")
        
        # Формируем команду с указанием устройства
        if self.device:
            cmd = f"adb -s {self.device} logcat -v time -d"
        else:
            cmd = f"adb logcat -v time -d"
        
        # Запускаем с явной кодировкой utf-8 и errors='replace'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        # Записываем в файл
        if result.returncode == 0 and result.stdout:
            with open(self.log_file, "w", encoding='utf-8', errors='replace') as f:
                f.write(result.stdout)
            
            print(f"✓ Лог сохранен: {self.log_file}")
            print(f"  Размер: {len(result.stdout)} байт")
            return self.log_file
        else:
            print(f"✗ Ошибка сбора логов: {result.stderr}")
            return None
    
    def read_log(self) -> str:
        """Прочитать лог"""
        if self.log_file and os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding='utf-8', errors='ignore') as f:
                return f.read()
        return ""
    
    def search(self, pattern: str) -> List[str]:
        """Поиск по логу"""
        log_content = self.read_log()
        if not log_content:
            return []
        
        return [line.strip() for line in log_content.split("\n") if pattern.lower() in line.lower()]
    
    def get_errors(self) -> List[str]:
        """Получить ошибки"""
        return self.search("E/")
    
    def get_stats(self) -> dict:
        """Статистика логов"""
        log_content = self.read_log()
        if not log_content:
            return {}
        
        lines = log_content.split("\n")
        return {
            "total_lines": len(lines),
            "errors": len([l for l in lines if "E/" in l]),
            "warnings": len([l for l in lines if "W/" in l]),
            "file": self.log_file
        }


def main():
    """Основная функция"""
    print("=" * 70)
    print("Android x86 Automation")
    print(f"Время: {datetime.now()}")
    print("=" * 70)
    
    parser = argparse.ArgumentParser(
        description="Подключение к Android через ADB и выполнение команд",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python android_qemu.py
  python android_qemu.py --port 5555
  python android_qemu.py --no-logcat
  python android_qemu.py --launch-qemu --iso "путь/к/android.iso" --disk "путь/к/disk.img"
        """
    )
    
    parser.add_argument("--port", type=int, default=5555, help="ADB порт (по умолчанию: 5555)")
    parser.add_argument("--no-logcat", action="store_true", help="Не собирать logcat")
    parser.add_argument("--launch-qemu", action="store_true", help="Запустить QEMU")
    parser.add_argument("--iso", help="Путь к ISO образу (для --launch-qemu)")
    parser.add_argument("--disk", help="Путь к диску (для --launch-qemu)")
    parser.add_argument("--memory", type=int, default=2048, help="RAM для QEMU в MB")
    
    args = parser.parse_args()
    
    # Запуск QEMU если нужно
    if args.launch_qemu:
        if not args.iso or not args.disk:
            print("\n✗ Ошибка: Для запуска QEMU нужны --iso и --disk")
            return 1
        
        if not os.path.exists(args.iso):
            print(f"\n✗ ISO образ не найден: {args.iso}")
            return 1
        
        print(f"\n📁 ISO: {args.iso}")
        print(f"📁 Диск: {args.disk}")
        print(f"💾 RAM: {args.memory} MB")
        
        cmd = (
            f'qemu-system-x86_64 -m {args.memory} -smp 2 '
            f'-cdrom "{args.iso}" -hda "{args.disk}" -boot d -vga std -vnc :0 '
            f'-netdev user,id=net0,hostfwd=tcp::5555-:5555 -device e1000,netdev=net0'
        )
        
        print(f"\n🚀 Запуск QEMU...")
        qemu_process = subprocess.Popen(cmd, shell=True)
        time.sleep(3)
        
        if qemu_process.poll() is None:
            print(f"✓ QEMU запущен (PID: {qemu_process.pid})")
            print("⏳ Ожидание загрузки (120 сек)...")
            time.sleep(120)
        else:
            print("✗ QEMU не запустился")
            return 1
    
    # Подключение к Android
    print(f"\n🔌 Подключение к ADB на порт {args.port}...")
    adb = ADBClient(port=args.port)
    
    if not adb.connect():
        print("\n⚠ ADB не подключен")
        return 1
    
    # Информация об устройстве
    print("\n" + "=" * 70)
    print("ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ")
    print("=" * 70)
    
    devices = adb.get_devices()
    if devices:
        print(f"\n✓ Найдено устройств: {len(devices)}")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
        
        if adb.device:
            print(f"\n📱 Устройство: {adb.device}")
            print(f"   • Android: {adb.get_android_version() or 'неизвестно'}")
            print(f"   • Модель: {adb.get_model() or 'неизвестно'}")
            print(f"   • Экран: {adb.get_screen_size() or 'неизвестно'}")
    
    # Сбор логов
    if not args.no_logcat:
        print("\n" + "=" * 70)
        print("СБОР LOGCAT")
        print("=" * 70)
        
        logcat = LogcatCollector(device=adb.device)
        logcat.start()
        
        stats = logcat.get_stats()
        if stats and "error" not in stats:
            print(f"\n📊 Статистика:")
            print(f"   • Всего строк: {stats.get('total_lines', 0)}")
            print(f"   • Ошибок: {stats.get('errors', 0)}")
            print(f"   • Предупреждений: {stats.get('warnings', 0)}")
    
    # Завершение
    print("\n" + "=" * 70)
    print("✓ РАБОТА ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 70)
    
    adb.disconnect()
    
    if args.launch_qemu and 'qemu_process' in locals():
        input("\nНажмите Enter для остановки QEMU...")
        qemu_process.terminate()
    
    print(f"Время: {datetime.now()}")
    return 0


if __name__ == "__main__":
    exit(main())