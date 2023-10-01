import pandas as pd

def create_prompt_info(docs: list):
    """
    Create prompt for OpenAI GPT-3
    """
    df = pd.DataFrame(docs)
    df['pctPositive'] = df['pctPositive'].astype(str) + '%'
    df['pctNegative'] = df['pctNegative'].astype(str) + '%'
    df['pctNeutral'] = df['pctNeutral'].astype(str) + '%'
    df = df[[
    'topic',
    'postCount',
    'mainZone',
    'discussionLevel',
    'mostPopularPositiveNarrative',
    'mostPopularNegativeNarrative',	
    'mostPopularNeutralNarrative',
    'mostPopularSentiment',
    'totalPositiveCount',
    'totalNegativeCount',
    'totalNeutralCount',
    'pctPositive',
    'pctNegative',
    'pctNeutral',
    'publishFrom',
    'publishTo'
    ]].to_dict('records')


    prompt = f'''I am a media analyst, writing social media write-ups on what happened for the week, help me combine all the {len(df)} topics' and summarised the narratives in paragraphs.

For each topic, summarised in a single paragraph (100 words limit),  it should answer the following questions and provide insights based on it:
- Assess the level of discussion on the given topic based on the number of post counts?
- Which zone is the topic most prominently discussed on?
- Which online sentiments were the largest, stating sentiment percentage accordingly?
- Which type of narrative is most discussed and the content?
- When comparing between the narratives, what can we learn from it?

Context of {len(df)} topics:
{df}


    '''

    return prompt

def create_prompt_summarised(prev_results: str):
    """
    Create prompt for OpenAI GPT-3.5
    """

    prompt = f'''Summarised in a paragraph, combining all the information across topics.

Topics: {prev_results}
'''
    return prompt


def create_prompt_final(prev_results: str):
    """
    Create prompt for OpenAI GPT-3.5
    """

    prompt = f'''I am a media analyst, writing social media write-ups powerpoint slide, on what happened for the week, help me combine all the topics' and further summarised the information into a single paragraph.

Topics: {prev_results}
'''
    return prompt


def create_prompt_final2(prev_results: str):
    """
    Create prompt for OpenAI GPT-3.5
    """

    prompt = f'''Summarised this information into 1 paragraph of findings/insights for powerpoint slide.

Topics: {prev_results}
'''

    return prompt