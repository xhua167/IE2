######################################### build search function ###############################################
import re
import nltk
from nltk.stem import SnowballStemmer
from flaskweb import db
from flaskweb.getData import meanRating

sb = SnowballStemmer("english")

# create an array for replace some contractions
replace_patterns = [
    ('(A|a)in\'t', 'is not'),
    ('(C|c)an\'t', 'can not'),
    ('(H|h)ow\'s', 'how is'),
    ('(H|h)ow\'d', 'how did'),
    ('(H|h)ow\'d\'y', 'how do you'),
    ('(H|h)ere\'s', 'here is'),
    ('(I|i)t\'s', 'it is'),
    ('(I|i)\'m', 'i am'),
    ('(L|l)et\'s', 'let us'),
    ('(M|m)a\'am', 'madam'),
    ('(S|s)han\'t', 'shall not'),
    ('(S|s)ha\'n\'t', 'shall not'),
    ('(S|s)o\'s', 'so as'),
    ('(T|t)his\'s', 'this is'),
    ('(T|t)here\'s', 'there is'),
    ('(W|w)on\'t', 'will not'),
    ('(W|w)hat\'s', 'what is'),
    ('(W|w)hatis', 'what is'),
    ('(W|w)hen\'s', 'when is'),
    ('(W|w)here\'d', 'where did'),
    ('(W|w)here\'s', 'where is'),
    ('(W|w)ho\'s', 'who is'),
    ('(W|w)hy\'s', 'why is'),
    ('(Y|y)\'all', 'you all'),
    ('(\w+)\'ve', '\g<1> have'),
    ('(\w+)\'ll', '\g<1> will'),
    ('(\w+)n\'t', '\g<1> not'),
    ('(\w+)\'re', '\g<1> are'),
    ('(\w+)\'d', '\g<1> would')]


# function for clean contractions
def clean_contraction(x):
    x = str(x)
    for pattern, repl in replace_patterns:
        if re.search(pattern, x):
            x = re.sub(pattern, repl, x)
    return x


# unify the expression of time
check_pm = re.compile(r'[0-9]+p[.]?m[.]?')
check_PM = re.compile(r'[0-9]+P[.]?M[.]?')
check_am = re.compile(r'[0-9]+a[.]?m[.]?')
check_AM = re.compile(r'[0-9]+A[.]?M$[.]?')


# write the function
def fix_time(x):
    x = str(x)
    if re.search(check_pm, x):
        x = re.sub('p.m', ' PM', x)
    if re.search(check_PM, x):
        x = re.sub('P.M', ' PM', x)
    if re.search(check_am, x):
        x = re.sub('a.m', ' AM', x)
    if re.search(check_AM, x):
        x = re.sub('A.M', ' AM', x)
    return x


# fix duplication of letters
goood = re.compile(r'g+(o)\1{2,}(d)+')  # replace gooodddd by good
check_duplicate = re.compile(r'\w*(\S)\1{2,}\w*')  # replace words such as fantasticccccc by fantastic


# fix duplications and clean some puncs
def clean_punc(x):
    x = str(x)
    if re.search(goood, x):  # we can treat goood and goooood in the same way
        x = re.sub(goood, 'good', x)
    if re.findall(check_duplicate, x):  # we replace other duplicate characters
        x = re.sub(r'(\D)\1{2,}', r'\1', x)
    if re.search('(\[.*math).+(math\])', x):  # dealing with math functions(borrowed from kaggle)
        x = re.sub('(\[.*math).+(math\])', '[latex formula]', x)
    if "'s " in x:
        x = x.replace("'s ", " ")
    if "'" in x:
        x = x.replace("'", '')
    if "_" in x:
        x = x.replace("_", ' and ')
    for each in ",.!?()/":
        x = x.replace(each, '')
    return x


