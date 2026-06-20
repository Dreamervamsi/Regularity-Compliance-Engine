import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# Normalise query
def normalise_query(query:str):
    lower_query = query.lower()
    remove_nums = re.sub('\d+'," ",lower_query)
    no_punc_string = re.sub(r'[^\w\s]','', remove_nums)

    no_w_space = no_punc_string.strip()
    
    string_lst = [no_w_space][0].split()

    stop_words = set(stopwords.words('english'))

    normalised_query=''
    for i in string_lst:
        if i not in stop_words:
            normalised_query+=i + ' '

    return normalised_query