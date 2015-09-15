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

(require hy.contrib.loop)

(import [functools [reduce]])

(import [nlp [is-vowel-pho? is-punct-tag? is-vowel? is-alpha-tag? word->stem word->phonemes tokenize-sen tag word->chars sentence->stems]])

;; # General Utility Functions
(defn plus [x y] (+ x y)) ;; 2-arity for reducing
(defn sum [xs] (reduce plus xs 0))

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
       sum))

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
  {"stems"         (sentence->stems tagged-sen)
   "source"        source
   "tagged"        tagged-sen
   "rhyme_sound"   (rhyme-sound tagged-sen)
   "phonemes"      (->> tagged-sen
                      (map first)
                      (map word->phonemes)
                      list)
   "num_syllables" (count-syllables tagged-sen)
   "line_no"       line-no
   "raw"           (tagged->str tagged-sen)})

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
