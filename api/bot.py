from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import json
import os
from datetime import datetime

app = Flask(__name__)

TOKEN = "8992836993:AAGNiuBJGt3HuMyPjtMIQ4GG8XwO8XXl2bE"
WEBHOOK_URL = "https://your-domain.vercel.app/api/bot"

# পণ্যের তালিকা
PRODUCTS = {
    "night_socket": {"name": "🔌 Night Socket Light", "original_price": 2400, "discount_price": 1920},
    "rose_yellow": {"name": "🌹 Rose Tree (Yellow)", "original_price": 2500, "discount_price": 2000},
    "rose_pink": {"name": "🌹 Rose Tree (Pink)", "original_price": 2500, "discount_price": 2000},
    "acrylic_3d": {"name": "✨ 3D Acrylic Lamp", "original_price": 1500, "discount_price": 1200},
    "spiral_led": {"name": "🌀 Spiral LED Lamp", "original_price": 3000, "discount_price": 2400},
    "lighthouse": {"name": "🗼 Lighthouse Lamp", "original_price": 1000, "discount_price": 800},
    "neon": {"name": "🎆 Neon Light", "original_price": 1500, "discount_price": 1200},
    "tree_branch": {"name": "🌳 Tree Branch Lights", "original_price": 1500, "discount_price": 1200},
    "moon_head": {"name": "🌙 Moon Head Lights", "original_price": 700, "discount_price": 560}
}

user_state = {}

@app.route('/api/bot', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        data = request.json
        
        if not data:
            return {'ok': True}
        
        # Update object থেকে তথ্য নিন
        if 'message' not in data:
            return {'ok': True}
        
        message = data['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from'].get('first_name', 'বন্ধু')
        text = message.get('text', '').lower()
        
        # /start কমান্ড
        if text == '/start':
            send_message(chat_id, f"""
👋 আস্সালামু আলাইকুম {user_name}!

🎉 <b>LOZE BD এ স্বাগতম!</b>

আমরা সুন্দর Light বিক্রি করি।

📋 <b>কমান্ড:</b>
/products - সব পণ্য দেখুন 💡
/order - অর্ডার করুন 🛒
/contact - যোগাযোগ 📱
            """)
        
        # /products কমান্ড
        elif text == '/products':
            msg = "<b>💡 আমাদের পণ্য:</b>\n\n"
            for idx, (key, product) in enumerate(PRODUCTS.items(), 1):
                msg += f"{idx}. {product['name']}\n   দাম: <b>{product['discount_price']} টাকা</b> (20% ছাড়)\n\n"
            msg += "অর্ডার করতে: /order লিখুন"
            send_message(chat_id, msg)
        
        # /order কমান্ড
        elif text == '/order':
            user_state[user_id] = {'step': 'waiting_product'}
            send_message(chat_id, """
🛒 <b>অর্ডার করুন</b>

আপনি যে পণ্য চান তার নাম বলুন।

উদাহরণ: night socket, rose tree, acrylic lamp
            """)
        
        # /contact কমান্ড
        elif text == '/contact':
            send_message(chat_id, """
📱 <b>যোগাযোগ করুন</b>

WhatsApp: 01829244034
Bkash: 01829244034

🕐 সকাল ১০টা - রাত ১০টা
            """)
        
        # সাধারণ মেসেজ
        else:
            if user_id in user_state:
                state = user_state[user_id]
                
                if state.get('step') == 'waiting_product':
                    # পণ্য খুঁজুন
                    product_found = None
                    for key, product in PRODUCTS.items():
                        if key.replace('_', ' ') in text or product['name'].lower() in text:
                            product_found = key
                            break
                    
                    if product_found:
                        user_state[user_id] = {
                            'step': 'waiting_name',
                            'product_key': product_found,
                            'product_name': PRODUCTS[product_found]['name']
                        }
                        send_message(chat_id, f"""
✅ পণ্য: {PRODUCTS[product_found]['name']}
দাম: {PRODUCTS[product_found]['discount_price']} টাকা

এখন আপনার <b>নাম</b> বলুন:
                        """)
                
                elif state.get('step') == 'waiting_name':
                    user_state[user_id]['customer_name'] = text
                    user_state[user_id]['step'] = 'waiting_phone'
                    send_message(chat_id, f"✅ নাম: <b>{text}</b>\n\nফোন নম্বর বলুন:")
                
                elif state.get('step') == 'waiting_phone':
                    user_state[user_id]['customer_phone'] = text
                    user_state[user_id]['step'] = 'waiting_address'
                    send_message(chat_id, f"✅ ফোন: <b>{text}</b>\n\nঠিকানা বলুন:")
                
                elif state.get('step') == 'waiting_address':
                    user_state[user_id]['customer_address'] = text
                    
                    # অর্ডার সম্পন্ন
                    state = user_state[user_id]
                    product = PRODUCTS[state['product_key']]
                    
                    confirmation = f"""
✅ <b>অর্ডার কনফার্ম হয়েছে!</b>

📦 পণ্য: {state['product_name']}
👤 নাম: {state['customer_name']}
📱 ফোন: {state['customer_phone']}
📍 ঠিকানা: {state['customer_address']}

💰 দাম: {product['discount_price']} টাকা

<b>বিকাশে পাঠান: 01829244034</b>

WhatsApp: 01829244034
                    """
                    send_message(chat_id, confirmation)
                    
                    # স্টেট ক্লিয়ার করুন
                    del user_state[user_id]
            else:
                send_message(chat_id, "❌ কমান্ড বুঝতে পারলাম না। /start করুন।")
        
        return {'ok': True}
    
    except Exception as e:
        print(f"Error: {e}")
        return {'ok': False, 'error': str(e)}

def send_message(chat_id, text):
    """মেসেজ পাঠান"""
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    requests.post(url, json=data)

@app.route('/api/health', methods=['GET'])
def health():
    """স্বাস্থ্য চেক"""
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=False)
