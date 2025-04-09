"""
Show how to use custom outputs.

@dev You need to add OPENAI_API_KEY to your environment variables.
"""
import os
import sys
import pydantic
import asyncio

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from browser_use import Browser, Agent, Controller
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
from models.ca_firstnations_model import FirstNation

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

controller = Controller(output_model=FirstNation)

config = BrowserContextConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    wait_between_actions=1.0,
)

browser = Browser()
context = BrowserContext(browser=browser, config=config)

async def run_search() -> AgentHistoryList:
    task = ("1. Input 'Campbell River' in the 'Name' text input field."
            "2. Click the 'Search' button."
            "3. Check the link matching the name"
            "4. Extract the 'Official Name', 'Number', 'Address', 'Postal Code', 'Phone', 'Fax', and 'Website'."
            )
    llm = ChatOllama(
        model='qwen2.5:14b',
        num_ctx=6000,
        temperature=0.0,
        keep_alive=120
    )

    initial_actions = [
        {'go_to_url': {'url': 'https://fnp-ppn.aadnc-aandc.gc.ca/fnp/Main/Search/SearchFN.aspx?lang=eng'}},
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
    result = history.final_result()

    durations+=(history.total_duration_seconds())
    tokens+=(history.total_input_tokens())

    if result:
        try:
            parsed: FirstNation = FirstNation.model_validate_json(result)
            fn_num = parsed.number
            with open(f"/home/daniel/projects/outputs/json/ca/FirstNation_{fn_num}.json", 'w', encoding="utf-8") as file:
                file.write(parsed.model_dump_json(indent=4))
            print(parsed.model_dump_json(indent=4))
        except pydantic.ValidationError:
            print("invalid json model, web scrap failed")
        except OSError:
            print(f"error with writing file")
    else:
        print("no results")

    print(f"Time duration: {durations}")
    print(f"Input tokens: {tokens}")

    await browser.close() #there's a bug with Browser-Use not closing correctly if using local Chrome


if __name__ == '__main__':
    asyncio.run(main())
