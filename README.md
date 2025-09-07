# Qala WhatsApp Bot

A WhatsApp webhook bot built with Twilio for processing candidate video assessments in Qala's hiring pipeline. This bot streamlines the recruitment process by automatically handling candidate interactions, collecting video submissions, and facilitating the assessment workflow through WhatsApp messaging.

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- A Twilio account with WhatsApp Business API access
- Flask framework knowledge
- ngrok or similar tool for webhook testing (development)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/qala-work/qala-whatsappbot.git
   cd qala-whatsappbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your Twilio credentials
   ```


## 🏃‍♂️ Running the Application

### Development Mode

1. **Start the Flask application**
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

2. **Set up ngrok for webhook testing**
   ```bash
   ngrok http 5000
   ```

3. **Configure Twilio webhook URL**
   - Copy the ngrok HTTPS URL
   - Set webhook URL in Twilio Console: `https://your-ngrok-url.ngrok.io/webhook`


**Built with ❤️ by the Qala Team**

*Empowering African talent through innovative hiring solutions*
