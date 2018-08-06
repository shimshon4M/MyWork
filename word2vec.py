from gensim.models import word2vec
import sys

#sentences=word2vec.Text8Corpus("./data/wakachi/NLP_L_C_wakachi_nolabel.txt")
#model=word2vec.Word2Vec(sentences,size=200,window=20)

#model.wv.save_word2vec_format("./data/model/word2vec_NLP_LCorpus.txt",fvocab=None,binary=False)

model=word2vec.Word2Vec.load("./data/model/word2vec_NLP_LCorpus.model")
print("input")
print(model.most_similar(sys.argv[1]))
