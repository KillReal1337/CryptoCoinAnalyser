#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crypto Analysis Suite - Основная программа
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Добавляем текущую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

def main():
    """Основная функция программы"""
    print("🚀 Запуск Crypto Analysis Suite...")
    print("="*60)
    
    try:
        # Импортируем модули здесь, чтобы отлавливать ошибки импорта
        from cmc_api import CoinMarketCapAPI
        from contract_processor import ContractProcessor
        from utils import display_crypto_table, get_user_choice, format_timestamp
        from profit_analyzer import ProfitAnalyzer
        
        # Инициализация API
        cmc_api = CoinMarketCapAPI()
        
        # Инициализация процессора
        external_api_url = os.getenv('EXTERNAL_API_URL')
        external_api_key = os.getenv('EXTERNAL_API_KEY')
        processor = ContractProcessor(external_api_url, external_api_key)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта модуля: {e}")
        print("\n📦 Установите зависимости:")
        print("pip install requests python-dotenv")
        input("\nНажмите Enter для выхода...")
        return
    except ValueError as e:
        print(f"❌ {e}")
        print("\n📝 Настройте API ключи в файле .env:")
        print("COINMARKETCAP_API_KEY=ваш_ключ_coinmarketcap")
        print("ZAPPER_API_KEY=ваш_ключ_zapper (опционально)")
        input("\nНажмите Enter для выхода...")
        return
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        input("\nНажмите Enter для выхода...")
        return
    
    # Главный цикл программы
    while True:
        print("\n" + "="*60)
        print("🎯 CRYPTO ANALYSIS SUITE - ОСНОВНОЕ МЕНЮ")
        print("="*60)
        print("1. 🚀 Топ 20 растущих криптовалют")
        print("2. 🔗 Получить контракты растущих монет")
        print("3. 👛 Топ 5 кошельков по заработку (24ч)")
        print("4. 📊 Детальный анализ кошелька")
        print("5. 🔍 Поиск держателей токенов")
        print("6. 📈 Анализ за 7 дней")
        print("7. 🔗 Проверить подключения API")
        print("8. 📋 Показать настройки")
        print("9. 📊 Общая статистика рынка")
        print("10. 💰 Анализ держателей растущих токенов")
        print("11. 🎯 Анализ конкретных токенов из списка")
        print("0. ❌ Выход")
        
        choice = input("\nВыберите опцию: ").strip()
        
        if choice == '1':
            # Топ 20 растущих
            print("\n" + "="*60)
            print("🚀 ТОП 20 РАСТУЩИХ КРИПТОВАЛЮТ")
            print("="*60)
            
            try:
                data = cmc_api.get_top_gainers_with_contracts(limit=20)
                if data:
                    display_crypto_table(data, "🚀 ТОП 20 РАСТУЩИХ КРИПТОВАЛЮТ:")
                else:
                    print("❌ Не удалось получить данные")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '2':
            # Получить контракты
            print("\n" + "="*60)
            print("🔗 ПОЛУЧЕНИЕ КОНТРАКТНЫХ АДРЕСОВ")
            print("="*60)
            
            try:
                limit = int(input("Сколько криптовалют проверить? (рек. 30): ") or "30")
                limit = min(limit, 50)
            except ValueError:
                print("❌ Ошибка: введите число")
                continue
            
            try:
                data = cmc_api.get_top_gainers_with_contracts(limit=limit)
                
                if data:
                    contracts = processor.extract_contracts(data)
                    
                    if contracts:
                        print(f"\n✅ Найдено {len(contracts)} контрактных адресов")
                        
                        for i, contract in enumerate(contracts[:5], 1):
                            print(f"{i}. {contract['symbol']}: {contract['contract_address']}")
                        
                        # Сохраняем
                        save = input("\n💾 Сохранить контракты? (да/нет): ").lower()
                        if save in ['да', 'д', 'yes', 'y']:
                            filename = f'contracts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                            processor.save_wallets_to_file(contracts, filename)
                    else:
                        print("❌ Контрактные адресы не найдены")
                else:
                    print("❌ Не удалось получить данные")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '3':
            # Топ 5 кошельков за 24ч
            print("\n" + "="*60)
            print("👛 ТОП 5 КОШЕЛЬКОВ ЗА 24 ЧАСА")
            print("="*60)
            
            if not processor.zapper_api:
                print("❌ Zapper API не настроен")
                print("📝 Добавьте в .env: ZAPPER_API_KEY=ваш_ключ")
                continue
            
            try:
                top_wallets = processor.find_top_trading_wallets(
                    sample_wallets=None,
                    days=1,
                    top_n=5
                )
                
                if top_wallets:
                    from utils import display_top_wallets
                    display_top_wallets(top_wallets)
                    
                    # Сохраняем
                    save = input("\n💾 Сохранить результаты? (да/нет): ").lower()
                    if save in ['да', 'д', 'yes', 'y']:
                        processor.save_wallets_to_file(top_wallets)
                else:
                    print("❌ Не удалось найти кошельки")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '4':
            # Детальный анализ кошелька
            print("\n" + "="*60)
            print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ КОШЕЛЬКА")
            print("="*60)
            
            wallet_address = input("Введите адрес кошелька (0x...): ").strip()
            if not wallet_address or not wallet_address.startswith('0x'):
                print("❌ Введите корректный адрес кошелька")
                continue
            
            if not processor.zapper_api:
                print("❌ Zapper API не настроен")
                print("📝 Добавьте в .env: ZAPPER_API_KEY=ваш_ключ")
                continue
            
            print(f"\n🔍 Анализ кошелька {wallet_address[:10]}...")
            
            try:
                detailed_analysis = processor.analyze_wallet_advanced(wallet_address, days=7)
                
                if 'error' in detailed_analysis:
                    print(f"❌ Ошибка: {detailed_analysis['error']}")
                else:
                    from utils import display_wallet_details
                    display_wallet_details(detailed_analysis)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '5':
            # Поиск держателей токенов
            print("\n" + "="*60)
            print("👥 ПОИСК ДЕРЖАТЕЛЕЙ ТОКЕНОВ")
            print("="*60)
            
            if not processor.zapper_api:
                print("❌ Zapper API не настроен")
                print("📝 Добавьте в .env: ZAPPER_API_KEY=ваш_ключ")
                continue
            
            # Сначала получаем контракты
            try:
                limit = int(input("Сколько растущих токенов проверить? (рек. 3): ") or "3")
                limit = min(limit, 5)
            except ValueError:
                print("❌ Ошибка: введите число")
                continue
            
            print(f"\n🔍 Получение топ {limit} растущих токенов...")
            
            try:
                crypto_data = cmc_api.get_top_gainers_with_contracts(limit=limit)
                
                if crypto_data:
                    contracts = processor.extract_contracts(crypto_data)
                    
                    if contracts:
                        print(f"\n🔍 Поиск держателей для {len(contracts)} токенов...")
                        
                        # Получаем держателей для каждого токена
                        holders_data = processor.find_top_wallets_for_tokens(contracts, wallets_per_token=10)
                        
                        if holders_data:
                            print(f"\n✅ Найдены держатели:")
                            for symbol, data in holders_data.items():
                                print(f"\n{symbol}: {data['total_holders']} держателей")
                                for i, holder in enumerate(data['holders'][:3], 1):
                                    # ВЫВОДИМ ПОЛНЫЙ АДРЕС
                                    address = holder.get('address', '')
                                    display_name = holder.get('display_name', '')
                                    balance = holder.get('balance', '0')
                                    print(f"  {i}. Адрес: {address}")
                                    if display_name:
                                        print(f"     Имя: {display_name}")
                                    print(f"     Баланс: {balance} токенов")
                        else:
                            print("❌ Не удалось получить держателей")
                    else:
                        print("❌ Контрактные адресы не найдены")
                else:
                    print("❌ Не удалось получить данные")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '6':
            # Анализ за 7 дней
            print("\n" + "="*60)
            print("📈 АНАЛИЗ КОШЕЛЬКОВ ЗА 7 ДНЕЙ")
            print("="*60)
            
            if not processor.zapper_api:
                print("❌ Zapper API не настроен")
                print("📝 Добавьте в .env: ZAPPER_API_KEY=ваш_ключ")
                continue
            
            try:
                top_wallets = processor.find_top_trading_wallets(
                    sample_wallets=None,
                    days=7,
                    top_n=5
                )
                
                if top_wallets:
                    from utils import display_top_wallets
                    display_top_wallets(top_wallets)
                    
                    # Сохраняем
                    save = input("\n💾 Сохранить результаты? (да/нет): ").lower()
                    if save in ['да', 'д', 'yes', 'y']:
                        processor.save_wallets_to_file(top_wallets)
                else:
                    print("❌ Не удалось найти кошельки")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '7':
            # Проверка подключений
            print("\n" + "="*60)
            print("🔍 ПРОВЕРКА ПОДКЛЮЧЕНИЙ API")
            print("="*60)
            
            print("\n1. CoinMarketCap API:")
            try:
                success, message = cmc_api.test_connection()
                print(f"   {message}")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
            
            print("\n2. Zapper API:")
            if processor.zapper_api:
                try:
                    success, message = processor.zapper_api.test_connection()
                    print(f"   {message}")
                except Exception as e:
                    print(f"   ❌ Ошибка: {e}")
            else:
                print("   ❌ Zapper API не инициализирован")
                print("   📝 Добавьте в .env: ZAPPER_API_KEY=ваш_ключ")
            
            print("\n3. Общая информация:")
            print(f"   • Время: {format_timestamp()}")
            print(f"   • Директория: {os.getcwd()}")
        
        elif choice == '8':
            # Показать настройки
            print("\n" + "="*60)
            print("⚙️  НАСТРОЙКИ ПРОГРАММЫ")
            print("="*60)
            
            cmc_key = os.getenv('COINMARKETCAP_API_KEY')
            zapper_key = os.getenv('ZAPPER_API_KEY')
            
            print(f"\nCoinMarketCap API: {'✅ Настроен' if cmc_key and cmc_key != 'your_api_key_here' else '❌ Не настроен'}")
            print(f"Zapper API: {'✅ Настроен' if zapper_key and zapper_key != 'your_zapper_api_key_here' else '❌ Не настроен'}")
            print(f"\nТекущая директория: {os.getcwd()}")
            print(f"Файл .env: {'✅ Найден' if os.path.exists('.env') else '❌ Не найден'}")
            
            if os.path.exists('.env'):
                print("\nСодержимое .env (первые 200 символов):")
                try:
                    with open('.env', 'r') as f:
                        content = f.read(200)
                        print(f"   {content}")
                        if len(content) == 200:
                            print("   ... (файл длиннее 200 символов)")
                except:
                    print("   Не удалось прочитать файл")
        
        elif choice == '9':
            # Общая статистика рынка
            print("\n" + "="*60)
            print("📊 ОБЩАЯ СТАТИСТИКА РЫНКА")
            print("="*60)
            
            try:
                market_overview = cmc_api.get_market_overview()
                
                if market_overview:
                    print(f"\n💰 Общая рыночная капитализация: ${market_overview['total_market_cap']:,.0f}")
                    print(f"📈 Общий объем за 24ч: ${market_overview['total_volume_24h']:,.0f}")
                    print(f"🏆 Доминирование BTC: {market_overview['btc_dominance']:.2f}%")
                    print(f"🔷 Доминирование ETH: {market_overview['eth_dominance']:.2f}%")
                    print(f"🔢 Активных криптовалют: {market_overview['active_cryptocurrencies']:,}")
                    print(f"⏰ Обновлено: {market_overview['last_updated']}")
                else:
                    print("❌ Не удалось получить статистику рынка")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '10':
            # Анализ держателей растущих токенов
            print("\n" + "="*60)
            print("💰 АНАЛИЗ ДЕРЖАТЕЛЕЙ РАСТУЩИХ ТОКЕНОВ")
            print("="*60)
            print("🔍 Находит держателей быстрорастущих токенов")
            print("   и определяет кто заработал больше всего")
            print("="*60)
            
            try:
                analyzer = ProfitAnalyzer()
                
                limit = int(input("Сколько растущих токенов проанализировать? (рек. 10): ") or "10")
                limit = min(limit, 20)
                
                holders_per_token = int(input("Сколько держателей проверять для каждого токена? (рек. 20): ") or "20")
                holders_per_token = min(holders_per_token, 50)
                
                print(f"\n🔍 Анализ {limit} токенов по {holders_per_token} держателей...")
                
                results = analyzer.analyze_top_gainers_holders(
                    limit=limit,
                    holders_per_token=holders_per_token
                )
                
                analyzer.display_analysis_results(results)
                
            except ImportError as e:
                print(f"❌ Ошибка импорта: {e}")
                print("📦 Создайте файл profit_analyzer.py")
            except Exception as e:
                print(f"❌ Ошибка анализа: {e}")
        
        elif choice == '11':
            # Анализ конкретных токенов из списка
            print("\n" + "="*60)
            print("🎯 АНАЛИЗ КОНКРЕТНЫХ ТОКЕНОВ ИЗ СПИСКА")
            print("="*60)
            print("⚠️  ВНИМАНИЕ: Для этого пункта нужно сначала получить")
            print("   список токенов через пункт 1")
            print("="*60)
            
            # Сначала получаем данные о токенах
            try:
                limit = int(input("Сколько токенов взять для анализа? (рек. 5-10): ") or "5")
                limit = min(limit, 20)
                
                print(f"\n🔍 Получение топ {limit} растущих токенов...")
                crypto_data = cmc_api.get_top_gainers_with_contracts(limit=limit)
                
                if not crypto_data:
                    print("❌ Не удалось получить данные о токенах")
                    continue
                
                # Отображаем полученные токены
                display_crypto_table(crypto_data, "📋 ПОЛУЧЕННЫЕ ТОКЕНЫ:")
                
                # Подтверждение
                confirm = input("\n🔍 Начать анализ этих токенов? (да/нет): ").lower()
                if confirm not in ['да', 'д', 'yes', 'y']:
                    print("❌ Анализ отменен")
                    continue
                
                # Создаем список для анализа
                tokens_to_analyze = []
                for token in crypto_data:
                    if token.get('contract_address'):
                        tokens_to_analyze.append({
                            'symbol': token['symbol'],
                            'name': token['name'],
                            'contract_address': token['contract_address'],
                            'platform': token.get('platform', 'unknown'),
                            'percent_change_24h': token['percent_change_24h'],
                            'price_usd': token['price_usd']
                        })
                
                if not tokens_to_analyze:
                    print("❌ Нет токенов с контрактными адресами для анализа")
                    continue
                
                print(f"\n🎯 Начинаем анализ {len(tokens_to_analyze)} токенов...")
                
                # Запускаем анализ
                analyzer = ProfitAnalyzer()
                results = analyzer.analyze_specific_tokens_from_list(tokens_to_analyze)
                
                # Сохраняем результаты
                save = input("\n💾 Сохранить результаты? (да/нет): ").lower()
                if save in ['да', 'д', 'yes', 'y']:
                    import json
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f'specific_tokens_analysis_{timestamp}.json'
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump({
                            'tokens_analyzed': tokens_to_analyze,
                            'top_holders': results[:20],
                            'analysis_time': timestamp
                        }, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Результаты сохранены в {filename}")
                
            except Exception as e:
                print(f"❌ Ошибка анализа: {e}")
        
        elif choice == '0':
            print("\n" + "="*60)
            print("👋 Выход из программы...")
            print("="*60)
            break
        
        else:
            print("❌ Неверный выбор. Введите число от 0 до 11")
        
        input("\n↵ Нажмите Enter для продолжения...")

# ЯВНЫЙ ЗАПУСК ПРОГРАММЫ
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Программа прервана пользователем")
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка: {e}")
        print("Попробуйте:")
        print("1. Проверить наличие файла .env с API ключами")
        print("2. Установить зависимости: pip install requests python-dotenv")
        print("3. Проверить подключение к интернету")
    
    # Завершающий ввод
    input("\nНажмите Enter для выхода...")