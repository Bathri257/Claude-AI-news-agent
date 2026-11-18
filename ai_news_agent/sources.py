"""News sources. Every source here is free and needs NO API key.

kinds:
  rss    - any RSS/Atom feed
  gdelt  - GDELT DOC 2.0 API (free, global, ~65 languages, direct article links)
  hn     - Hacker News via the Algolia search API (good for small AI firms / launches)

`ai_only=False` means the source covers general news, so items are kept only if they
mention AI. Query-based sources (Google News search, GDELT, HN) are already AI-focused.
"""
from urllib.parse import quote_plus


def google_news(query: str, region: str = "US", lang: str = "en") -> str:
    q = quote_plus(f"{query} when:1d")
    return f"https://news.google.com/rss/search?q={q}&hl={lang}-{region}&gl={region}&ceid={region}:{lang}"


SOURCES = [
    # ---------- Global tech press ----------
    {"name": "TechCrunch", "kind": "rss", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge", "kind": "rss", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "VentureBeat", "kind": "rss", "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "MIT Technology Review", "kind": "rss", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
    {"name": "Ars Technica", "kind": "rss", "url": "https://arstechnica.com/ai/feed/"},
    {"name": "Wired", "kind": "rss", "url": "https://www.wired.com/feed/tag/ai/latest/rss"},
    {"name": "ZDNET", "kind": "rss", "url": "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"},
    {"name": "The Register", "kind": "rss", "url": "https://www.theregister.com/software/ai_ml/headlines.atom"},
    {"name": "BBC Technology", "kind": "rss", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "ai_only": False},
    {"name": "Rest of World", "kind": "rss", "url": "https://restofworld.org/feed/latest/", "ai_only": False},
    {"name": "The Decoder", "kind": "rss", "url": "https://the-decoder.com/feed/"},
    {"name": "Sifted (Europe)", "kind": "rss", "url": "https://sifted.eu/feed", "ai_only": False},
    {"name": "SCMP Tech (Asia)", "kind": "rss", "url": "https://www.scmp.com/rss/320663/feed", "ai_only": False},
    {"name": "AI News", "kind": "rss", "url": "https://www.artificialintelligence-news.com/feed/"},
    {"name": "MarkTechPost", "kind": "rss", "url": "https://www.marktechpost.com/feed/"},

    # ---------- AI labs & companies (first-hand announcements) ----------
    {"name": "OpenAI", "kind": "rss", "url": "https://openai.com/news/rss.xml"},
    {"name": "Google DeepMind", "kind": "rss", "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Google AI Blog", "kind": "rss", "url": "https://blog.google/technology/ai/rss/"},
    {"name": "Hugging Face", "kind": "rss", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "NVIDIA", "kind": "rss", "url": "https://blogs.nvidia.com/feed/"},
    {"name": "AWS Machine Learning", "kind": "rss", "url": "https://aws.amazon.com/blogs/machine-learning/feed/"},
    {"name": "MIT News: AI", "kind": "rss", "url": "https://news.mit.edu/rss/topic/artificial-intelligence2"},

    # ---------- Global search-based (catches labs without RSS, e.g. Anthropic, and small startups) ----------
    {"name": "Google News: AI labs", "kind": "rss", "url": google_news(
        '(Anthropic OR OpenAI OR "Google DeepMind" OR "Meta AI" OR Mistral OR DeepSeek OR xAI OR Qwen)')},
    {"name": "Google News: AI startups", "kind": "rss", "url": google_news(
        '("AI startup" OR "generative AI") (raises OR launches OR funding OR acquires)')},
    {"name": "Hacker News", "kind": "hn", "url": "AI OR LLM OR GPT OR Claude OR Gemini"},
    {"name": "GDELT: global AI", "kind": "gdelt", "url":
        '("artificial intelligence" OR "generative AI" OR "large language model") sourcelang:english'},

    # ---------- India ----------
    {"name": "Economic Times Tech", "kind": "rss", "url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms", "ai_only": False},
    {"name": "The Hindu: Technology", "kind": "rss", "url": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss", "ai_only": False},
    {"name": "BusinessLine Info-tech", "kind": "rss", "url": "https://www.thehindubusinessline.com/info-tech/feeder/default.rss", "ai_only": False},
    {"name": "Indian Express Tech", "kind": "rss", "url": "https://indianexpress.com/section/technology/feed/", "ai_only": False},
    {"name": "Inc42", "kind": "rss", "url": "https://inc42.com/feed/", "ai_only": False},
    {"name": "YourStory", "kind": "rss", "url": "https://yourstory.com/feed", "ai_only": False},
    {"name": "Entrackr", "kind": "rss", "url": "https://entrackr.com/feed/", "ai_only": False},
    {"name": "MediaNama", "kind": "rss", "url": "https://www.medianama.com/feed/", "ai_only": False},
    {"name": "Analytics India Magazine", "kind": "rss", "url": "https://analyticsindiamag.com/feed/"},
    {"name": "Google News: AI India", "kind": "rss", "url": google_news(
        '("artificial intelligence" OR "generative AI" OR "AI startup") India', region="IN")},
    {"name": "Google News: Indian AI firms", "kind": "rss", "url": google_news(
        '("Sarvam AI" OR Krutrim OR "IndiaAI" OR BharatGPT OR CoRover OR "Gnani.ai" OR "Fractal Analytics" OR "Zoho AI")',
        region="IN")},
    {"name": "GDELT: India AI", "kind": "gdelt", "url":
        '("artificial intelligence" OR "generative AI" OR "AI startup") sourcecountry:india'},

    # ---------- Tamil Nadu ----------
    {"name": "The Hindu: Tamil Nadu", "kind": "rss", "url": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss", "ai_only": False},
    {"name": "Times of India: Chennai", "kind": "rss", "url": "https://timesofindia.indiatimes.com/rssfeeds/2950623.cms", "ai_only": False},
    {"name": "Google News: AI Tamil Nadu", "kind": "rss", "url": google_news(
        '("artificial intelligence" OR "AI") ("Tamil Nadu" OR Chennai OR Coimbatore OR Madurai OR "IIT Madras" OR Hosur)',
        region="IN")},
    {"name": "Google News: TN AI jobs & policy", "kind": "rss", "url": google_news(
        '("Tamil Nadu" OR Chennai) (AI OR "data centre" OR GCC OR semiconductor) (jobs OR policy OR investment OR startup OR hiring)',
        region="IN")},
    {"name": "Google News: AI (Tamil)", "kind": "rss", "url": google_news("செயற்கை நுண்ணறிவு", region="IN", lang="ta")},
    {"name": "GDELT: Tamil Nadu AI", "kind": "gdelt", "url":
        '("artificial intelligence" OR "AI startup" OR "machine learning" OR "data centre") '
        '("Tamil Nadu" OR Chennai OR Coimbatore OR Madurai OR "IIT Madras")'},
]

# Technology categories the digest is organised by.
CATEGORIES = [
    "Models & LLMs",
    "AI Agents",
    "Generative Media",
    "Research",
    "Chips & Infrastructure",
    "Robotics",
    "Open Source",
    "Industry & Products",
    "Business & Funding",
    "Policy & Regulation",
    "Safety & Ethics",
    "Jobs & Skills",
]

# Used for tagging when Claude isn't available, and as hints in the prompts.
COMPANIES = [
    "OpenAI", "Anthropic", "Google", "DeepMind", "Meta", "Microsoft", "NVIDIA", "Apple", "Amazon",
    "AWS", "xAI", "Mistral", "DeepSeek", "Alibaba", "Qwen", "Baidu", "Tencent", "ByteDance",
    "Samsung", "IBM", "Intel", "AMD", "TSMC", "Hugging Face", "Perplexity", "Cohere", "Stability AI",
    "Midjourney", "Runway", "Databricks", "Scale AI", "Salesforce", "Oracle",
    "Sarvam AI", "Krutrim", "Ola", "CoRover", "Gnani.ai", "Fractal", "Zoho", "Freshworks", "Infosys",
    "TCS", "Wipro", "HCLTech", "Tech Mahindra", "Reliance", "Jio", "IIT Madras", "IndiaAI",
]
