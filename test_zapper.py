#!/usr/bin/env python3
"""
Финальный тест Zapper API с рабочим запросом
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_zapper_api():
    """Тестирует Zapper API с рабочим запросом"""
    print("🔧 ТЕСТИРОВАНИЕ ZAPPER API (ФИНАЛЬНЫЙ ТЕСТ)")
    print("="*60)
    
    # Получаем API ключ
    api_key = os.getenv('ZAPPER_API_KEY')
    
    if not api_key or api_key == 'your_zapper_api_key_here':
        print("❌ API ключ не найден в .env файле")
        print("\n📝 Добавьте в .env:")
        print("ZAPPER_API_KEY=343a5c13-9181-4aab-b57f-10008fa8b15c")
        return
    
    print(f"✅ API ключ найден: {api_key[:10]}...{api_key[-10:]}")
    
    # Настройка заголовков
    headers = {
        'Content-Type': 'application/json',
        'x-zapper-api-key': api_key
    }
    
    # ТЕСТ 1: Самый простой запрос
    print("\n" + "="*60)
    print("🧪 ТЕСТ 1: Простейший запрос")
    print("="*60)
    
    simple_query = {
        "query": "{ __typename }"
    }
    
    try:
        response = requests.post(
            'https://public.zapper.xyz/graphql',
            headers=headers,
            json=simple_query,
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL ошибка: {data['errors']}")
            else:
                print(f"✅ Успешно! Ответ: {data}")
        else:
            print(f"❌ HTTP ошибка: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    # ТЕСТ 2: Рабочий запрос из вашего curl (портфель)
    print("\n" + "="*60)
    print("🧪 ТЕСТ 2: Запрос портфеля (рабочий запрос)")
    print("="*60)
    
    portfolio_query = {
        "query": """
        query TokenBalances($addresses: [Address!]!, $first: Int, $chainIds: [Int!]) {
            portfolioV2(addresses: $addresses, chainIds: $chainIds) {
                tokenBalances {
                    totalBalanceUSD
                    byToken(first: $first) {
                        totalCount
                        edges {
                            node {
                                name
                                symbol
                                price
                                tokenAddress
                                imgUrlV2
                                decimals
                                balanceRaw
                                balance
                                balanceUSD
                                onchainMarketData {
                                    priceChange24h
                                    marketCap
                                }
                            }
                        }
                    }
                }
            }
        }
        """,
        "variables": {
            "addresses": ["0x849151d7d0bf1f34b70d5cad5149d28cc2308bf1"],
            "first": 5,
            "chainIds": [8453]  # Base network
        }
    }
    
    try:
        response = requests.post(
            'https://public.zapper.xyz/graphql',
            headers=headers,
            json=portfolio_query,
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ GraphQL ошибка: {data['errors'][0].get('message')}")
            else:
                print("✅ Запрос успешен!")
                
                # Показываем данные портфеля
                portfolio = data.get('data', {}).get('portfolioV2', {})
                token_balances = portfolio.get('tokenBalances', {})
                
                total_balance = token_balances.get('totalBalanceUSD', 0)
                print(f"\n💰 Общий баланс: ${total_balance:,.2f}")
                
                edges = token_balances.get('byToken', {}).get('edges', [])
                print(f"📊 Найдено токенов: {len(edges)}")
                
                if edges:
                    print("\n📈 Топ токенов:")
                    for i, edge in enumerate(edges[:3], 1):
                        node = edge.get('node', {})
                        print(f"{i}. {node.get('symbol')}: ${node.get('balanceUSD', 0):,.2f}")
        else:
            print(f"❌ HTTP ошибка: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    # ТЕСТ 3: Запрос для Ethereum сети
    print("\n" + "="*60)
    print("🧪 ТЕСТ 3: Запрос портфеля Ethereum")
    print("="*60)
    
    eth_query = {
        "query": """
        query TokenBalances($addresses: [Address!]!, $first: Int, $chainIds: [Int!]) {
            portfolioV2(addresses: $addresses, chainIds: $chainIds) {
                tokenBalances {
                    totalBalanceUSD
                    byToken(first: $first) {
                        edges {
                            node {
                                symbol
                                name
                                balanceUSD
                                price
                            }
                        }
                    }
                }
            }
        }
        """,
        "variables": {
            "addresses": ["0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"],  # Виталик
            "first": 3,
            "chainIds": [1]  # Ethereum
        }
    }
    
    try:
        response = requests.post(
            'https://public.zapper.xyz/graphql',
            headers=headers,
            json=eth_query,
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ GraphQL ошибка: {data['errors'][0].get('message')}")
            else:
                print("✅ Запрос успешен!")
                
                portfolio = data.get('data', {}).get('portfolioV2', {})
                token_balances = portfolio.get('tokenBalances', {})
                
                total_balance = token_balances.get('totalBalanceUSD', 0)
                print(f"\n💰 Баланс кошелька Виталика: ${total_balance:,.2f}")
                
        else:
            print(f"❌ HTTP ошибка: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    # ТЕСТ 4: Запрос держателей токена
    print("\n" + "="*60)
    print("🧪 ТЕСТ 4: Запрос держателей токена")
    print("="*60)
    
    holders_query = {
        "query": """
        query FungibleToken($address: Address!, $chainId: Int!, $first: Int!) {
            fungibleTokenV2(address: $address, chainId: $chainId) {
                holders(first: $first) {
                    edges {
                        node {
                            holderAddress
                            value
                            percentileShare
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """,
        "variables": {
            "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
            "chainId": 1,  # Ethereum
            "first": 5
        }
    }
    
    try:
        response = requests.post(
            'https://public.zapper.xyz/graphql',
            headers=headers,
            json=holders_query,
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ GraphQL ошибка: {data['errors'][0].get('message')}")
            else:
                print("✅ Запрос успешен!")
                
                token_data = data.get('data', {}).get('fungibleTokenV2', {})
                holders = token_data.get('holders', {}).get('edges', [])
                
                print(f"\n👥 Найдено держателей WETH: {len(holders)}")
                
                if holders:
                    print("\nТоп держатели:")
                    for i, holder in enumerate(holders[:3], 1):
                        node = holder.get('node', {})
                        address = node.get('holderAddress', '')
                        value = float(node.get('value', 0))
                        print(f"{i}. {address[:10]}...{address[-6:]}: {value:,.0f} WETH")
                        
        else:
            print(f"❌ HTTP ошибка: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    print("\n" + "="*60)
    print("📋 ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    print("\n🎯 РЕКОМЕНДАЦИИ ДЛЯ ОСНОВНОЙ ПРОГРАММЫ:")
    print("1. Используйте тот же формат запроса что в ТЕСТЕ 2")
    print("2. Укажите правильный chainId для сети:")
    print("   • Ethereum: 1")
    print("   • Base: 8453")
    print("   • Polygon: 137")
    print("   • Arbitrum: 42161")
    print("3. Добавляйте задержки между запросами (0.5-1 сек)")
    print("4. Обрабатывайте ошибки GraphQL в ответе")

if __name__ == "__main__":
    try:
        test_zapper_api()
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван")
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка: {e}")
    
    input("\nНажмите Enter для выхода...")