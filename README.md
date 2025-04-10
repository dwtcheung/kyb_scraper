# KYB Scraper
**This is a set of demo web scraping agent based on Browser-Use.**

## Key Project Notes
* Tested against Browser-Use version d4073d0f
* Codes are using Ollama local LLM, modify the "Agent" to use cloud LLM
* Business entity names are hard coded for the purpose of the demo
* If the registry search returns multiple businesses, this demo will not work

## Requirements
You will need an API key from one of the following Models:
* OpenAI
* Anthropic
* Azure OpenAI
* Gemini
* DeepSeek-V3
* DeepSeek-R1

Or you will need to install Ollama and pull one of the Models:
* Qwen2.5:14b + Qwen2.5:7b
* Phi4
* Llama3.1

### Note about local LLM with Ollama
* The code is tested with a Nvidia GTX 1080Ti with 11GB of memory.
* Models with parameter size smaller than 12b do not function well
* Suggest you read "Optimizing Ollama VRAM Settings" blog first and use the interactive calculator to determine context size
* https://blog.peddals.com/en/ollama-vram-fine-tune-with-kv-cache/

## Install Instruction
1. Check out Browser-Use as a local development project, ie. use GIT clone
2. Inside the Browser-Use project folder, check out this project as a submodule

## TODO
1. Add ability to handle multiple business names from search result
