from newsapi import NewsApiClient

# IMPORTANT: Replace with your own News API key
NEWS_API_KEY = 'YOUR_API_KEY'

def run(intent, target):
    if intent == "get_news":
        if NEWS_API_KEY == 'YOUR_API_KEY':
            return "Please set your News API key in the news.py skill file."
        
        try:
            newsapi = NewsApiClient(api_key=NEWS_API_KEY)
            top_headlines = newsapi.get_top_headlines(language='en', country='us')
            
            if top_headlines['status'] == 'ok' and top_headlines['articles']:
                articles = top_headlines['articles'][:5] # Read top 5
                headlines = "Here are the top headlines: "
                for article in articles:
                    headlines += article['title'] + ". "
                return headlines
            else:
                return "I couldn't fetch the news at the moment."

        except Exception as e:
            return f"I encountered an error trying to fetch the news: {e}"
            
    return None
