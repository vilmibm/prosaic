(require hy.contrib.loop)

(import [functools [partial reduce]])
(import re)
(import sys)

(import nltk)
(import [nltk.chunk :as chunk])
(import [nltk.stem.snowball [EnglishStemmer]])
(import [nltk.corpus [cmudict]])


;; # General Utility Functions
(defn invert [f] (fn [&rest args] (not (apply f args))))
(defn plus [&rest args] (reduce (fn [x y] (+ x y))) args)
(defn match [regex str] (bool (.match regex str)))
(defn plus [x y] (+ x y))
(defn comp [f g] (fn [&rest args] (f (apply g args))))

;; # NLTK Helpers
(def sd (nltk.data.load "tokenizers/punkt/english.pickle"))
(def stemmer (EnglishStemmer))
(def cmudict-dict (.dict cmudict))
(def vowel-pho-re (.compile re "AA|AE|AH|AO|AW|AY|EH|EY|ER|IH|IY|OW|OY|UH|UW"))
(def vowel-re (.compile re "[aeiouAEIOU]"))
(def punct-tag-re (.compile re "^[^a-zA-Z]+$"))

(def is-vowel? (partial match vowel-re))
(def is-vowel-pho? (partial match vowel-pho-re))
(def is-punct-tag? (partial match punct-tag-re))
(def is-alpha-tag? (invert is-punct-tag?))

(defn word->phonemes [word]
  (try
   (first (get cmudict-dict (.lower word)))
   (catch [e KeyError]
     []))) ;; Not sure what is best here...

(defn tokenize-sen [raw-text]
  (.tokenize sd raw-text))

(defn tag [sentence-str] (->> sentence-str
                              (.word-tokenize nltk)
                              (.pos-tag nltk)))

(defn word->chars [word] (list word))
(defn word->stem [word] (.stem stemmer word))
(defn sentence->stems [tagged-sen]
  (->> tagged-sen
       (map (comp word->stem first))
       list))

(defn rhyme-sound [tagged-sen]
  (let [[is-punct-pair? (fn [tu] (is-alpha-tag? (second tu)))]
        [no-punct       (list (filter is-punct-pair? tagged-sen))]]
    (if (empty? no-punct)
      nil
      (let [[last-word (->> (list no-punct)
                            reversed
                            list
                            first
                            first)]
            [phonemes  (word->phonemes last-word)]]
        (.join "" (->> (reversed phonemes)
                       (take 3)
                       list
                       reversed
                       list))))))

(defn count-syllables-in-word [word]
  (let [[phonemes  (word->phonemes word)]
        [vowels (if phonemes
                  (filter is-vowel-pho? phonemes)
                  (->> (word->chars word) ;; fall back to raw vowel counting
                       (filter is-vowel?)))]]
    (len (list vowels))))

(defn count-syllables [tagged-sen]
  (->> tagged-sen
       (map first)
       (map count-syllables-in-word)
       (reduce plus)))

(defn tagged->str [tagged-sen]
  (loop [[str ""] [t-s tagged-sen]]
        (if (empty? t-s)
          str
          (let [[token-tuple (first t-s)]
                [text        (first token-tuple)]
                [tag         (second token-tuple)]
                [text        (if (is-punct-tag? tag) text (+ " " text))]]
            (recur (+ str text) (rest t-s))))))

;; # Database Interaction
(defn store! [db data] (.insert db data))

;; # Text Pre-processing
(defn multiclause? [tagged-sen]
  (some (fn [tu] (= ":" (second tu))) tagged-sen))

(defn split-multiclause [tagged-sen]
  (if (multiclause? tagged-sen)
    (let [[pred          (fn [x] (not (= ":" (second x))))]
          [first-clause  (list (take-while pred tagged-sen))]
          [second-clause (list (drop-while pred tagged-sen))]]
      [first-clause second-clause])
    [tagged-sen]))

(defn expand-multiclause [tagged-sens]
  (let [limit (len tagged-sens)]
    (loop [[t-s tagged-sens] [new []]]
          (if (empty? t-s)
            new
            (recur (rest t-s) (+ new (split-multiclause (first t-s))))))))

(defn process-sentence [tagged-sen source line-no]
  {:stems         (sentence->stems tagged-sen)
   :tagged        tagged-sen
   :rhyme-sound   (rhyme-sound tagged-sen)
   :phonemes      (->> tagged-sen
                      (map first)
                      (map word->phonemes)
                      list)
   :num-syllables (count-syllables tagged-sen)
   :raw           (tagged->str tagged-sen)})

;; # Main entry point for text processing
(defn process-txt! [raw-text source db]
  (let [[tagged-sens (->> raw-text
                          tokenize-sen
                          (map tag)
                          list
                          (expand-multiclause))]]
    (for [ix (range 0 (len tagged-sens))]
      (let [[tagged-sen (nth tagged-sens ix)]
            [to-db      (process-sentence tagged-sen source ix)]]
        (store! db to-db)))))
