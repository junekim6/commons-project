# How we chose a model

The core of Commons is the data we extract from millions of comments of federal regulations. Its accuracy is critical to the utility of the tool and rests largely on the LLM used to extract it. 

We tested six different models: `Claude-3-haiku`, `Claude-3-Sonnet` and `Claude-3-opus` from Anthropic; `GPT-3.5-turbo` and `GPT-4` from OpenAI; and `Gemini-1.0-pro` from Google. 

The models vary in token price, performance time, rhetorical style and accuracy.
Choosing the right one came down to a combination of the effectiveness and price of each model.

![Alt text](images/table1.png?raw=true)

### How we tested the models
To test the accuracy of the models’ outputs we created a random sample of 200 comments from our database. 
We then ran the comments through all six models using the same prompt and guardrails output validation model. All models were asked to return a valid json. 

We manually divided all values in each json response into the four categories: true positive, true negative, false positive and false negative. Based on the manual categorization we calculated the error rates: how often do the models make up or miss information. 

The full output file and the response categorizations can be found in the `model_outputs.csv`.

So how did the models do?

## The results

### False positives
False positives occur when the models either start hallucinating, making up information that is not in the comment text or return the examples we gave them (and we clearly told them not to return!). 
More than anything else, these are the errors we want to avoid.

### False negatives
False negatives occur when the model misses information that is provided in the comment. It could either represent a failure to extract information requested in the prompt or to summarize the comment.