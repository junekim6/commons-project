# How we chose a model

*The test was conducted on March 28th 2024 by [Laura Bejder Jensen](https://github.com/laurabejder)*

The core of Commons is the data we extract from millions of comments on federal regulations. Its accuracy is critical to the utility of the tool and rests largely on the LLM used to extract it. 

We tested six different models: `Claude-3-haiku`, `Claude-3-Sonnet` and `Claude-3-opus` from Anthropic; `GPT-3.5-turbo` and `GPT-4` from OpenAI; and `Gemini-1.0-pro` from Google. 

The models vary in token price, performance time, rhetorical style and accuracy. Choosing the right one came down to a combination of the effectiveness and price of each model.

![Alt text](images/table1.png?raw=true)

<sup>**Source**: [OpenAI Documentation](https://openai.com/pricing), [Anthropic Documentation](https://docs.anthropic.com/claude/docs/models-overview), [Google Gemini Documentation](https://ai.google.dev/pricing) (as of March 28th, 2024).The specific models used are: claude-3-haiku-20240307, claude-3-opus-20240229, claude-3-sonnet-20240229, gemini-1.0-pro, gpt-3.5-turbo-1106, gpt-4-1106-preview</sup>

To be realistic, with the sheer volume of comments we are dealing with, we can only afford `Claude-3-haiku`, `GPT-3.5-turbo` and `Gemini-1.0-pro` but we included the other models in our testing for comparison.

*We ended up choosing `Gemini-1.0-pro` as our model of choice. It is the most accurate model in our test and has a reasonable price.*

### How we tested the models
To test the accuracy of the models’ outputs we created a random sample of 200 comments from our database. 
We then ran the comments through all six models using the same prompt and guardrails output validation model. All models were asked to return a valid json. 

We manually divided all values in each json response into the four categories: true positive, true negative, false positive and false negative. Based on the manual categorization we calculated the error rates: how often do the models make up or miss information. 

The full output file and the response categorizations can be found in the `model_outputs.csv`.

So how did the models perform?

## The results
Not surprisingly, there is a correlation between price and accuracy: The more expensive models perform better. 

But we also saw a difference between the cheapest models with `GPT-3.5-turbo` returning notably more errors than `Claude-3-haiku` and `Gemini-1.0-pro`. Many of those errors were the model failing to provide summaries of the comments. 

![Alt text](images/bar_chart.png?raw=true)

#### Accuracy, precision and recall
We use a combination of the models’ accuracy, precision, and recall as a metrics for their overall performance.

- Accuracy is the overall balance between correct and incorrect responses ($true positives + true negatives / all responses$). Here we also use the error rate to show the same (or technically, the reverse…)
- Precision is the model’s ability to only identify only the relevant data points ($true positives / true positives + false positives$). In our case, we want to know how many of the extracted values are true. 
- Recall is  the model’s ability to find all the relevant cases within our data set ($true positives / true positives + false negatives$). Here it is the balance between correctly extracted data and information the model missed.

![Alt text](images/table2.png?raw=true)

GPT-3.5-turbo had the lowest precision and recall. Combined with the highest error rate, it is the worst performing model in the test.

We also found that `Gemini-1.0-pro` has the highest precision (very few false positives) but its recall is a bit lower than `Claude-3-haiku`'s. Gemini seems more conservative than Haiku and as a result misses more information. 

### False positives
False positives occur when the models either start hallucinating, making up information that is not in the comment text or return the examples we gave them (and we clearly told them not to return!). 

More than anything else, these are the errors we want to avoid.

![Alt text](images/false_positives.png?raw=true)

Digging a little deeper, we were wondering if the errors could have something to do with the quality of the underlying data? 

To answer that question we categorized all comments into a boolean variable `substantial_text`. Rows that contained an actual comment were categorized as `True` while rows where the `full_text` column was either empty or something like “See attached” were categorized as `False`. 

Not surprisingly, it turns out that a lot of the false positive errors could have been prevented if we had only analyzed substantial comments. It appears that many of the instances where the models made up false names, addresses, organizations etc. were when they had little to no text to extract the information we asked for. 

![Alt text](images/stacked_bar.png?raw=true)

However, that leaves us with a handful of unexplained errors – especially from Claude-3-haiku. 

It had a tendency to assume that the commenter is from the United States regardless of whether they provided information about their location. In most cases, these assumptions are correct but as we want to err on the side of caution, we want the model to only return information that is clearly stated in the comment (we did accept `United States` as a correct response if the commenter stated their town/city and state). 

Claude-3-haiku also had issues extracting names. It would pull out random words from sentences as first names (e.g. Ameriprise, As, I) or last names (e.g. Ficial, a member, strongly) if there was no clear name stated. The other models did not have this issue.

### False negatives
False negatives occur when the model misses information that is provided in the comment. It could either represent a failure to extract information requested in the prompt or to summarize the comment.

![Alt text](images/false_negatives.png?raw=true)