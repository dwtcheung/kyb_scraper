"""
This is demo code for extracting business entity from
Taiwan Ministry of Economic Affairs

* uses Chromium that came with Playwright
* business name is hardcoded and must be in Chinese
* no handling of multiple business in search result
* multiple Agents to extract profile, business scopes, and directors
* different model size and context used in Agents
* slightly faster than single Agent

TODO: handle multiple names in search result and determine which one to extract
"""
import json
import os
import sys
import asyncio

from typing import List, Optional

import pydantic

from browser_use import Browser,Agent, Controller
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from models.tw_business_model_multi import TWBusiness, TWDirectors, TWBusinessScopes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# Config for Chromium that Playwright uses
config = BrowserContextConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    wait_between_actions=1.0,
)

browser = Browser()
context = BrowserContext(browser=browser, config=config)

async def run_search() -> AgentHistoryList:
    task = ("1. Input '華碩電腦股份有限公司' in text input field."
            "2. Click the 'Search' button."
            "3. Check the link matching the name"
            "4. Extract the 'Company Profile', ignore Business Scope.'."
            )
    llm = ChatOllama(
        model='qwen2.5:14b',
        num_ctx=6000,
        temperature=0.0,
        keep_alive=300
    )

    controller = Controller(output_model=TWBusiness)
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

async def extract_scope() -> AgentHistoryList:
    llm = ChatOllama(
        model='qwen2.5:7b',
        num_ctx=35000,
        temperature=0.0,
        keep_alive=300
    )
    controller = Controller(output_model=TWBusinessScopes)
    task = "1. Scroll down and extract 'Business Scope' with 'Code' and 'Description'. Make sure to extract all of them."
    agent = Agent(
        browser_context=context,
        task=task,
        llm=llm,
        controller=controller
    )

    history = await agent.run()
    return history


async def extract_directors() -> AgentHistoryList:
    llm = ChatOllama(
        model='qwen2.5:7b',
        num_ctx=35000,
        temperature=0.0,
        keep_alive=300
    )
    controller = Controller(output_model=TWDirectors)
    task = "1. Click 'Directors and Supervisors' and extract 'Directors and Supervisors'."
    agent = Agent(
        browser_context=context,
        task=task,
        llm=llm,
        controller=controller
    )

    history = await agent.run()
    return history


async def main():
    durations = 0.0
    tokens = 0
    profile_dict = None
    scope_dict = None
    director_dict = None
    company_num = str

    #Extract company profile without business scope and directors
    history = await run_search()
    profile_result = history.final_result()
    durations += (history.total_duration_seconds())
    tokens += (history.total_input_tokens())

    #Extract list of business scopes
    b_history = await extract_scope()
    b_result = b_history.final_result()
    durations += (b_history.total_duration_seconds())
    tokens += (b_history.total_input_tokens())

    #Extract list of directors
    d_history = await extract_directors()
    d_result = d_history.final_result()
    durations += (d_history.total_duration_seconds())
    tokens += (d_history.total_input_tokens())

    if profile_result:
        try:
            parsed: TWBusiness = TWBusiness.model_validate_json(profile_result)
            profile_dict = parsed.model_dump()
            company_num = parsed.unified_business_no
        except pydantic.ValidationError:
            print("invalid json, web scrap failed")
            sys.exit("invalid json, web scrap failed")
    else:
        print("no results")

    if b_result:
        try:
            parsed: TWBusinessScopes = TWBusinessScopes.model_validate_json(b_result)
            scope_dict = parsed.model_dump()
        except pydantic.ValidationError:
            print("extracting business scope failed")
    else:
        print("no business scope")

    if d_result:
        try:
            parsed: TWDirectors = TWDirectors.model_validate_json(d_result)
            director_dict = parsed.model_dump()
        except pydantic.ValidationError:
            print("extracting directors failed")

    else:
        print("no business scope")

    #Merge extracted data into single JSON and write to file
    merged_dict = {**profile_dict, **scope_dict, **director_dict}
    json_string = json.dumps(merged_dict, indent=4)

    with open(f"/home/daniel/projects/outputs/json/tw/'{company_num}.json'", 'w', encoding="utf-8") as file:
        file.write(json_string)

    print(durations)
    print(tokens)

    await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
