import wikipedia, spacy, copy

nlp_model = spacy.load('en')
page = wikipedia.page('Brad Pitt').content
analyzed_page = nlp_model(page)


# for token in analyzed_page:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#           token.shape_, token.is_alpha, token.is_stop)


class linear_relation_extractor:
    last_token_was_propnoun = False

    relations_triplets = []
    prop_noun_set = set()
    triplet = {'subject': [], 'relation': [], 'object': []}

    def step(self, token):
        if token.pos_ == "PROPN":
            self.handle_propn(token)
        else:
            if self.last_token_was_propnoun:
                self.finish_last_triplet_and_start_next()
            if token.pos_ == "VERB" or token.pos_ == "ADP":
                self.handle_verb_or_adp(token)
            elif token.pos_ == 'PUNCT':
                self.reset()

    def finish_last_triplet_and_start_next(self):
        self.relations_triplets.append(self.triplet)
        next_subject = self.triplet['object']
        self.triplet = {'subject': next_subject, 'relation': [], 'object': []}
        self.last_token_was_propnoun = False

    # call only when getting punctuation and moving to the next sentence
    def reset(self):
        self.triplet = {'subject': [], 'relation': [], 'object': []}

    def handle_propn(self, token):
        self.prop_noun_set.add(token.text)
        self.last_token_was_propnoun = True
        self.triplet['object'].append(token)

    def handle_verb_or_adp(self, token):
        self.triplet['relation'].append(token)

    # this method return the output to part 1
    def extract_valid_triplets(self):
        result = []
        for triplet in self.relations_triplets:
            if self.relation_contains_verb(triplet['relation']):
                result.append(triplet)
        self.relations_triplets = result
        return result


    def relation_contains_verb(self, relation):
        for token in relation:
            if token.pos_ == "VERB":
                return True
        return False
extractor = linear_relation_extractor()
for token in analyzed_page:
    extractor.step(token)
result = extractor.extract_valid_triplets()

for i in range(len(analyzed_page)):
    triplet = result[i]
    print("-------i = "+str(i))
    print(triplet)