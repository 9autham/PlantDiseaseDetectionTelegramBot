# your code goes here
import telebot
import requests
import json
import base64
import time
 
# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '6010056833:AAGkDj_4bHGS_VJGKpPYf7jmPj1P9nTZXW0'
 
# Telegram Bot Instance
bot = telebot.TeleBot(bot_token)
 
# Define your Plant.id API key
api_key = 't7z2V3XOUJ1sEYLyBo345KTtVhwhjuGuFyh4yGsPle97k3pZdM'
 
 
 
# Handle the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    greeting_msg1="🌿🌱🤖 Welcome to the Plant Health Hub! 🌱🌿🔍\nAre your plants feeling under the weather? Fret not! You've stumbled upon your very own plant whisperer. Just share an image of your plant, and I'll work my magic to assess its health. Whether it's a flourishing garden companion or a potted buddy, I've got the expertise to spot potential issues.\n"
    greeting_msg2="Simply snap a clear picture, send it my way, and let's embark on the journey to greener and healthier plants! If you ever doubt your plant's well-being, remember that I'm just a message away. Let's nurture those greens back to life! 🌞🌼🌱\n"
    greeting_msg3="Think of me as your virtual plant doctor, here to assist you anytime, anywhere. So, don't hesitate to share snapshots of your beloved plants. Together, we'll ensure lush gardens, vibrant windowsills, and thriving botanical corners. Your plant's well-being begins right here! 🌾🌷🍃"
    bot.reply_to(message, greeting_msg1)
    time.sleep(1);
    bot.send_message(message.chat.id, greeting_msg2)
    time.sleep(1);
    bot.send_message(message.chat.id, greeting_msg3)
 
# Handle incoming images
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        # Get the file ID of the largest available photo
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
 
        # Download the image from Telegram servers
        # image_url = f'https://a...content-available-to-author-only...m.org/file/bot{bot_token}/{file_info.file_path}'
        image_url = f'https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}'

        response = requests.get(image_url)
 
        # Encode the image data in base64
        encoded_image_data = base64.b64encode(response.content).decode('utf-8')
        # Create JSON payload for API request
        payload = {
            'api_key': api_key,
            'images': [encoded_image_data],
            'modifiers': ['crops_fast', 'similar_images'],
            'language': 'en',
            'disease_details': ['cause', 'common_names', 'classification', 'description', 'treatment', 'url','is_healthy','is_plant','health_assessment','probability'],
        }
 
        # Send request to Plant.id API
        # url = 'https://a...content-available-to-author-only...t.id/v2/health_assessment'
        url = 'https://api.plant.id/v2/health_assessment'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        #Check Whether it is a plant image or not
        # Display API response
        if response.ok:
            response_data = json.loads(response.content)
            isplant=response_data['is_plant'] #Probablity not included in code!! 
            ishealthy=response_data['health_assessment']['is_healthy'] # is healthy or not
            name = response_data['health_assessment']['diseases'][0]['name'] # Most Accurate dieases name
            probablity = response_data['health_assessment']['diseases'][0]['probability'] # Probability of dieases
            description = response_data['health_assessment']['diseases'][0]['disease_details']['description']
            # You can customize the response format here

            # Checking if chemical_treatment exists in the response{Treatment}
            if 'chemical' in response_data['health_assessment']['diseases'][0]['disease_details']['treatment']:
                chemical_treatments = response_data['health_assessment']['diseases'][0]['disease_details']['treatment']['chemical']
                chemical_treatments_msg = ""
                for treatment in chemical_treatments:
                    chemical_treatments_msg += "✔️ " + treatment + "\n"
            else:
                chemical_treatments_msg = "No specific chemical treatments listed.\n"

            # Checking if biological_treatment exists in the response{Treatment}
            if 'biological' in response_data['health_assessment']['diseases'][0]['disease_details']['treatment']:
                biological_treatments = response_data['health_assessment']['diseases'][0]['disease_details']['treatment']['biological']
                biological_treatments_msg = ""
                for treatment in biological_treatments:
                    biological_treatments_msg += "✔️ " + treatment + "\n"
            else:
                biological_treatments_msg = "No specific biological treatments listed.\n"

            # Checking if prevention exists in the response{Treatment}
            if 'prevention' in response_data['health_assessment']['diseases'][0]['disease_details']['treatment']:
                preventive_measures = response_data['health_assessment']['diseases'][0]['disease_details']['treatment']['prevention']
                preventive_measures_msg = ""
                for measure in preventive_measures:
                    preventive_measures_msg += "✔️ " + measure + "\n"
            else:
                preventive_measures_msg = "No specific preventive measures listed.\n"



            #Check if the image is plant or not!!
            if(isplant==False):
                assessment_result="Whoops! It seems like you've shared a non-plant image. My expertise is in assessing plant health. Please provide an image of a plant, and I'll be more than happy to assist you! 🌿📷"
                bot.reply_to(message, assessment_result) 
            # Check if the plant is healthy or not
            elif(ishealthy==True):
                assessment_result="Great job! You've uploaded an image of a healthy plant. Your green thumb skills are shining bright! If you ever have more plants to check or questions to ask, feel free to share. Happy gardening! 🌱🌿🌼"
                bot.reply_to(message, assessment_result) 
            #if not healthy the else block executes
            else:
                assessment_result="Thank you for sharing the image of your plant. Based on my assessment, it appears that your plant might be experiencing☘️ "+name+" ☘️ with accuracy of "+str(probablity*100)+" %"
                bot.reply_to(message, assessment_result)
                time.sleep(1);
                bot.send_message(message.chat.id,"☘️Description☘️\n\n✔️ "+description)
                bot.send_message(message.chat.id, "☘️Chemical Treatment☘️\n\n"+chemical_treatments_msg)
                time.sleep(1);
                bot.send_message(message.chat.id, "☘️Biological Treatment☘️\n\n"+biological_treatments_msg)
                time.sleep(1);
                bot.send_message(message.chat.id,"☘️Preventive Treatment☘️\n\n"+preventive_measures_msg)
        else:
            bot.reply_to(message, f"Error {response.status_code}: {response.reason}")
 
    except Exception as e:
        # Handle any errors that may occur
        print(str(e))
        bot.reply_to(message, "Oops! Something went wrong.")
 
# Handle any other text messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "I can only handle images. Please send me a plant image.")
 
# Start the Flask web application
if __name__ == "__main__":
    bot.polling()