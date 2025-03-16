def send_ai_chat_page(self):
    """Send the AI chat interface page"""
    self.send_response(200)
    self.send_header('Content-type', 'text/html; charset=UTF-8')
    self.end_headers()
    
    # Define HTML content - using a simple approach to avoid syntax issues
    username = current_user["username"] if current_user["username"] else "کاربر"
    
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>چت هوشمند</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ecf0f1;
            direction: rtl;
            margin: 0;
            padding: 0;
        }
        .navbar {
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
        }
        .content {
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .chat-container {
            background-color: #1e1e1e;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .ai-message {
            background-color: rgba(0, 255, 170, 0.1);
            border: 1px solid #00ffaa;
        }
        .user-message {
            background-color: rgba(0, 170, 255, 0.1);
            border: 1px solid #00aaff;
            text-align: left;
        }
        .input-area {
            display: flex;
            margin-top: 20px;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #2d2d2d;
            background-color: #1a1a1a;
            color: #ecf0f1;
            border-radius: 4px;
            margin-left: 10px;
        }
        button {
            padding: 10px 20px;
            background-color: transparent;
            color: #00ffaa;
            border: 1px solid #00ffaa;
            border-radius: 4px;
            cursor: pointer;
        }
        h1, h2 {
            color: #00ffaa;
        }
        a {
            color: #ecf0f1;
            text-decoration: none;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Persian Life Manager</h1>
        <div>
            <a href="/dashboard">داشبورد</a>
            <a href="/finance">مالی</a>
            <a href="/health">سلامت</a>
            <a href="/calendar">تقویم</a>
            <a href="/ai-chat">چت هوشمند</a>
            <a href="/logout">خروج</a>
        </div>
    </div>
    
    <div class="content">
        <h2>چت هوشمند</h2>
        
        <div class="chat-container" id="chat-container">
            <div class="message ai-message">سلام ''' + username + '''! من دستیار هوشمند Persian Life Manager هستم. چطور می‌توانم به شما کمک کنم؟</div>
        </div>
        
        <div class="input-area">
            <input type="text" id="user-input" placeholder="پیام خود را بنویسید...">
            <button id="send-button">ارسال</button>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            let chatHistory = [];
            
            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
                messageDiv.textContent = content;
                chatContainer.appendChild(messageDiv);
            }
            
            async function sendMessage(message) {
                if (!message.trim()) return;
                
                addMessage(message, true);
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            history: chatHistory
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        addMessage('متأسفانه خطایی رخ داد: ' + data.error, false);
                    } else {
                        addMessage(data.response, false);
                        
                        chatHistory.push({
                            role: 'user',
                            content: message
                        });
                        
                        chatHistory.push({
                            role: 'assistant',
                            content: data.response
                        });
                    }
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.', false);
                }
            }
            
            sendButton.addEventListener('click', function() {
                const message = userInput.value;
                if (message.trim()) {
                    sendMessage(message);
                    userInput.value = '';
                }
            });
            
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const message = userInput.value;
                    if (message.trim()) {
                        sendMessage(message);
                        userInput.value = '';
                    }
                }
            });
        });
    </script>
</body>
</html>
'''
    self.wfile.write(html_content.encode('utf-8'))