# we fix common wrong spellings in our specific document context
mispell_dict = {'colour': 'color',
                'centre': 'center',
                'didnt': 'did not',
                'Didnt': 'Did not',
                'Doesnt': 'Does not',
                'Couldnt': 'Could not',
                'doesnt': 'does not',
                'isnt': 'is not',
                'shouldnt': 'should not',
                'flavour': 'flavor',
                'flavours': 'flavors',
                'wasnt': 'was not',
                'cancelled': 'canceled',
                'neighbourhood': 'neighborhood',
                'neighbour': 'neighbor',
                'theatre': 'theater',
                'grey': 'gray',
                'favourites': 'favorites',
                'favourite': 'favorite',
                'flavoured': 'flavored',
                'acknowledgement': 'acknowledgment',
                'judgement': 'judgment',
                'speciality': 'specialty',
                'favour': 'favor',
                'colours': 'colors',
                'coloured': 'colored',
                'theatres': 'theaters',
                'behaviour': 'behavior',
                'travelling': 'traveling',
                'colouring': 'coloring',
                'labelled': 'labeled',
                'cancelling': 'canceling',
                'waitedand': 'waited and',
                'whisky': 'Whisky',
                'tastey': 'tasty',
                'goodbut': 'good but',
                'sushis': 'sushi',
                'disapoointed': 'disappointed',
                'disapointed': 'disappointed',
                'disapointment': 'disappointment',
                'Amzing': 'Amazing',
                'bAd': 'bad',
                'fantastics': 'fatastic',
                'flavuorful': 'flavorful',
                'infomation': 'information',
                'informaiton': 'information',
                'eveeyone': 'everyone',
                'Hsppy': 'Happy',
                'waygu': 'wagyu',
                'unflavorful': 'untasty',
                'Flavortown': 'Flavor Town',
                'wi-fi': 'wifi',
                'ayce': 'all you can eat',
                'appriceiate': 'appriciate',
                'worest': 'worst'}


def correct_spelling(x):
    x = str(x)
    for word in mispell_dict.keys():
        if word in x:
            x = x.replace(word, mispell_dict[word])
    return x


# seperate words, numbers and some unremoved punctuations such as ,.?!
def seperate_word(x):
    for pattern, repl in [('[\W]', lambda p: ' ' + p.group() + ' '), ('[0-9]{1,}', lambda p: ' ' + p.group() + ' ')]:
        if re.search(pattern, x):
            x = re.sub(pattern, repl, x)
    return x


# tokenize text
def tokenizeRawData(text):
    sb = SnowballStemmer("english")
    text = clean_contraction(text)
    text = clean_punc(text)
    text = fix_time(text)
    text = correct_spelling(text)
    text = seperate_word(text)
    text = text.lower()
    output = text.split()
    for i in range(len(output)):
        token = output[i]
        output[i] = sb.stem(token)
    return output

def Search(astring):
    tokenizedDoc = db.tokenizedDoc
    services = db.Services
    astring = str(astring)
    cursor = tokenizedDoc.find()
    data = cursor[0]
    token_string = tokenizeRawData(astring)
    outcome = []
    for ID, content in data.items():
        if ID != '_id':
            cnt = 0
            for eachWord in set(token_string):
                if eachWord in content:
                    cnt += 1
            if len(token_string) != 0:
                if cnt / len(token_string) >= 0.50:
                    outcome.append(ID)
    if len(outcome) == 0:
        return outcome
    else:
        cursor = services.find()
        search_result = []
        for document in cursor:
            MatchedKey = str(document['_id'])
            if MatchedKey in outcome:
                search_result.append(document)
        search_result = meanRating(search_result)
        return search_result


