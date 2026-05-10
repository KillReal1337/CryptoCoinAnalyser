import sys
import requests
import pandas as pd
from dotenv import load_dotenv
import os

def test_environment():
    print("🧪 Тестирование окружения...")
    
    # Проверка Python версии
    print(f"✅ Python версия: {sys.version}")
    
    # Проверка импортов
    try:
        import requests
        import pandas
        from dotenv import load_dotenv
        print("✅ Все библиотеки импортируются")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Проверка .env файла
    load_dotenv()
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    if api_key:
        print("✅ .env файл загружен")
        print(f"✅ API ключ: {'*' * len(api_key)}")
    else:
        print("⚠️  API ключ не найден в .env")
    
    # Проверка виртуального окружения
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Виртуальное окружение активировано")
    else:
        print("⚠️  Виртуальное окружение не активировано")
    
    return True

if __name__ == "__main__":
    test_environment()