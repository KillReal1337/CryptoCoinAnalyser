from datetime import datetime

def display_crypto_table(data, title=""):
    """Отображает таблицу с данными о криптовалютах"""
    if not data:
        print("❌ Нет данных для отображения")
        return
    
    if title:
        print(f"\n{title}")
    
    print("="*130)
    print(f"{'№':<3} {'Название':<20} {'Символ':<8} {'Цена USD':<12} {'Объем 24ч':<18} {'Рост 24ч':<10} {'Контракт':<50}")
    print("-" * 130)
    
    for coin in data:
        # Форматируем цену
        price = coin['price_usd']
        if price >= 1:
            price_str = f"${price:,.2f}"
        elif price >= 0.01:
            price_str = f"${price:,.4f}"
        else:
            price_str = f"${price:.8f}"
        
        # Форматируем объем
        volume = coin['volume_24h']
        if volume >= 1_000_000_000:
            volume_str = f"${volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            volume_str = f"${volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            volume_str = f"${volume/1_000:.2f}K"
        else:
            volume_str = f"${volume:,.0f}"
        
        # Форматируем процент роста
        change = coin['percent_change_24h']
        change_str = f"{change:+.2f}%"
        
        # Форматируем контрактный адрес
        contract = coin['contract_address']
        if contract:
            if len(contract) > 46:
                contract_display = f"{contract[:20]}...{contract[-20:]}"
            else:
                contract_display = contract
        else:
            contract_display = "Нет контракта"
        
        print(f"{coin['rank']:<3} {coin['name'][:20]:<20} {coin['symbol']:<8} "
              f"{price_str:<12} {volume_str:<18} "
              f"{change_str:<10} {contract_display:<50}")
        
        if contract and coin.get('platform') and coin['platform'] != 'unknown':
            print(f"    ↳ Платформа: {coin['platform']}")

def display_top_wallets(wallets_data):
    """Отображает топ кошельков - ВЫВОДИТ ПОЛНЫЙ АДРЕС"""
    if not wallets_data:
        print("❌ Нет данных о кошельках")
        return
    
    print("\n" + "="*130)
    print("🏆 ТОП КОШЕЛЬКОВ ПО ЗАРАБОТКУ (ПОЛНЫЕ АДРЕСА)")
    print("="*130)
    print(f"{'№':<3} {'Кошелек':<44} {'Баланс USD':<15} {'Прибыль 24ч':<15} {'ROI %':<10} {'Win Rate %':<12} {'Сделок':<8} {'Рейтинг':<10}")
    print("-" * 130)
    
    for i, wallet in enumerate(wallets_data, 1):
        address = wallet.get('wallet_address', '')
        # ВЫВОДИМ ПОЛНЫЙ АДРЕС
        display_address = address
        
        balance = wallet.get('current_balance_usd', 0)
        daily_profit = wallet.get('estimated_daily_profit_usd', 0)
        roi = wallet.get('roi_percent', 0)
        win_rate = wallet.get('win_rate_percent', 0)
        trades = wallet.get('total_trades', 0)
        
        # Определяем рейтинг
        if daily_profit > 1000:
            rating = "S-Tier 🏆"
        elif daily_profit > 500:
            rating = "A-Tier ⭐"
        elif daily_profit > 100:
            rating = "B-Tier 👍"
        elif daily_profit > 0:
            rating = "C-Tier 📈"
        else:
            rating = "D-Tier 📉"
        
        print(f"{i:<3} {display_address:<44} ${balance:,.0f} ${daily_profit:,.0f} {roi:+.1f}% {win_rate:.1f}% {trades:<8} {rating:<10}")

def display_wallet_details(wallet_data):
    """Отображает детальную информацию о кошельке - ПОЛНЫЙ АДРЕС"""
    print("\n" + "="*80)
    print(f"🔍 ДЕТАЛЬНЫЙ АНАЛИЗ КОШЕЛЬКА")
    print("="*80)
    
    address = wallet_data.get('wallet_address', '')
    # ВЫВОДИМ ПОЛНЫЙ АДРЕС
    print(f"Кошелек: {address}")
    
    if 'daily_analysis' in wallet_data:
        daily = wallet_data['daily_analysis']
        print(f"\n📊 ЗА 24 ЧАСА:")
        print(f"• Баланс: ${daily.get('current_balance_usd', 0):,.2f}")
        print(f"• Прибыль: ${daily.get('estimated_daily_profit_usd', 0):,.2f}")
        print(f"• Сделок: {daily.get('total_trades', 0)}")
        print(f"• Объем: ${daily.get('daily_volume_usd', 0):,.2f}")
        print(f"• ROI: {daily.get('roi_percent', 0):+.1f}%")
        print(f"• Win Rate: {daily.get('win_rate_percent', 0):.1f}%")
    
    if 'weekly_analysis' in wallet_data:
        weekly = wallet_data['weekly_analysis']
        print(f"\n📅 ЗА 7 ДНЕЙ:")
        print(f"• Прибыль: ${weekly.get('estimated_daily_profit_usd', 0)*7:,.2f}")
        print(f"• Сделок: {weekly.get('total_trades', 0)}")
    
    if 'top_tokens' in wallet_data and wallet_data['top_tokens']:
        print(f"\n💰 ТОП ТОКЕНОВ:")
        for i, token in enumerate(wallet_data['top_tokens'][:5], 1):
            print(f"{i}. {token['symbol']}: ${token['balance_usd']:,.2f}")
    
    if 'consistency_score' in wallet_data:
        print(f"\n📈 МЕТРИКИ:")
        print(f"• Консистенси: {wallet_data.get('consistency_score', 0):.1f}/100")
        print(f"• Риск: {wallet_data.get('risk_score', 0):.1f}/100")
        print(f"• Рейтинг успеха: {wallet_data.get('success_rating', 'Неизвестно')}")

def get_user_choice(prompt="Выберите опцию: ", min_val=0, max_val=10):
    """Получает выбор пользователя"""
    try:
        choice = int(input(prompt).strip())
        if min_val <= choice <= max_val:
            return choice
        else:
            print(f"❌ Введите число от {min_val} до {max_val}")
            return get_user_choice(prompt, min_val, max_val)
    except ValueError:
        print("❌ Введите корректное число")
        return get_user_choice(prompt, min_val, max_val)

def format_timestamp():
    """Форматирует текущее время"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def display_holders_profit(holders_data, title=""):
    """Отображает держателей и их предполагаемую прибыль с ПОЛНЫМИ адресами"""
    if not holders_data:
        print("❌ Нет данных о держателях")
        return
    
    if title:
        print(f"\n{title}")
    
    print("="*150)
    print(f"{'Ранг':<5} {'Адрес кошелька':<44} {'Имя':<20} {'Прибыль USD':<15} {'Токенов':<15} {'Доля %':<10} {'Текущая стоимость USD':<20}")
    print("-" * 150)
    
    for holder in holders_data:
        # ВЫВОДИМ ПОЛНЫЙ АДРЕС
        address = holder.get('address', '')
        
        display_name = holder.get('display_name', '')
        profit = holder.get('estimated_profit_usd', 0)
        token_amount = holder.get('token_amount', 0)
        share_percent = holder.get('share_percent', 0)
        current_value = holder.get('current_value_usd', 0)
        
        # Форматируем большие числа
        if profit >= 1_000_000:
            profit_str = f"${profit/1_000_000:.2f}M"
        elif profit >= 1_000:
            profit_str = f"${profit/1_000:.2f}K"
        else:
            profit_str = f"${profit:,.2f}"
        
        if current_value >= 1_000_000:
            current_str = f"${current_value/1_000_000:.2f}M"
        elif current_value >= 1_000:
            current_str = f"${current_value/1_000:.2f}K"
        else:
            current_str = f"${current_value:,.2f}"
        
        print(f"{holder['rank']:<5} {address:<44} {display_name[:20]:<20} "
              f"{profit_str:<15} {token_amount:,.0f} {'':<10} {share_percent:.2f}% {'':<8} {current_str:<20}")