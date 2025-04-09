"""
Code demo for extracting company profile from Washington Secretary of State business search

* uses locally installed Chrome browser instead of Browser-Use Chromium
* business name is hardcoded
* no handling of multiple business in search result

TODO: handle multiple names in search result and determine which one to extract
"""
import os
import sys
import asyncio
import pydantic

from dotenv import load_dotenv
from browser_use import Agent, Controller
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.context import BrowserContextConfig
from browser_use.browser.browser import Browser, BrowserConfig
from langchain_ollama import ChatOllama
from models.us_wa_model import USWABusiness

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

controller = Controller(output_model=USWABusiness)

'''
#Config for built in Chromium browser
browser=Browser()
config = BrowserContextConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    wait_between_actions=2.0,
)
context = BrowserContext(browser=browser, config=config)
'''

#Config for using locally install Chrome browser
browser=Browser(
    config=BrowserConfig(
        browser_binary_path='/usr/bin/google-chrome-stable',
        new_context_config=BrowserContextConfig(
            wait_between_actions=2.0,
            #wait_for_network_idle_page_load_time=1.0,
        )))

async def run_search() -> AgentHistoryList:
    task = ("1. Input 'SEVA BODYWORK LLC' in the 'Business Name' text input field."
            "2. Click the 'Search' button."
            "3. Click the link matching the business name"
            "4. Extract the 'Business Information', 'Registered agent', and list of 'Governors'."
            "5. Close the browser tab."
            )
    llm = ChatOllama(
        model='qwen2.5:14b',
        num_ctx=6000,
        temperature=0.0,
        keep_alive=100
    )

    initial_actions = [
        {'go_to_url': {'url': 'https://ccfs.sos.wa.gov/#/AdvancedSearch'}},
    ]
    agent = Agent(
        #browser_context=context, #switch to built in Chromium
        browser=browser, #use local Chrome browser
        initial_actions=initial_actions,
        task=task,
        llm=llm,
        controller=controller,
    )

    history = await agent.run()
    return history


async def main():
    durations = 0.0
    tokens = 0

    history = await run_search()
    result = history.final_result()
    durations+=(history.total_duration_seconds())
    tokens+=(history.total_input_tokens())

    if result:
        try:
            parsed: USWABusiness = USWABusiness.model_validate_json(result)
            print(parsed.model_dump_json(indent=4))

            company_ubi = parsed.ubi_number
            with open(f"/home/daniel/projects/outputs/json/us/{company_ubi}.txt", 'w', encoding="utf-8") as file:
                file.write(parsed.model_dump_json(indent=4))
        except pydantic.ValidationError:
            print("invalid json model, web scrap failed")
    else:
        print("no results")

    await browser.close()

    print(f"Time duration: {durations}")
    print(f"Input tokens: {tokens}")

if __name__ == '__main__':
    asyncio.run(main())
