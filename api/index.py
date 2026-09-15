from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "8992836993:AAGNiuBJGt3HuMyPjtMIQ4GG8XwO8XXl2bE"
BIKASH = "01829244034"
GROUP_CHAT_ID = None  # পরে সেট করব

PRODUCTS = {
    "p1": {"img": "https://ibb.co/prLdYKtT", "price": 1920},
    "p2": {"img": "https://ibb.co/WZjL6kL", "price": 2400},
    "p3": {"img": "https://ibb.co/zHVwDW92", "price": 2000},
    "p4": {"img": "https://ibb.co/8nxCrMFg", "price": 2000},
    "p5": {"img": "https://ibb.co/JFKHWZwS", "price": 1200},
    "p6": {"img": "https://ibb.co/XZtYZHp3", "price": 800},
    "p7": {"img": "https://ibb.co/Hf3938xG", "price": 1200},
    "p8": {"img": "https://ibb.co/twS4gwZ2", "price": 1200},
    "p9": {"img": "https://ibb.co/sd1qJHjm", "price": 560},
    "p10": {"img": "https://ibb.co/4n0hsVCq", "price": 560},
    "p11": {"img": "https://ibb.co/pB8tVFnf", "price": 560},
}

state = {}

def send_msg(cid, txt, img=None):
    if img:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                     json={'chat_id': cid, 'photo': img, 'caption': txt, 'parse_mode': 'HTML'})
    else:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={'chat_id': cid, 'text': txt, 'parse_mode': 'HTML'})

def send_button_msg(cid, txt):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📦 Products", "callback_data": "products"}],
            [{"text": "🛒 Order", "callback_data": "order"}]
        ]
    }
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                 json={'chat_id': cid, 'text': txt, 'reply_markup': keyboard, 'parse_mode': 'HTML'})

@app.route('/api/index', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return {'ok': True}
    
    # Callback query (button click)
    if 'callback_query' in data:
        query = data['callback_query']
        cid = query['message']['chat']['id']
        uid = query['from']['id']
        name = query['from'].get('first_name', 'বন্ধু')
        action = query['data']
        
        if action == 'products':
            send_msg(cid, "💡 আমাদের পণ্য:")
            for p in PRODUCTS.values():
                send_msg(cid, " ", p['img'])
        
        elif action == 'order':
            state[uid] = {'step': 'select_product', 'name': name}
            send_msg(cid, "🛒 কোন পণ্য অর্ডার করবেন?\n\n(নম্বর বলুন: 1-11)\n\nউদাহরণ: 1")
        
        return {'ok': True}
    
    # Message
    if 'message' not in data:
        return {'ok': True}
    
    msg = data['message']
    cid = msg['chat']['id']
    uid = msg['from']['id']
    name = msg['from'].get('first_name', 'বন্ধু')
    txt = msg.get('text', '').lower().strip()
    
    # /start
    if txt == '/start':
        send_button_msg(cid, f"👋 আস্সালামু আলাইকুম {name}!\n\n🎉 LOZE BD এ স্বাগতম!")
    
    else:
        if uid in state:
            s = state[uid]
            
            # পণ্য সিলেক্ট
            if s['step'] == 'select_product':
                try:
                    num = int(txt)
                    if 1 <= num <= 11:
                        key = f"p{num}"
                        state[uid]['product_num'] = num
                        state[uid]['price'] = PRODUCTS[key]['price']
                        state[uid]['step'] = 'name'
                        send_msg(cid, f"✅ পণ্য নির্বাচিত\n💰 দাম: {PRODUCTS[key]['price']} টাকা\n\nআপনার নাম বলুন:")
                    else:
                        send_msg(cid, "❌ 1-11 এর মধ্যে নম্বর বলুন")
                except:
                    send_msg(cid, "❌ নম্বর বলুন (যেমন: 1, 2, 3...)")
            
            # নাম
            elif s['step'] == 'name':
                state[uid]['customer_name'] = txt
                state[uid]['step'] = 'phone'
                send_msg(cid, f"✅ নাম: {txt}\n\nফোন নম্বর বলুন:")
            
            # ফোন
            elif s['step'] == 'phone':
                state[uid]['phone'] = txt
                state[uid]['step'] = 'address'
                send_msg(cid, f"✅ ফোন: {txt}\n\nঠিকানা বলুন:")
            
            # ঠিকানা
            elif s['step'] == 'address':
                total = state[uid]['price']
                adv = 200
                remain = total - adv
                prod_num = state[uid]['product_num']
                
                msg_txt = f"""
✅ অর্ডার কনফার্ম!

📦 পণ্য #: {prod_num}
👤 নাম: {state[uid]['customer_name']}
📱 ফোন: {state[uid]['phone']}
📍 ঠিকানা: {txt}

💰 মোট দাম: {total} টাকা
💳 Advance (Bikash): {adv} টাকা
⏳ বাকি (ডেলিভারিতে): {remain} টাকা

📱 Bikash নম্বর: {BIKASH}

ধন্যবাদ! 🙏
                """
                send_msg(cid, msg_txt)
                
                # GROUP_CHAT_ID এ পাঠাবে (পরে সেট করলে)
                if GROUP_CHAT_ID:
                    send_msg(GROUP_CHAT_ID, f"📋 নতুন অর্ডার!\n{msg_txt}")
                
                del state[uid]
    
    return {'ok': True}

@app.route('/', methods=['GET'])
def home():
    return '🤖 LOZE BD Bot'

if __name__ == '__main__':
    app.run()
