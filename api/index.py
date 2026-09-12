from flask import Flask, request
import requests
import json

app = Flask(__name__)

TOKEN = "8992836993:AAGNiuBJGt3HuMyPjtMIQ4GG8XwO8XXl2bE"

# পণ্যের তালিকা
PRODUCTS = {
    "night_socket": {"name": "🔌 Night Socket Light", "price": 1920},
    "rose_yellow": {"name": "🌹 Rose Tree (Yellow)", "price": 2000},
    "rose_pink": {"name": "🌹 Rose Tree (Pink)", "price": 2000},
    "acrylic_3d": {"name": "✨ 3D Acrylic Lamp", "price": 1200},
    "spiral_led": {"name": "🌀 Spiral LED Lamp", "price": 2400},
    "lighthouse": {"name": "🗼 Lighthouse Lamp", "price": 800},
    "neon": {"name": "🎆 Neon Light", "price": 1200},
    "tree_branch": {"name": "🌳 Tree Branch Lights", "price": 1200},
    "moon_head": {"name": "🌙 Moon Head Lights", "price": 560}
}

user_state = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})

@app.route('/api/index', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'message' not in data:
        return {'ok': True}
    
    message = data['message']
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    user_name = message['from'].get('first_name', 'বন্ধু')
    text = message.get('text', '').lower()
    
    if text == '/start':
        msg = f"👋 আস্সালামু আলাইকুম {user_name}!\n\n🎉 LOZE BD এ স্বাগতম!\n\n/products - সব পণ্য\n/order - অর্ডার করুন\n/contact - যোগাযোগ"
        send_message(chat_id, msg)
    
    elif text == '/products':
        msg = "<b>💡 আমাদের পণ্য:</b>\n\n"
        for idx, (key, product) in enumerate(PRODUCTS.items(), 1):
            msg += f"{idx}. {product['name']}\n   দাম: <b>{product['price']} টাকা</b>\n\n"
        send_message(chat_id, msg)
    
    elif text == '/order':
        user_state[user_id] = {'step': 'waiting_product'}
        send_message(chat_id, "🛒 অর্ডার করুন\n\nপণ্যের নাম বলুন:\nউদাহরণ: night socket, rose tree")
    
    elif text == '/contact':
        send_message(chat_id, "📱 WhatsApp: 01829244034\nBkash: 01829244034")
    
    else:
        if user_id in user_state:
            state = user_state[user_id]
            if state.get('step') == 'waiting_product':
                product_found = None
                for key, product in PRODUCTS.items():
                    if key.replace('_', ' ') in text:
                        product_found = key
                        break
                
                if product_found:
                    user_state[user_id] = {'step': 'waiting_name', 'product_key': product_found}
                    send_message(chat_id, f"✅ পণ্য: {PRODUCTS[product_found]['name']}\nদাম: {PRODUCTS[product_found]['price']} টাকা\n\nনাম বলুন:")
            
            elif state.get('step') == 'waiting_name':
                user_state[user_id]['customer_name'] = text
                user_state[user_id]['step'] = 'waiting_phone'
                send_message(chat_id, f"✅ নাম: {text}\n\nফোন নম্বর বলুন:")
            
            elif state.get('step') == 'waiting_phone':
                user_state[user_id]['customer_phone'] = text
                user_state[user_id]['step'] = 'waiting_address'
                send_message(chat_id, f"✅ ফোন: {text}\n\nঠিকানা বলুন:")
            
            elif state.get('step') == 'waiting_address':
                state = user_state[user_id]
                product = PRODUCTS[state['product_key']]
                msg = f"""✅ অর্ডার কনফার্ম!

📦 পণ্য: {state['product_name'] if 'product_name' in state else product['name']}
👤 নাম: {state['customer_name']}
📱 ফোন: {state['customer_phone']}
📍 ঠিকানা: {text}

💰 দাম: {product['price']} টাকা

📱 WhatsApp: 01829244034
💳 Bkash: 01829244034"""
                send_message(chat_id, msg)
                del user_state[user_id]
    
    return {'ok': True}

@app.route('/', methods=['GET'])
def home():
    return 'Bot is running!'
