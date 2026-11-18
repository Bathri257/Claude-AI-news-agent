"""Global AI news sources (RSS / Atom). Add or remove feeds freely."""

FEEDS = [
    # Major tech press (US / global)
    ("TechCrunch", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("VentureBeat", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Technology Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Ars Technica", "https://arstechnica.com/ai/feed/"),
    ("Wired", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("ZDNET", "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
    ("The Register", "https://www.theregister.com/software/ai_ml/headlines.atom"),
    # Global / regional coverage
    ("BBC Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Rest of World", "https://restofworld.org/feed/latest/"),
    ("The Decoder (EU)", "https://the-decoder.com/feed/"),
    ("Sifted (EU)", "https://sifted.eu/feed"),
    ("SCMP Tech (Asia)", "https://www.scmp.com/rss/320663/feed"),
    ("Analytics India Magazine", "https://analyticsindiamag.com/feed/"),
    ("AI News", "https://www.artificialintelligence-news.com/feed/"),
    ("Google News: AI", "https://news.google.com/rss/search?q=%22artificial+intelligence%22+OR+%22generative+AI%22+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Labs and companies (first-hand announcements)
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("NVIDIA", "https://blogs.nvidia.com/feed/"),
    ("AWS Machine Learning", "https://aws.amazon.com/blogs/machine-learning/feed/"),
    ("MIT News: AI", "https://news.mit.edu/rss/topic/artificial-intelligence2"),
    # Research-focused
    ("MarkTechPost", "https://www.marktechpost.com/feed/"),
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
]
