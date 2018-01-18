import wikipedia, spacy, copy
nlp_model = spacy.load('en')
page = wikipedia.page('Brad Pitt').content
analyzed_page = nlp_model(page)
for token in analyzed_page:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop)

relations_triplets=[]
prop_noun_set=set()
triplet={}
first_propnoun_found=False
verb_found=False
prop_noun=[]
for token in analyzed_page:
    if token.pos_=='PROPN':
        prop_noun.append(token.text)
    if prop_noun and token.pos_ != 'PROPN':
        prop_noun_full=" ".join(prop_noun)
        prop_noun_set.add(prop_noun_full)
        prop_noun.clear()
        if not first_propnoun_found:
            triplet['subject']=prop_noun_full
            first_propnoun_found=True
            triplet['relation']=[]
        if first_propnoun_found and verb_found:
            # insert relation ***
            triplet['object'] = prop_noun_full
            # clear all!!!!
            first_propnoun_found = False
            verb_found = False
            relations_triplets.append(copy.deepcopy(triplet))
            triplet.clear()
        if first_propnoun_found and not verb_found:
            first_propnoun_found = False
            verb_found = False
            triplet.clear()
    if token.pos_=='VERB' and first_propnoun_found:
        verb_found = True
    if first_propnoun_found and (token.pos_=='VERB' or token.pos_=='ADP'):
        triplet['relation'].append(token.text)


# print(prop_noun_set)






