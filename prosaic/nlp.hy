;   This program is part of prosaic.

;   This program is free software: you can redistribute it and/or modify
;   it under the terms of the GNU General Public License as published by
;   the Free Software Foundation, either version 3 of the License, or
;   (at your option) any later version.

;   This program is distributed in the hope that it will be useful,
;   but WITHOUT ANY WARRANTY; without even the implied warranty of
;   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;   GNU General Public License for more details.

;   You should have received a copy of the GNU General Public License
;   along with this program.  If not, see <http://www.gnu.org/licenses/>.

(import [os.path [join exists dirname expanduser]])
(import [functools [partial]])
(import re)
(import nltk)
(import [prosaic.util [match]])

(def NLTK-DATA-PATH (join (expanduser "~") "nltk_data"))
(def NLTK-DATA ["punkt"
                "maxent_ne_chunker"
                "cmudict"
                "words"
                "maxent_treebank_pos_tagger"])

(if-not (exists NLTK-DATA-PATH)
  (for [datum NLTK_DATA]
    (nltk.download datum)))

(import [nltk.stem.snowball [EnglishStemmer]])
(import [nltk.chunk :as chunk])
(import [nltk.corpus [cmudict]])

(defn invert [f] (fn [&rest args] (not (apply f args))))
(defn comp [f g] (fn [&rest args] (f (apply g args))))

(def stemmer (EnglishStemmer))

(defn word->stem [word] (.stem stemmer word))

(def sd (nltk.data.load "tokenizers/punkt/english.pickle"))
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
(defn sentence->stems [tagged-sen]
  (->> tagged-sen
       (map (comp word->stem first))
       list))

