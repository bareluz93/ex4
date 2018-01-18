import wikipedia, spacy, copy

nlp_model = spacy.load('en')



# for token in analyzed_page:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#           token.shape_, token.is_alpha, token.is_stop)


class linear_relation_extractor:
    def __init__(self):
        self.last_token_was_propnoun = False

        self.relations_triplets = []
        self.prop_noun_set = set()
        self.triplet = {'subject': [], 'relation': [], 'object': []}

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

    # evaluate linear extractor
    def evaluate(self,analyzed_page,name):
        for token in analyzed_page:
            self.step(token)
        result = self.extract_valid_triplets()

        for triplet in result[:10]:
            print("----------------")
            print(triplet)
        print('num of triplets in the linear extractor of ' + name + " page = " + str(len(result)))



class tree_relation_extractor:
    def __init__(self):
        self.relations_triplets = []
        self.heads_set = set()

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
                self.heads_set.add(token)
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
        if token1.head == token2.head.head and token1.dep_ == "nsubj" and token2.dep_ == "pobj" and token2.head.dep_ == "prep" :
            triplet = {'subject': [token1], 'relation': [token2.head.head, token2.head], 'object': [token2]}
            return triplet
        return None

    # iterate over all triplets and add the children of the propn-head. return the triplet list
    def extract_all_children(self):
        for triplet in self.relations_triplets:

            cur_subj=triplet['subject'][0]
            for child in cur_subj.children:
                if child.dep_ == 'compound':
                    triplet['subject'].append(child)

            cur_obj = triplet['object'][0]
            for child in cur_obj.children:
                if child.dep_ == 'compound':
                    triplet['object'].append(child)

    def evaluate(self,sents,name):
        for sent in sents:
            self.parse_sentence(sent)
        self.extract_all_children()

        for triplet in self.relations_triplets[:10]:
            print("----------------")
            print(triplet)
        print('num of triplets in the tree extractor of ' + name + " page = " + str(len(self.relations_triplets)))


if __name__ == '__main__':
    pages_names=['Brad Pitt','Donald Trump','Angelina Jolie']
    for name in pages_names:
        print('********************************************************')
        page = wikipedia.page(name).content
        analyzed_page = nlp_model(page)

        tree_extractor = tree_relation_extractor()
        linear_extractor = linear_relation_extractor()

        linear_extractor.evaluate(analyzed_page,name)
        print('********************************************************')
        tree_extractor.evaluate(analyzed_page.sents,name)