# ######################################### build search function ###############################################
# import re
# import nltk
# from nltk.tokenize import RegexpTokenizer
# from nltk.stem import SnowballStemmer
# from flaskweb import db
# from flaskweb.getData import meanRating
#
# # create an array for replace some contractions
# replace_patterns = [
#     ('(A|a)in\'t', 'is not'),
#     ('(C|c)an\'t', 'can not'),
#     ('(H|h)ow\'s', 'how is'),
#     ('(H|h)ow\'d', 'how did'),
#     ('(H|h)ow\'d\'y', 'how do you'),
#     ('(H|h)ere\'s', 'here is'),
#     ('(I|i)t\'s', 'it is'),
#     ('(I|i)\'m', 'i am'),
#     ('(L|l)et\'s', 'let us'),
#     ('(M|m)a\'am', 'madam'),
#     ('(S|s)han\'t', 'shall not'),
#     ('(S|s)ha\'n\'t', 'shall not'),
#     ('(S|s)o\'s', 'so as'),
#     ('(T|t)his\'s', 'this is'),
#     ('(T|t)here\'s', 'there is'),
#     ('(W|w)on\'t', 'will not'),
#     ('(W|w)hat\'s', 'what is'),
#     ('(W|w)hatis', 'what is'),
#     ('(W|w)hen\'s', 'when is'),
#     ('(W|w)here\'d', 'where did'),
#     ('(W|w)here\'s', 'where is'),
#     ('(W|w)ho\'s', 'who is'),
#     ('(W|w)hy\'s', 'why is'),
#     ('(Y|y)\'all', 'you all'),
#     ('(\w+)\'ve', '\g<1> have'),
#     ('(\w+)\'ll', '\g<1> will'),
#     ('(\w+)n\'t', '\g<1> not'),
#     ('(\w+)\'re', '\g<1> are'),
#     ('(\w+)\'d', '\g<1> would')]
#
# # function for clean contractions
# def clean_contraction(x):
#     x = str(x)
#     for pattern, repl in replace_patterns:
#         if re.search(pattern,x):
#             x = re.sub(pattern, repl, x)
#     return x
#
# # unify the expression of time
# check_pm = re.compile(r'[0-9]+p[.]?m[.]?')
# check_PM = re.compile(r'[0-9]+P[.]?M[.]?')
# check_am = re.compile(r'[0-9]+a[.]?m[.]?')
# check_AM = re.compile(r'[0-9]+A[.]?M$[.]?')
#
# # write the function
# def fix_time(x):
#     x = str(x)
#     if re.search(check_pm, x):
#         x = re.sub('p.m', ' PM', x)
#     if re.search(check_PM, x):
#         x = re.sub('P.M', ' PM', x)
#     if re.search(check_am, x):
#         x = re.sub('a.m', ' AM', x)
#     if re.search(check_AM, x):
#         x = re.sub('A.M', ' AM', x)
#     return x
#
# # fix duplication of letters
# goood = re.compile(r'g+(o)\1{2,}(d)+') # replace gooodddd by good
# check_duplicate = re.compile(r'\w*(\S)\1{2,}\w*') # replace words such as fantasticccccc by fantastic
# # fix duplications and clean some puncs
# def clean_punc(x):
#     x = str(x)
#     if re.search(goood,x): # we can treat goood and goooood in the same way
#         x = re.sub(goood, 'good', x)
#     if re.findall(check_duplicate,x): # we replace other duplicate characters
#         x = re.sub(r'(\D)\1{2,}', r'\1', x)
#     if re.search('(\[.*math).+(math\])',x): # dealing with math functions(borrowed from kaggle)
#         x = re.sub('(\[.*math).+(math\])', '[latex formula]', x)
#     if "'s " in x:
#         x = x.replace("'s "," ")
#     if "'" in x:
#         x = x.replace("'", '')
#     if "_" in x:
#         x = x.replace("_", ' and ')
#     for each in ",.!?()/":
#         x = x.replace(each, '')
#     return x
#
# # we fix common wrong spellings in our specific document context
# mispell_dict = {'colour':'color',
#                 'centre':'center',
#                 'didnt':'did not',
#                 'Didnt':'Did not',
#                 'Doesnt':'Does not',
#                 'Couldnt':'Could not',
#                 'doesnt':'does not',
#                 'isnt':'is not',
#                 'shouldnt':'should not',
#                 'flavour':'flavor',
#                 'flavours':'flavors',
#                 'wasnt':'was not',
#                 'cancelled':'canceled',
#                 'neighbourhood':'neighborhood',
#                 'neighbour':'neighbor',
#                 'theatre':'theater',
#                 'grey':'gray',
#                 'favourites':'favorites',
#                 'favourite':'favorite',
#                 'flavoured':'flavored',
#                 'acknowledgement':'acknowledgment',
#                 'judgement':'judgment',
#                 'speciality':'specialty',
#                 'favour':'favor',
#                 'colours':'colors',
#                 'coloured':'colored',
#                 'theatres':'theaters',
#                 'behaviour':'behavior',
#                 'travelling':'traveling',
#                 'colouring':'coloring',
#                 'labelled':'labeled',
#                 'cancelling':'canceling',
#                 'waitedand': 'waited and',
#                 'whisky':'Whisky',
#                 'tastey':'tasty',
#                 'goodbut': 'good but',
#                 'sushis':'sushi',
#                 'disapoointed': 'disappointed',
#                 'disapointed':'disappointed',
#                 'disapointment':'disappointment',
#                 'Amzing':'Amazing',
#                 'bAd':'bad',
#                 'fantastics':'fatastic',
#                 'flavuorful':'flavorful',
#                 'infomation':'information',
#                 'informaiton':'information',
#                 'eveeyone':'everyone',
#                 'Hsppy':'Happy',
#                 'waygu':'wagyu',
#                 'unflavorful':'untasty',
#                 'Flavortown': 'Flavor Town',
#                 'wi-fi':'wifi',
#                 'ayce':'all you can eat',
#                 'appriceiate':'appriciate',
#                 'worest':'worst'}
#
# def correct_spelling(x):
#     x = str(x)
#     for word in mispell_dict.keys():
#         if word in x:
#             x = x.replace(word, mispell_dict[word])
#     return x
#
# # seperate words, numbers and some unremoved punctuations such as ,.?!
# def seperate_word(x):
#     for pattern, repl in [('[\W]',lambda p:' '+p.group()+' '),('[0-9]{1,}',lambda p:' '+p.group()+' ')]:
#         if re.search(pattern,x):
#             x = re.sub(pattern, repl, x)
#     return x
#
# # tokenize text
# def tokenizeRawData(text):
#     sb = SnowballStemmer("english")
#     text = clean_contraction(text)
#     text = clean_punc(text)
#     text = fix_time(text)
#     text = correct_spelling(text)
#     text = seperate_word(text)
#     text = text.lower()
#     tokenizer = RegexpTokenizer(r"[A-Za-z]\w+(?:[-'?]\w+)?")
#     output = tokenizer.tokenize(text)
#     for i in range(len(output)):
#             token = output[i]
#             output[i] = sb.stem(token)
#     return output
#
# def Search(astring):
#     tokenizedDoc = db.tokenizedDoc
#     services = db.Services
#     astring = str(astring)
#     cursor = tokenizedDoc.find()
#     data = cursor[0]
#     token_string = tokenizeRawData(astring)
#     outcome = []
#     for ID, content in data.items():
#         if ID != '_id':
#             cnt = 0
#             for eachWord in set(token_string):
#                 if eachWord in content:
#                     cnt += 1
#             if cnt / len(token_string) >= 0.50:
#                 outcome.append(ID)
#     if len(outcome) == 0:
#         return 'No Results Found'
#     else:
#         cursor = services.find()
#         search_result = []
#         for document in cursor:
#             MatchedKey = str(document['_id'])
#             if MatchedKey in outcome:
#                 search_result.append(document)
#         search_result = meanRating(search_result)
#         return search_result
