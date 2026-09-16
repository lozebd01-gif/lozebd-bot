from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "8992836993:AAGNiuBJGt3HuMyPjtMIQ4GG8XwO8XXl2bE"
BIKASH = "01829244034"
OWNER_CHAT_ID = 7216817853

PRODUCTS = {
    "p1": {
        "name": "Eiffel Tower 3D",
        "images": ["https://ibb.co.com/0p4p0Sxs"],
        "price": 720
    },
    "p2": {
        "name": "LED Table Lamp",
        "images": ["https://ibb.co.com/MwXyhKT", "https://ibb.co.com/vMW3tD2", "https://ibb.co.com/NgFYSFYL"],
        "price": 1920
    },
    "p3": {
        "name": "LED Night Light",
        "images": ["https://ibb.co.com/dy7pRWf"],
        "price": 400
    },
    "p4": {
        "name": "Rose Light",
        "images": ["https://ibb.co.com/gX0Rmpw", "https://ibb.co.com/VppG7zCS"],
        "price": 1200
    },
    "p5": {
        "name": "Cylindrical Wooden Table Lamp",
        "images": ["https://ibb.co.com/5xk3qg21"],
        "price": 2000
    },
    "p6": {
        "name": "Moon Lamp",
        "images": ["https://ibb.co.com/6JvP94ns"],
        "price": 2560
    },
    "p7": {
        "name": "Tree Light",
        "images": ["https://ibb.co.com/pjJz93Cj"],
        "price": 1600
    },
    "p8": {
        "name": "Moon LED Table Lamps",
        "images": ["https://ibb.co.com/dwrMdc1R"],
        "price": 1440
    },
    "p9": {
        "name": "Eiffel Tower 3D Illusion",
        "images": ["https://ibb.co.com/s8QshYv", "https://ibb.co.com/WWNYGfwP", "https://ibb.co.com/v45QbnCP", "https://ibb.co.com/WmS0RR3", "https://ibb.co.com/HTfWGQ5w"],
        "price": 720
    },
    "p10": {
        "name": "Night Light with Dusk to Dawn Sensors",
        "images": ["https://ibb.co.com/HL4989SS"],
        "price": 520
    }
}

state = {}
shown_welcome = {}

def send_msg(cid, txt, img=None):
    if img:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                     json={'chat_id': cid, 'photo': img, 'caption': txt, 'parse_mode': 'HTML'})
    else:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={'chat_id': cid, 'text': txt, 'parse_mode': 'HTML'})

def send_button_msg(cid, txt, buttons=None):
    if not buttons:
        buttons = [[{"text": "📦 Products", "callback_data": "products"}],
                   [{"text": "🛒 Order", "callback_data": "order"}]]
    
    keyboard = {"inline_keyboard": buttons}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                 json={'chat_id': cid, 'text': txt, 'reply_markup': keyboard, 'parse_mode': 'HTML'})

