from telegram import *
import telegram.ext
import os
from telegram import Update
import requests
import datetime
from decouple import config

TOKEN = config("TOKEN", default="")
ADMIN_CHAT_ID = config("ADMIN_CHAT_ID", default="")
Programmer_CHAT_ID = config("PROGRAMMER_CHAT_ID", default="")
address = config("ADDRESS", default="")


async def start_command(update:Update,context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton("register")],[KeyboardButton("login")]]
    user_id = update.effective_message.chat_id

    user = update.message.from_user
    if int(user_id) == int(Programmer_CHAT_ID):
        context.job_queue.run_repeating(callback=open_positions,interval=5,chat_id=user_id,user_id=user_id)
        context.job_queue.run_repeating(callback=deposit,interval=5,chat_id=user_id,user_id=user_id)
        context.job_queue.run_repeating(callback=withdraw,interval=5,chat_id=user_id,user_id=user_id)
        context.job_queue.run_repeating(callback=closedposition,interval=5,chat_id=user_id,user_id=user_id)
        context.job_queue.run_daily(callback=expiration_message,time=datetime.time(hour=17, minute=4, second=0),days=(0, 1, 2, 3, 4, 5, 6),chat_id=user_id,user_id=user_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="welcome!", reply_markup=ReplyKeyboardMarkup(buttons))



