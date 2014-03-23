(import [nltk.stem.snowball [EnglishStemmer]])

(def stemmer (EnglishStemmer))

(defn word->stem [word] (.stem stemmer word))