@app.route('/api/index', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return {'ok': True}
    
    if 'callback_query' in data:
        query = data['callback_query']
        cid = query['message']['chat']['id']
        uid = query['from']['id']
        name = query['from'].get('first_name', 'বন্ধু')
        action = query['data']
        
        if action == 'products':
            send_msg(cid, "💡 আমাদের পণ্য:")
            for key, product in PRODUCTS.items():
                for img in product['images']:
                    send_msg(cid, f"{product['name']}\n💰 {product['price']} টাকা", img)
        
        elif action == 'order':
            state[uid] = {'step': 'select_product', 'name': name, 'cid': cid}
            send_msg(cid, "🛒 কোন পণ্য অর্ডার করবেন?\n\n(নম্বর বলুন: 1-10)\n\nউদাহরণ: 1")
        
        return {'ok': True}
    
    if 'message' in data and 'photo' in data['message']:
        msg = data['message']
        cid = msg['chat']['id']
        uid = msg['from']['id']
        
        if uid in state and state[uid]['step'] == 'screenshot':
            s = state[uid]
            total = s['price']
            adv = 200
            remain = total - adv
            
            customer_msg = f"""
✅ অর্ডার কনফার্ম!

📦 পণ্য: {s['product_name']}
👤 নাম: {s['customer_name']}
📱 ফোন: {s['phone']}
📍 ঠিকানা: {s['address']}

💰 মোট দাম: {total} টাকা
✅ Advance পেমেন্ট: 200 টাকা ✓
⏳ বাকি (ডেলিভারিতে): {remain} টাকা

ধন্যবাদ! 🙏
            """
            send_msg(cid, customer_msg)
            
            owner_msg = f"""
📋 নতুন অর্ডার!

📦 পণ্য: {s['product_name']}
👤 নাম: {s['customer_name']}
📱 ফোন: {s['phone']}
📍 ঠিকানা: {s['address']}

💰 মোট দাম: {total} টাকা
💳 Advance: 200 টাকা
⏳ বাকি: {remain} টাকা

📸 Bikash Screenshot ↓
            """
            send_msg(OWNER_CHAT_ID, owner_msg)
            
            photo_id = msg['photo'][-1]['file_id']
            send_msg(OWNER_CHAT_ID, "Screenshot:", photo_id)
            
            del state[uid]
        
        return {'ok': True}
    
    if 'message' not in data:
        return {'ok': True}
    
    msg = data['message']
    cid = msg['chat']['id']
    uid = msg['from']['id']
    name = msg['from'].get('first_name', 'বন্ধু')
    txt = msg.get('text', '').lower().strip()
    
    if uid not in shown_welcome:
        send_button_msg(cid, f"👋 আস্সালামু আলাইকুম {name}!\n\n🎉 LOZE BD এ স্বাগতম!")
        shown_welcome[uid] = True
        return {'ok': True}
    
    if txt == '/start':
        send_button_msg(cid, f"👋 আস্সালামু আলাইকুম {name}!\n\n🎉 LOZE BD এ স্বাগতম!")
    
    else:
        if uid in state:
            s = state[uid]
            
            if s['step'] == 'select_product':
                try:
                    num = int(txt)
                    if 1 <= num <= 10:
                        key = f"p{num}"
                        product = PRODUCTS[key]
                        state[uid]['product_name'] = product['name']
                        state[uid]['price'] = product['price']
                        state[uid]['step'] = 'customer_name'
                        
                        send_msg(cid, f"✅ পণ্য নির্বাচিত\n💰 দাম: {product['price']} টাকা\n\nআপনার নাম বলুন:")
                    else:
                        send_msg(cid, "❌ 1-10 এর মধ্যে নম্বর বলুন")
                except:
                    send_msg(cid, "❌ নম্বর বলুন (যেমন: 1, 2, 3...)")
            
            elif s['step'] == 'customer_name':
                state[uid]['customer_name'] = txt
                state[uid]['step'] = 'phone'
                send_msg(cid, f"✅ নাম: {txt}\n\nফোন নম্বর বলুন:")
            
            elif s['step'] == 'phone':
                state[uid]['phone'] = txt
                state[uid]['step'] = 'address'
                send_msg(cid, f"✅ ফোন: {txt}\n\nঠিকানা বলুন:")
            
            elif s['step'] == 'address':
                state[uid]['address'] = txt
                state[uid]['step'] = 'screenshot'
                
                advance_msg = f"""
আপনার অর্ডার প্রায় সম্পূর্ণ!

📦 পণ্য: {s['product_name']}
💰 দাম: {s['price']} টাকা

⚠️ <b>প্রথমে 200 টাকা Advance Bikash এ পাঠান:</b>

📱 <b>Bikash নম্বর: {BIKASH}</b>

✅ <b>এখানে 200 টাকার screenshot পাঠান</b>
                """
                send_msg(cid, advance_msg)
    
    return {'ok': True}

@app.route('/', methods=['GET'])
def home():
    return '🤖 LOZE BD Bot'

if __name__ == '__main__':
    app.run()
