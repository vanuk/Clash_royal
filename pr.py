import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjMyYjc2MGM3LTkwMTAtNDIyNy1iMGI3LWFmNTcxZjdiYzYyNSIsImlhdCI6MTc3MDU1NDc1NCwic3ViIjoiZGV2ZWxvcGVyL2VjMWU2YWFjLTNjYTMtZDdkNy05NTg3LWE1YjczZmJkY2M3MyIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI5MS4yMTEuMTM0LjE4MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.KgzunTyss-eWLVgCUlEbHo8jozdWXiq7qYH3aQLAmHetlUBfhGnBXVdr0FFXrKHaQCyuRYq2l3c7NZ_ZL7QyRA"
CLAN_TAG = "#QJ29YQ80"
TG_BOT_TOKEN = "8009691533:AAEA2IpUCHcliz8KJbz5RYY4yANtlTuxWVI"

def get_clash_royale_data():
    """Отримує дані про клан та членів"""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    clan_tag_encoded = CLAN_TAG.replace("#", "%23")
    url = f"https://api.clashroyale.com/v1/clans/{clan_tag_encoded}"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_inactive_members(days=2):
    """Повертає список неактивних учасників"""
    data = get_clash_royale_data()
    if not data:
        return None, None
    
    members_data = data.get('memberList', [])
    now = datetime.utcnow()
    threshold = now - timedelta(days=days)
    
    inactive_members = []
    for member in members_data:
        last_seen_str = member.get('lastSeen', '')
        if last_seen_str:
            try:
                last_seen = datetime.strptime(last_seen_str.split('.')[0], '%Y%m%dT%H%M%S')
                if last_seen < threshold:
                    days_inactive = (now - last_seen).days
                    inactive_members.append({
                        'name': member.get('name'),
                        'tag': member.get('tag'),
                        'days_inactive': days_inactive
                    })
            except:
                pass
    
    inactive_members.sort(key=lambda x: x['days_inactive'], reverse=True)
    return inactive_members, data['members']

def send_to_telegram(text):
    """Надсилає повідомлення в Telegram"""
    if TG_CHAT_ID == "YOUR_CHAT_ID":
        print("⚠️  Помилка: TG_CHAT_ID не встановлено!")
        print("💡 Напиши боту @userinfobot щоб отримати свій Chat ID")
        return False
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Помилка Telegram: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Помилка з'єднання: {e}")
        return False

def show_menu():
    """Меню команд"""
    print("\n" + "="*55)
    print("📱 Clash Royale Clan Manager")
    print("="*55)
    print("1. 📋 Показати неактивних учасників (>2 днів)")
    print("2. 📊 Показати статистику клану")
    print("3. 💬 Надіслати в Telegram")
    print("4. 🚪 Вихід")
    print("="*55)

def main():
    while True:
        show_menu()
        choice = input("\n▶️  Виберіть команду (1-4): ").strip()
        
        if choice == "1":
            print("\n⏳ Завантажую дані...")
            inactive_members, total_members = get_inactive_members()
            
            if inactive_members is None:
                print("❌ Помилка при отриманні даних з API")
                continue
            
            if not inactive_members:
                print("✅ Немає учасників, неактивних більше 2 днів")
                continue
            
            print(f"\n📋 Неактивні учасники (більше 2 днів):\n")
            for i, member in enumerate(inactive_members, 1):
                print(f"{i}. 👤 {member['name']} {member['tag']} - ⏰ {member['days_inactive']} днів")
            
            print(f"\n📊 Всього учасників: {total_members}")
            print(f"🚫 Неактивних: {len(inactive_members)}")
        
        elif choice == "2":
            print("\n⏳ Завантажую дані...")
            data = get_clash_royale_data()
            
            if not data:
                print("❌ Помилка при отриманні даних з API")
                continue
            
            print(f"\n📊 Статистика клану:")
            print(f"🏆 Назва: {data.get('name', 'N/A')}")
            print(f"📍 Тег: {data.get('tag', 'N/A')}")
            print(f"👥 Учасників: {data.get('members', 0)}/50")
            print(f"⭐ Трофеї: {data.get('clanScore', 0):,}")
            print(f"📈 Опис: {data.get('description', 'Немає опису')}")
        
        elif choice == "3":
            print("\n⏳ Завантажую дані...")
            inactive_members, total_members = get_inactive_members()
            
            if not inactive_members:
                print("✅ Немає неактивних учасників")
                continue
            
            message = "📋 <b>Неактивні учасники (більше 2 днів):</b>\n\n"
            for member in inactive_members[:20]:
                message += f"👤 <b>{member['name']}</b> {member['tag']}\n⏰ {member['days_inactive']} днів\n\n"
            
            if len(inactive_members) > 20:
                message += f"... та ще {len(inactive_members)-20} учасників\n\n"
            
            message += f"📊 <b>Всього:</b> {total_members}\n🚫 <b>Неактивних:</b> {len(inactive_members)}"
            
            if send_to_telegram(message):
                print("✅ Повідомлення надіслано в Telegram!")
            else:
                print("❌ Помилка при надсиланні")
        
        elif choice == "4":
            print("\n👋 До побачення!")
            break
        
        else:
            print("❌ Неправильний вибір! Введіть 1-4")

if __name__ == '__main__':
    main()