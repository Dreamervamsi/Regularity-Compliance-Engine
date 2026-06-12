from rag_pipeline.dual_search.dense_search.src.index import get_client,get_collection
import ahocorasick
import re
import config

class IntentCheck:
    def __init__(self):
        self.injection_patterns = {
            "profanity_words":[
                "how to build a bomb", "how to make a weapon", 
                "how to commit suicide", "how to hack into",
                "how to hack the system", "how to theft"
            ],
            "prompt_injection":[
                "ignore previous instructions", "ignore above", "ignore the rules",
                "system prompt", "you must now act as", "bypass restriction", 
                "developer mode", "unfiltered ai", "do anything now"
            ]
        }
        self.db_injection_patterns = [
            re.compile(r"(?i)\b(DROP|DELETE|UNION|INSERT)\b"),
            re.compile(r"(?i)\bor\s+\d+=\d+\b"),  # Matches OR 1=1
            re.compile(r"<script.*?>.*?</script>", re.IGNORECASE)  # Matches XSS
        ]
        
        # instead of checking the pattern for each word every time(which increases
        # CPU power) this alogorithm uses efficient methods for matching the word Or string

        self.aho = ahocorasick.Automaton() # initialising ahocorasick algorithm

        for category,terms in self.injection_patterns.items():
            for word in terms:
                word=word.lower()
                if word not in self.aho:
                    self.aho.add_word(word,(word,category))

        self.aho.make_automaton()
    
    def check_query_in_keyword_blocklist(self,normalised_query:str):
        
        for pattern in self.db_injection_patterns:
            if pattern.search(normalised_query):
                return {
                    'detected':True,
                    'message': 'Data base injection found',
                    'word':None,
                    'category':'Data base injection'
                }

        for end_index, (term, category) in self.aho.iter(normalised_query):
            return {
                'detected':True,
                'message':'🛑 Security Alert! Query blocked.',
                'word':term,
                'category':category
            }

        return {
                'detected':False,
                'message':"No issue found",
                'word':None,
                'category':None
            }

    def safety_vector_scan(self,normalised_query:str):
        client = get_client()

        safety_collection = get_collection(full_reingest=False,collection_name=config.SAFETY_BLOCKLIST_COLLECTION)

        