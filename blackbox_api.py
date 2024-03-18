import aiohttp, asyncio, os, mimetypes, aiofiles, textwrap, re, os
from datetime import datetime
from typing import Literal
from io import BufferedReader
from aiohttp_socks import ProxyConnector
from rich.console import Console
from rich.markdown import Markdown
console = Console()
class blackbox_api:
    async def get_trending_agents(proxy: str = None):
        mainpattern = r"function getTrendingAgentImage\(e\)\{return\((.*?)\)"
        scriptspattern = r"<script src=\"(\S+)\" async=\"\">"

        headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        connector = aiohttp.TCPConnector()
        if proxy and "socks5" in proxy:
            connector = ProxyConnector.from_url(proxy)
        found_from_cache = False
        async with aiohttp.ClientSession(connector=connector) as session:
            if os.path.exists("cache.txt"):
                with open("cache.txt", 'r') as f1:
                    url = f1.read()
                async with session.get(url, proxy=proxy if proxy and proxy.startswith("https") else None) as r:
                    response = await r.text(encoding="utf-8")
                    the = re.findall(mainpattern, response)
                    if the:
                        print("found from cache")
                        found_from_cache = True
                    else:
                        print("didnt find from cache")
                        os.remove("cache.txt")
            if not found_from_cache:
                async with session.get("https://blackbox.ai", proxy=proxy if proxy and proxy.startswith("https") else None, headers=headers) as r:
                    response = await r.text()
                    the = re.findall(scriptspattern, response)
                    if the:
                        print("found scripts", end="\r")
                    else:
                        print("couldnt find scripts")
                        return None
                for match in the:
                    async with session.get("https://blackbox.ai" + match, proxy=proxy if proxy and proxy.startswith("https") else None) as r:
                        response = await r.text(encoding="utf-8")
                        the = re.findall(mainpattern, response)
                        if the:
                            print("found function in %s" % "https://blackbox.ai" + match)
                            with open("cache.txt", "w") as f1:
                                f1.write("https://blackbox.ai" + match)
                            break
                        else:
                            print("couldnt find function in %s" % "https://blackbox.ai" + match, end="\r")
        if not the:
            return None
        parsepattern = r"(?:,|\{)?(\w*?):"
        trendingagents = []
        for i in re.findall(parsepattern, the[0]):
            if i and not i == "https":
                trendingagents.append(i)
        return trendingagents
    async def blackbox(query: str = None, history: list[dict] = None, mode: Literal['continue'] = None, 
                       upload: str | bytes | BufferedReader = None, proxy: str = None, chunk_size: int = None,
                       trending_agent: str = None):
        """
        Args:
            query (str) - what to ask the ai
            history (list[dict]) - history to give to the ai. should be like [{"content": "", "role": "user"/"assistant"}]
            mode (Literal['continue']) - whether to make ai continue from what it last said, required on if no query
            upload (str OR bytes OR BufferedReader) - file to upload to the ai, can be https link, path, bytes or a reader (open(file, 'rb'))
            proxy (str) - proxy to use, can be socks5 or https
            chunk_size (int) - yield text with that size, if None, yield as you receive the response
            trending_agent(str) - trending agent to use, you can get a list from the get_trending_agents
        """
        if mode and not query and not history:
            raise ValueError("ai requires history to continue what they were saying")
        if history and not query and not mode:
            raise ValueError("ai requires a prompt or a mode, not just history")
        connector = aiohttp.TCPConnector()
        if proxy and "socks5" in proxy:
            connector = ProxyConnector.from_url(proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            headers = {
                'authority': 'www.blackbox.ai',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://www.blackbox.ai',
                'referer': 'https://www.blackbox.ai/',
                'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            }
            if upload:
                if os.path.exists(upload):
                    mime = mimetypes.guess_type(upload)[0]
                    data = aiohttp.FormData()
                    data.add_field("image", open(upload ,'rb'), filename=upload, content_type=mime)
                elif upload.startswith("https://"):
                    tempfile = f"tempfile{int(datetime.now().timestamp())}"
                    async with aiofiles.open(tempfile, "wb") as f1:
                        async with session.get(upload, proxy=proxy if proxy and proxy.startswith("https") else None) as r:
                            mime = r.headers.get("content-type")
                            while True:
                                chunk = await r.content.read(1024)
                                if not chunk:
                                    break
                                await f1.write(chunk)
                    filename = f"{mime.split('/')[0]}-{int(datetime.now().timestamp())}.{mime.split('/')[1].replace('quicktime', 'mov')}"
                    os.rename(tempfile, filename)
                    data = aiohttp.FormData()
                    data.add_field(name="image", filename=filename, content_type=mime, value=open(filename,'rb'))
                    data.add_field(name="fileName", value=filename)
                elif isinstance(upload, bytes):
                    tempfile = f"tempfile{int(datetime.now().timestamp())}"
                    async with aiofiles.open(tempfile, "wb") as f1:
                        await f1.write(upload)
                    mime = mimetypes.guess_type(tempfile)[0]
                    filename = f"{mime.split('/')[0]}-{int(datetime.now().timestamp())}.{mime.split('/')[1].replace('quicktime', 'mov')}"
                    os.rename(tempfile, filename)
                    data = aiohttp.FormData()
                    data.add_field(name="image", filename=filename, content_type=mime, value=open(filename,'rb'))
                    data.add_field(name="fileName", value=filename)
                elif isinstance(upload, BufferedReader):
                    tempfile = f"tempfile{int(datetime.now().timestamp())}"
                    async with aiofiles.open(tempfile, "wb") as f1:
                        await f1.write(upload.read())
                    mime = mimetypes.guess_type(tempfile)[0]
                    filename = f"{mime.split('/')[0]}-{int(datetime.now().timestamp())}.{mime.split('/')[1].replace('quicktime', 'mov')}"
                    os.rename(tempfile, filename)
                    data = aiohttp.FormData()
                    data.add_field(name="image", filename=filename, content_type=mime, value=open(filename,'rb'))
                    data.add_field(name="fileName", value=filename)
                async with session.post('https://www.blackbox.ai/api/upload', data=data, proxy=proxy if proxy and proxy.startswith("https") else None) as r:
                    response = await r.json()
                    response = response['response']
                query = f"FILE:BB\n$#$\n{response}\n$#$\{query}" if len(response.replace("\n", "")) < 1 else f"{response}{query}"
            json_data = {
                'previewToken': None,
                'codeModelMode': True,
                'agentMode': {},
                'trendingAgentMode': {},
                'isMicMode': False,
                'isChromeExt': False,
                'githubToken': None,
                'mode': mode
            }
            if trending_agent and not mode:
                json_data['trendingAgentMode'] = {"mode": True, "id": trending_agent}
            if history:
                if not mode:
                    history.append({'content': query,'role': 'user',})
                json_data['messages'] = history
            if not mode:
                json_data['messages'] = [{'content': query,'role': 'user',}]

            url = 'https://www.blackbox.ai/api/chat'
            temp = ""
            error = False
            async with session.post(url, headers=headers, json=json_data, proxy=proxy if proxy and proxy.startswith("https") else None) as r:
                if r.status not in [200, 206]:
                    yield f"ERROR: STATUS CODE: {r.status}"
                    error = True
                if not error:
                    while True:
                        chunk = await r.content.read(1024)
                        if not chunk:
                            break
                        if not chunk_size:
                            yield chunk.decode()
                        else:
                            if len(temp) + len(chunk.decode()) < chunk_size:
                                temp += chunk.decode()
                            elif len(temp) + len(chunk.decode()) == chunk_size:
                                yield temp + chunk.decode()
                                temp = ""
                            elif len(temp) + len(chunk.decode()) > chunk_size:
                                for i in textwrap.wrap(temp+chunk.decode(), chunk_size, replace_whitespace=False, drop_whitespace=False):
                                    yield i
                                temp = ""
                    if temp:
                        yield temp
async def main():
    history = []
    mode = None
    agent = None
    agents = []
    upload = None
    while True:
        query = str(input("query: "))
        if query == "continue":
            mode = "continue"
        else:
            mode = None
        if query == "history":
            console.print(history)
            continue
        if query == "exit":
            break
        if query == "cls" or query == "clear":
            os.system("cls")
            continue
        if query == "getagents":
            agents = await blackbox_api.get_trending_agents()
            console.print(await blackbox_api.get_trending_agents())
            continue
        if query == "setagent":
            agent = str(input("which agent to use: "))
            if agent not in agents:
                print("this agent isnt in the trending ones or you havent checked the trending ones, but still gonna try it")
            continue
        if query == "removeagent":
            agent = None
            continue
        if query == "upload":
            upload = str(input("path or url to what you want to upload: "))
            query = str(input("query to go with that: "))
        botresponse = ""
        async for msg in blackbox_api.blackbox(query=query if query != "continue" else None, history=history if history else None, mode=mode, chunk_size=20, trending_agent=agent, upload=upload):
            botresponse += msg
            print(msg, end="")
        print(f"\n\n\n\n\n\n\n\nquery: {query}\n")
        botresponsemd = Markdown(botresponse)
        console.print(botresponsemd)
        history.append({"content": query, "role": "user"})
        history.append({"content": botresponse, "role": "assistant"})
        botresponse = ""
if __name__ == "__main__":
    asyncio.run(main())