# Simple Blackbox.ai API script
completely free (for now) authentication-less llm with file reading capabilities and larger input capablity

[https://blackbox.ai](https://blackbox.ai)
## Installation
1. Install [python (3.6-3.11)](https://python.org)
2. in terminal
```bash
git clone https://github.com/Hecker5556/blackbox_api
```
3. in terminal
```bash
cd blackbox_api
```
4. in terminal
```bash
pip install -r requirements.txt
```

## Usage
In terminal:
```bash
python blackbox_api.py
```
this will open a loop where you can text the bot, and stream the response. every response and query for the session will be sent as history.

terminal commands:
exit - exits
cls/clear - clears the terminal
continue - if ai cuts off, u can send a continue request
history - prints out current session history
getagents - prints out a list of trending agents 
setagent - prompts to set agent for use with the bot
removeagent - removes the currently used agent
upload - upload something from a path or a url

In python
```python
from blackbox_api import backbox_api
async def main():
    async for msg in blackbox_api.blackbox(query="how are you"):
        print(msg, end="")
    trending_agents = await blackbox_api.get_trending_agents()
    # for use with trending_agent parameter
```

Parameters:
* query (str) - what to ask the ai
* history (list[dict]) - history to give to the ai. should be like [{"content": "", "role": "user"/"assistant"}]
* mode (Literal['continue']) - whether to make ai continue from what it last said, required on if no query
* upload (str OR bytes OR BufferedReader) - file to upload to the ai, can be https link, path, bytes or a reader (open(file, 'rb'))
* proxy (str) - proxy to use =, can be socks5 or https
* chunk_size (int) - yield text with that size, if None, yield as you receive the response
* trending_agent(str) - trending agent to use, you can get a list from the get_trending_agents