#Go Travel
This telegram bot allows you to search hotels


### To install locally:

1. Download this repository
2. Create a file *.env* in the downloaded directory
3. Find Bot-Father in telegram. Register a new bot and copy his *token*
4. Add this strings to the *.env* file and save it:
        
        BOT_TOKEN=*your token*
        API_KEY=29265c1e4bmsh2cd19e7bab9e2abp1ee17ejsna86ae3426e38
        API_HOST=hotels4.p.rapidapi.com

5. Navigate to this directory in the terminal and enter:
        
        pip install -r requirements.txt

6. Run script:

        python main.py

7. Bot commands
        
        /start - запуск бота
        /help — помощь по командам бота
        /lowprice — вывод самых дешёвых отелей в городе
        /highprice — вывод самых дорогих отелей в городе
        /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра
        /history - вывод истории поиска отелей

8.***Enjoy***