# data-science-reddit
### Execution Instructions
The user of the script will need to get a Reddit API key. To do this they will need to go to the following link: **https://www.reddit.com/prefs/apps** and create a new Reddit App. The app should be a **script**. It does not matter what they name it. It should probably just use **http://localhost:8080** as a redirect uri.
Once they have created the app, they will need to create a file in the same directory as the script called **client_info.json** and it should be formatted like so:
```json
{
    "client_id": "14_CHARACTER_CLIENT_ID",
    "client_secret": "27_CHARACTER_SECRET_KEY",
    "user_agent": "WHATEVER_YOU_NAMED_THE_APP",
    "username": "YOUR_REDDIT_USERNAME",
    "password": "YOUR_REDDIT_PASSWORD"
}
```
For obvious reasons, we cannot share our passwords or secret keys.
Once the user has set up their authentication, ensure that the following two folders are present in the same directory as the script: **republicans/** and **democrats/**. After that, run the script with the following command: python **rtdata.py** and it will fill these folders with files corresponding with both recent and popular posts in **r/republicans** and **r/democrats**. 