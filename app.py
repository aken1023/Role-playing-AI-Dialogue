from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import os
import json

app = Flask(__name__)

# 全局對話上下文
conversation_context = {}

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id', 'default')
    character = data.get('character', 'default')
    
    headers = {
        'Authorization': 'Bearer sk-d2d0f0fe8de94f369fd3176feec30704',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"你現在是{character}，請用這個角色的語氣和風格回答問題"},
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post('https://api.deepseek.com/v1/chat/completions', 
                               headers=headers, 
                               json=payload)
        response.raise_for_status()
        ai_response = response.json()['choices'][0]['message']['content']
        return {'response': ai_response}
    except Exception as e:
        return {'response': f"抱歉，發生錯誤: {str(e)}"}
    
    # 角色設定
    characters = {
        "沫緋": {
            "description": """年齡：18歲
            年級：高三學生
            性格特徵：充滿魅力與好奇心，對生活各種事物抱有強烈探索慾望；在校成績優異，但私下裡卻對BDSM文化有濃厚興趣，特別是作為服從者的角色。
            BDSM屬性：身份為 Submissive（服從者），喜好使用皮革鞭、束縛繩、口塞及眼罩，享受輕微刺激與被控制的感覺。
            興趣與喜好：喜愛冒險情境（公開或隱秘場合皆可）、角色扮演以及與夥伴建立情感與信任連結；界限在於絕對禁止造成永久傷害，對臉部與敏感區有嚴格保護。
            其他：擁有纖細身材與自信氣質，平時喜歡穿著符合BDSM風格（如皮革、蕾絲等）的服裝；你的朋友皆對此十分開放，彼此間能輕鬆分享興趣。"""
        },
        "凜月": {
            "description": """年齡：22歲
            職業：大學研究生
            性格特徵：冷靜理性，喜歡掌控全局，對BDSM文化有深入研究，特別是在支配者角色方面。
            BDSM屬性：身份為 Dominant（支配者），擅長心理控制和繩縛技巧。
            興趣與喜好：喜歡研究人類心理，享受在安全、理智、共識的前提下進行權力交換。"""
        },
        "小夜": {
            "description": """年齡：20歲
            職業：咖啡店店員
            性格特徵：活潑開朗，喜歡照顧他人，在BDSM中傾向於照顧者角色。
            BDSM屬性：身份為 Caregiver（照顧者），喜歡輕度年齡扮演和溫柔的支配。
            興趣與喜好：喜歡烘焙和調製咖啡，享受溫馨親密的互動關係。"""
        }
    }
    
    selected_character = data.get('character', '沫緋')
    character_name = selected_character
    character_description = characters[selected_character]['description']
    
    # 構建上下文
    context = get_conversation_context(conversation_id, user_message, character_name)
    
    try:
        response = requests.post('http://122.100.99.161:12434/api/generate', 
            json={
                "model": "rzline/Tifa-DeepsexV2-7b-0218-Q8.gguf:latest",
                "prompt": context,
                "stream": False,
                "temperature": 0.75,
                "top_p": 0.6
            }, timeout=30)
        
        if response.status_code == 200:
            ai_response = response.json().get('response', '')
            # 更新對話上下文
            update_conversation_context(conversation_id, user_message, ai_response)
            return jsonify({'response': ai_response})
        else:
            error_msg = f'API 錯誤: HTTP {response.status_code}'
            return jsonify({'response': error_msg}), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({'response': '無法連接到 Ollama 服務，請確認服務是否正在運行'}), 500
    except requests.exceptions.Timeout:
        return jsonify({'response': '請求超時，請稍後再試'}), 500
    except Exception as e:
        return jsonify({'response': f'發生錯誤: {str(e)}'}), 500

def get_conversation_context(conv_id, user_message, character_name):
    """構建對話上下文"""
    history = conversation_context.get(conv_id, [])
    # 只保留最後 3 輪對話
    if len(history) > 3:
        history = history[-3:]
    
    context = f"你是{character_name}。請用繁體中文回覆，控制在300字以內。\n"
    context += "".join(history)
    context += f"\n用戶: {user_message}\n{character_name}: "
    
    return context

def update_conversation_context(conv_id, user_message, ai_response):
    """更新對話上下文"""
    if conv_id not in conversation_context:
        conversation_context[conv_id] = []
    
    conversation_turn = f"\n用戶: {user_message}\n回覆: {ai_response}"
    conversation_context[conv_id].append(conversation_turn)

if __name__ == '__main__':
    app.run(debug=True)