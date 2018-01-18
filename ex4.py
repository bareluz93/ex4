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
            if self.relation_contains_verb(triplet['relation']) and (triplet['subject']) and (triplet['object']):
                result.append(triplet)
        self.relations_triplets = result
        return result

    def relation_contains_verb(self, relation):
        for token in relation:
            if token.pos_ == "VERB":
                return True
        return False


extractor = linear_relation_extractor()


# for token in analyzed_page:
#     extractor.step(token)
# result = extractor.extract_valid_triplets()
#
# for triplet in result:
#     print("----------------")
#     print(triplet)

class tree_relation_extractor:
    relations_triplets = []
    prop_noun_set = set()

    # insert all triplets in the sentence to the relation_triplets list
    def parse_sentence(self, sentence):
        heads = self.extract_heads(sentence)
        for head1 in heads:
            for head2 in heads:
                triplet = self.check_condition_1(head1, head2)
                if not triplet:
                    triplet = self.check_condition_2(head1, head2)
                if triplet:
                    self.relations_triplets.append(triplet)

    # return all prpn-heads in the sentence as a list
    def extract_heads(self, sent):
        heads = []
        for token in sent:
            if token.pos_ == 'PROPN' and not token.dep_ == 'compound':
                heads.append(token)
        return heads

    # if condition is true, return the triplet (without the full prpn, just heads)
    # else return None
    def check_condition_1(self, token1, token2):
        if token1.head == token2.head and token1.dep_ == "nsubj" and token2.dep_ == "dobj":
            triplet = {'subject': [token1], 'relation': [token2.head], 'object': [token2]}
            return triplet
        return None

    # if condition is true, return the triplet (without the full prpn, just heads)
    # else return None
    def check_condition_2(self, token1, token2):
        if token1.head == token2.head.head and token1.dep_ == "nsubj" and token2.dep_ == "prep" and token2.head.dep_ == "pobj":
            triplet = {'subject': [token1], 'relation': [token2.head.head, token2.head], 'object': [token2]}
            return triplet
        return None

    # iterate over all triplets and add the children of the propn-head. return the triplet list
    def extract_all_children(self):
        print("TBD")
        return None

tree_extractor=tree_relation_extractor()
for sent in analyzed_page.sents:
    tree_extractor.parse_sentence(sent)
result2=tree_extractor.relations_triplets

for triplet in result2:
    print("----------------")
    print(triplet)