async def open_positions(context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    req_channel = requests.get("http://localhost:8000/dydx/api/v1/telegramchannel/")
    data_channel = req_channel.json()
    req_openpositions = requests.get("http://localhost:8000/dydx/api/v1/openpositions/")
    openpositionsdata = req_openpositions.json()
    
    for user,opened in openpositionsdata.items():
        for new_pos in opened:
            user_id = openpositionsdata[user][0]["telegram_user"]
            if new_pos['channel_sent'] == False:
                body = {"channel_sent": True}
                change_status_req = requests.patch( 
                f"http://localhost:8000/dydx/api/v1/openpositions/{new_pos['id']}/",body)
                if not change_status_req.status_code == 200:
                    continue
                channel_id = data_channel[user_id]["channel_id"]
                if new_pos['long'] == True:
                    dir = f"📈Long Size: {round(new_pos['size_channel'],2)} $"
                else:
                    dir = f"📉short Size: {round(new_pos['size_channel'],2)} $"

                text_open = f"""
#Open #{new_pos['wallet_name']}
position id: #{int(new_pos["make_position"])+1000}
🗓 {new_pos['created_date']} 🗓 {new_pos['created_date_shamsi']} 🗓
📊 Positions Opened
🪙 At: {round(new_pos['average_open'])}
{dir}
"""         
                await context.bot.send_message(text=text_open,chat_id = channel_id)

    for user,opened in openpositionsdata.items():
        for pos in opened:
            user_id = openpositionsdata[user][0]["telegram_user"]
            if pos['channel_edited'] == False:
                body = {"channel_edited": True}
                change_status_req = requests.patch( 
                f"http://localhost:8000/dydx/api/v1/openpositions/{pos['id']}/",body)
                if not change_status_req.status_code == 200:
                    continue
                channel_id = data_channel[user_id]["channel_id"]

                if pos['long'] == True:
                    dir = f"📈Long Size: {round(pos['size_channel'],2)} $ added"
                else:
                    dir = f"📉short Size: {round(pos['size_channel'],2)} $ added"
                text_open = f"""
#add #{pos['wallet_name']} 
position id: #{int(pos["make_position"])+1000}
🗓 {pos['created_date']} 🗓 {pos['created_date_shamsi']} 🗓
📊 Positions Changed
🪙 At: {round(pos['average_open'],2)}
{dir}
"""                         
                await context.bot.send_message(text=text_open,chat_id = channel_id)
        

async def closedposition(context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    req_channel = requests.get("http://localhost:8000/dydx/api/v1/telegramchannel/")
    data_channel = req_channel.json()
    req_closeddata = requests.get("http://localhost:8000/dydx/api/v1/closedposition/")
    closed_data = req_closeddata.json()

    for user,closed in closed_data.items():
        for pos in closed:
            user_id = closed_data[user][0]["telegram_user"]
            if pos['channel_sent'] == False:
                body = {"channel_sent": True}
                change_status_req = requests.patch( 
                f"http://localhost:8000/dydx/api/v1/closedposition/{pos['id']}/",body)
                if not change_status_req.status_code == 200:
                    continue
                if pos['size'] == 0:
                    continue
                profit_perc = pos['profit']/pos['size'] * 100
                channel_id = data_channel[user_id]["channel_id"]
                if pos['long'] == True:
                    dir = f"Long📈"
                else:
                    dir = f"short📉"


                text_open = f"""
#{pos['wallet_name']}
#Close #{dir}
position id: #{int(pos["make_position"])+1000} 
🗓 {pos['created_date']} 🗓 {pos['created_date_shamsi']} 🗓
🔔 End of Position, {dir}
💲 Size USDT: {round(pos['size'],2)} $
🔼 Pure Profit: {round(pos["profit"],2)} $ ({round(profit_perc,2)}%) 
🔥 New balance: {round(pos['balance'],2)} $ (+N/A$)
"""         
                await context.bot.send_message(text=text_open,chat_id = channel_id)


async def deposit(context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    req_channel = requests.get("http://localhost:8000/dydx/api/v1/telegramchannel/")
    data_channel = req_channel.json()
    req_depositdata = requests.get("http://localhost:8000/dydx/api/v1/deposit/")
    deposit_data = req_depositdata.json()
    
    for user,deposits in deposit_data.items():
        for depos in deposits:
            user_id = deposit_data[user][0]["telegram_user"]
            if depos['channel_sent'] == False:
                body = {"channel_sent": True}
                change_status_req = requests.patch(
                f"http://localhost:8000/dydx/api/v1/deposit/{depos['id']}/",body)
                if not change_status_req.status_code == 200:
                    continue
                channel_id = data_channel[user_id]["channel_id"]
                if depos['wallettype'] == "Uniswap":
                    wallettype = f"""
Uniswap: {depos['volume']} $
1Inch: 0.00 $
"""
                else:
                    wallettype = f"""
Uniswap: 0.00 $ 
1Inch: {depos['volume']} $
"""

                text_open = f"""
#Deposit #{depos['wallet_name']}
🗓 {depos['created_date']} 🗓 {depos['created_date_shamsi']} 🗓
➡️🤑💲 Deposit: {depos['volume']} $
{wallettype}
New balance: {depos['balance']} $
"""         
                await context.bot.send_message(text=text_open,chat_id = channel_id)


async def withdraw(context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    req_channel = requests.get("http://localhost:8000/dydx/api/v1/telegramchannel/")
    data_channel = req_channel.json()
    req_withdrawdata = requests.get("http://localhost:8000/dydx/api/v1/withdraw/")
    withdraw_data = req_withdrawdata.json()
    
    for user,withdraws in withdraw_data.items():
        for withdraw in withdraws:
            user_id = withdraw_data[user][0]["telegram_user"]
            if withdraw['channel_sent'] == False:
                body = {"channel_sent": True}
                change_status_req = requests.patch( 
                f"http://localhost:8000/dydx/api/v1/withdraw/{withdraw['id']}/",body)
                if not change_status_req.status_code == 200:
                    continue
                channel_id = data_channel[user_id]["channel_id"]
                if withdraw['wallettype'] == "Uniswap":
                    wallettype = f"""
Uniswap: {withdraw['volume']} $
1Inch: 0.00 $
"""
                else:
                    wallettype = f"""
Uniswap: 0.00 $ 
1Inch: {withdraw['volume']} $
"""

                text_open = f"""
#{withdraw['wallet_name']}
#Withdraw 
🗓 {withdraw['created_date']} 🗓 {withdraw['created_date_shamsi']} 🗓
🔙🤑💲 Withdraw: {withdraw['volume']} $
{wallettype}
Status: Successfully Transferred ✅
ETR: 96 Hrs
"""         
                await context.bot.send_message(text=text_open,chat_id = channel_id)

        

async def expiration_message(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    req_channel = requests.get("http://localhost:8000/dydx/api/v1/telegramchannel/")
    data_channel = req_channel.json()
    staking_data = requests.get("http://localhost:8000/dydx/api/v1/staking/")
    staking_data = staking_data.json()

    for stake in staking_data:
        if stake['days_left'] < 3:
            user_id = stake["telegram_user"]
            if user_id in data_channel.keys():
                channel_id = data_channel[user_id]["channel_id"]
                text = f"""your stake with volume:{stake['staking_volume']} and date:{stake['staking_date']}
after {stake['days_left']} days will be expired.
"""         
                await context.bot.send_message(text=text,chat_id = channel_id)


if __name__=='__main__':

    app = telegram.ext.Application.builder().token(TOKEN).build()
    #commands
    app.add_handler(telegram.ext.CommandHandler('start',start_command))
    app.run_polling()


