# How we chose a model

*The test was conducted on March 28th 2024 by [Laura Bejder Jensen](https://github.com/laurabejder)*

The core of Commons is the data we extract from millions of comments of federal regulations. Its accuracy is critical to the utility of the tool and rests largely on the LLM used to extract it. 

We tested six different models: `Claude-3-haiku`, `Claude-3-Sonnet` and `Claude-3-opus` from Anthropic; `GPT-3.5-turbo` and `GPT-4` from OpenAI; and `Gemini-1.0-pro` from Google. 

The models vary in token price, performance time, rhetorical style and accuracy.
Choosing the right one came down to a combination of the effectiveness and price of each model.

![Alt text](images/table1.png?raw=true)

To be realistic, with the sheer volume of comments we are dealing with, we can only afford `Claude-3-haiku`, `GPT-3.5-turbo` and `Gemini-1.0-pro` but we included the other models in our testing for comparison.

### How we tested the models
To test the accuracy of the models’ outputs we created a random sample of 200 comments from our database. 
We then ran the comments through all six models using the same prompt and guardrails output validation model. All models were asked to return a valid json. 

We manually divided all values in each json response into the four categories: true positive, true negative, false positive and false negative. Based on the manual categorization we calculated the error rates: how often do the models make up or miss information. 

The full output file and the response categorizations can be found in the `model_outputs.csv`.

So how did the models perform?

## The results
Not surprisingly, there is a correlation between price and accuracy: The more expensive models perform better. 

But we also saw a difference between the cheapest models with `GPT-3.5-turbo` returning notably more errors than `Claude-3-haiku` and `Gemini-1.0-pro`. Many of those errors were the model failing to provide summaries of the comments. 

[bar chart]

But not all errors are created equal!

We use the terms accuracy (above showed error rate), precision and recall to measure the performance of the model. 

Precision is the model’s ability to only identify only the relevant data points ($true positives / true positives + false positives$). In our case, we want to know how many of the extracted values are true. 

Recall is  the model’s ability to find all the relevant cases within our data set ($true positives / true positives + false negatives$). Here it is the balance between correctly extracted data and information the model missed.  

### False positives
False positives occur when the models either start hallucinating, making up information that is not in the comment text or return the examples we gave them (and we clearly told them not to return!). 
More than anything else, these are the errors we want to avoid.

![Alt text](images/false_positives.png?raw=true)

### False negatives
False negatives occur when the model misses information that is provided in the comment. It could either represent a failure to extract information requested in the prompt or to summarize the comment.

![Alt text](images/false_negatives.png?raw=true)