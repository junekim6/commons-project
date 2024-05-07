# Analyse public comments on regulations.gov

This directory contains the code for the main analysis of comments posted on regulations.gov and a handful of template notebooks to get you started if you want to do your own analysis.

It also includes the subdirectory `how_we_chose_a_model` where we explain the model testing process that we went through to choose the best model for our purpose and data.

## 1. Project Description

When we pull data from the regulations.gov, we get a lot of text data – the comments. Often these comments are long and contain a lot of information but they are unstructured and difficult to analyze. 

In the Commons project, we use a language model to analyze the text data and return structured data including details on the commenter and short summaries of the comments.

[explanatory chart]

## 2. Content of the directory
The directory contains the following folders:
- `analysis_scripts`: A set of scripts to analyze the data collected from regulations.gov.
- `how_we_chose_a_model`: A detailed explanation of the model testing process that we went through to choose the best model for our analysis. 
- `template_notebooks`: A set of notebooks to analyze the public comment from regulations.gov using llms and returning structured data.

## 3. Installation and setup

In this repo, we provide analysis code that uses the LLMs from OpenAI, Anthropic and Google. Install all the different LLMs:

```bash
pip install openai anthropic google-generativeai
```
You also need to sign up for API keys from all three companies and add them to your `.env` file:

```bash
OPENAI_API_KEY = "xxxxxxxxxxxx"
ANTHROPIC_API_KEY = "xxxxxxxxxxxx"
GEMINI_API_KEY = "xxxxxxxxxxxx"
```

### Guardrails

LLMs are not great at returning structured data so we use the [Guardrails](https://github.com/guardrails-ai/guardrails) framework to validate the output of the models. 

```bash
pip install guardrails-ai
```

### Running local models

Download [LM Studio](https://lmstudio.ai/) and download the model you would like to run. And then you need to install litellm. This package allows you to connect the local model to the guardrail data validation system we have created.

```bash
pip install litellm
```