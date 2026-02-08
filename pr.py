import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImRmOTcyYjQ2LTExNzktNGM2OC1iZjQ5LTQ4N2M0MDllNzAxYyIsImlhdCI6MTc3MDU1ODA5Nywic3ViIjoiZGV2ZWxvcGVyL2VjMWU2YWFjLTNjYTMtZDdkNy05NTg3LWE1YjczZmJkY2M3MyIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI5MS4yMTEuMTM0LjE4MyIsIjEwNC4xOC4zNS40NiIsIjM0LjE3MS4xNjEuMTA1Il0sInR5cGUiOiJjbGllbnQifV19.seHBwWK1dO7j9vpqD4ZX4Xj1A1S_Hp5aszTu0__EJZIy3UrhfCuzRJom_6rFCAIV3nUJuYt8r-zqRowZIpgXqg"
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
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            error_data = response.json()
            reason = error_data.get('reason', 'Unknown')
            message = error_data.get('message', 'Access Denied')
            print(f"⚠️  403 Error: {reason}")
            print(f"📝 {message}")
            print("💡 Додай IP в білий список на https://developer.clashroyale.com/")
            return None
        else:
            print(f"⚠️  API Error: {response.status_code}")
            print(f"📝 {response.text}")
            return None
    except Exception as e:
        print(f"❌ Помилка з'єднання: {e}")
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

async def inactive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /inactive - показує неактивних учасників"""
    await update.message.reply_text("⏳ Завантажую дані...")
    
    inactive_members, total_members = get_inactive_members()
    
    if inactive_members is None:
        await update.message.reply_text("❌ Помилка при отриманні даних з API")
        return
    
    if not inactive_members:
        await update.message.reply_text("✅ Немає учасників, неактивних більше 2 днів")
        return
    
    message = "📋 <b>Неактивні учасники (більше 2 днів):</b>\n\n"
    for member in inactive_members[:15]:
        message += f"👤 <b>{member['name']}</b> {member['tag']}\n   ⏰ {member['days_inactive']} днів\n\n"
    
    if len(inactive_members) > 15:
        message += f"... та ще {len(inactive_members)-15} учасників\n\n"
    
    message += f"📊 Всього: {total_members}\n🚫 Неактивних: {len(inactive_members)}"
    await update.message.reply_text(message, parse_mode="HTML")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats - статистика клану"""
    await update.message.reply_text("⏳ Завантажую дані...")
    
    data = get_clash_royale_data()
    if not data:
        await update.message.reply_text("❌ Помилка при отриманні даних з API")
        return
    
    message = "<b>📊 Статистика клану:</b>\n\n"
    message += f"🏆 <b>Назва:</b> {data.get('name', 'N/A')}\n"
    message += f"📍 <b>Тег:</b> {data.get('tag', 'N/A')}\n"
    message += f"👥 <b>Учасників:</b> {data.get('members', 0)}/50\n"
    message += f"⭐ <b>Трофеї:</b> {data.get('clanScore', 0):,}\n"
    message += f"📈 <b>Опис:</b> {data.get('description', 'Немає опису')}\n"
    
    await update.message.reply_text(message, parse_mode="HTML")

def main():
    """Запуск бота"""
    app = Application.builder().token(TG_BOT_TOKEN).build()
    
    #app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inactive", inactive))
    app.add_handler(CommandHandler("stats", stats))
    #app.add_handler(CommandHandler("help", help_command))
    
    print("🤖 Бот запущено!")
    print("💡 Якщо виникне помилка timeout - потрібен VPN")
    print("⏹️  Натисніть Ctrl+C щоб зупинити")
    
    app.run_polling()

if __name__ == '__main__':
    main()