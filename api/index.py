
from flask import Flask, request
import requests
import json

app = Flask(__name__)

TOKEN = "8992836993:AAGNiuBJGt3HuMyPjtMIQ4GG8XwO8XXl2bE"
BIKASH = "01829244034"

PRODUCTS = {
    "neon": {"name": "🎆 Neon Light", "price": 1200, "img": "https://ibb.co/prLdYKtT"},
    "spiral": {"name": "🌀 Spiral LED", "price": 2400, "img": "https://ibb.co/WZjL6kL"},
    "rose_y": {"name": "🌹 Rose Yellow", "price": 2000, "img": "https://ibb.co/zHVwDW92"},
    "rose_p": {"name": "🌹 Rose Pink", "price": 2000, "img": "https://ibb.co/8nxCrMFg"},
    "acrylic": {"name": "✨ 3D Lamp", "price": 1200, "img": "https://ibb.co/JFKHWZwS"},
    "house": {"name": "🗼 Lighthouse", "price": 800, "img": "https://ibb.co/XZtYZHp3"},
    "night": {"name": "🔌 Night Socket", "price": 1920, "img": "https://ibb.co/Hf3938xG"},
    "tree": {"name": "🌳 Tree Branch", "price": 1200, "img": "https://ibb.co/twS4gwZ2"},
    "moon1": {"name": "🌙 Moon Lamp 1", "price": 560, "img": "https://ibb.co/sd1qJHjm"},
    "moon2": {"name": "🌙 Moon Lamp 2", "price": 560, "img": "https://ibb.co/4n0hsVCq"},
    "table": {"name": "💡 Table Lamp", "price": 560, "img": "https://ibb.co/pB8tVFnf"},
}

state = {}

def send_msg(cid, txt, img=None):
    if img:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json={'chat_id': cid, 'photo': img, 'caption': txt, 'parse_mode': 'HTML'})
    else:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={'chat_id': cid, 'text': txt, 'parse_mode': 'HTML'})

@app.route('/api/index', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'message' not in data:
        return {'ok': True}
    
    msg = data['message']
    cid = msg['chat']['id']
    uid = msg['from']['id']
    name = msg['from'].get('first_name', 'বন্ধু')
    txt = msg.get('text', '').lower()
    
    if txt == '/start' or uid not in state:
        send_msg(cid, f"👋 আস্সালামু আলাইকুম {name}!\n\n🎉 LOZE BD এ স্বাগতম!\n\n💡 পণ্য অর্ডার করুন")
        for p in PRODUCTS.values():
            send_msg(cid, f"{p['name']}\n💰 {p['price']} টাকা\n\nঅর্ডার: অর্ডার লিখুন", p['img'])
    
    elif 'অর্ডার' in txt or 'order' in txt:
        state[uid] = {'step': 'product'}
        send_msg(cid, "🛒 পণ্য বলুন (যেমন: spiral, rose, night)")
    
    else:
        if uid in state:
            s = state[uid]
            if s['step'] == 'product':
                prod = None
                for k, p in PRODUCTS.items():
                    if k in txt or p['name'].lower() in txt:
                        prod = k
                        break
                if prod:
                    state[uid] = {'step': 'name', 'prod': prod, 'data': PRODUCTS[prod]}
                    send_msg(cid, f"✅ {PRODUCTS[prod]['name']}\n💰 {PRODUCTS[prod]['price']} টাকা\n\nনাম বলুন:", PRODUCTS[prod]['img'])
            
            elif s['step'] == 'name':
                state[uid]['name'] = txt
                state[uid]['step'] = 'phone'
                send_msg(cid, f"✅ নাম: {txt}\n\nফোন বলুন:")
            
            elif s['step'] == 'phone':
                state[uid]['phone'] = txt
                state[uid]['step'] = 'addr'
                send_msg(cid, f"✅ ফোন: {txt}\n\nঠিকানা বলুন:")
            
            elif s['step'] == 'addr':
                prod = state[uid]['data']
                total = prod['price']
                adv = 200
                remain = total - adv
                
                order_msg = f"""
✅ অর্ডার কনফার্ম!

📦 {prod['name']}
👤 {state[uid]['name']}
📱 {state[uid]['phone']}
📍 {txt}

💰 মোট: {total} টাকা
💳 Advance: {adv} টাকা (Bikash)
⏳ বাকি: {remain} টাকা (ডেলিভারিতে)

📱 Bikash: {BIKASH}

ধন্যবাদ! 🙏
                """
                send_msg(cid, order_msg)
                
                # WhatsApp এ পাঠান (আপনার WhatsApp বটে এই মেসেজ আসবে)
                wa_msg = f"অর্ডার: {prod['name']} | {state[uid]['name']} | {state[uid]['phone']} | {txt} | Advance: {adv} টাকা"
                print(wa_msg)  # Log এ দেখা যাবে
                
                del state[uid]
    
    return {'ok': True}

@app.route('/', methods=['GET'])
def home():
    return '🤖 LOZE BD Bot is running!'

if __name__ == '__main__':
    app.run()
