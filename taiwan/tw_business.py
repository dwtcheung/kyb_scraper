"""
This is demo code for extracting business entity from
Taiwan Ministry of Economic Affairs

* uses Chromium that came with Playwright
* business name is hardcoded and must be in Chinese
* no handling of multiple business in search result
* single Agent to extract profile, business scopes, and directors

TODO: handle multiple names in search result and determine which one to extract
"""
import asyncio
import os
import sys

import pydantic
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from browser_use import Agent, Controller
from browser_use import Browser
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
from models.tw_business_model import TWBusiness_light

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

#Config for Chromium browser that Playwright uses
config = BrowserContextConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    wait_between_actions=1.0,
)

browser = Browser()
context = BrowserContext(browser=browser, config=config)

async def run_search() -> AgentHistoryList:

    # Define which JSON model to use during data extract
    controller = Controller(output_model=TWBusiness_light)

    task = ("1. Input '華碩電腦股份有限公司' in text input field."
            "2. Click the 'Search' button."
            "3. Check the link matching the name"
            "4. Extract the 'Company Profile'. Scroll down and extract 'Business Scope' with 'Code' and 'Description'. Make sure to extract all of them."
            )

    llm = ChatOllama(
        model='qwen2.5:14b',
        num_ctx=6000,
        temperature=0.0,
        keep_alive=300
    )

    initial_actions = [
        {'go_to_url': {'url': 'https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do?request_locale=en&fhl=en'}},
    ]
    agent = Agent(
        browser_context=context,
        initial_actions=initial_actions,
        task=task,
        llm=llm,
        controller=controller
    )

    history = await agent.run()
    return history

async def main():
    durations = 0.0
    tokens = 0

    history = await run_search()
    output = history.final_result()
    tokens += (history.total_input_tokens())

    if output:
        try:
            parsed: TWBusiness_light = TWBusiness_light.model_validate_json(output)
            print(parsed.model_dump_json(indent=4))
        except pydantic.ValidationError:
            print("invalid json, web scrap failed")

    else:
        print("no results")

    print(f"Time duration: {durations}")
    print(f"Input tokens: {tokens}")

    await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
