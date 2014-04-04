(require hy.contrib.loop)
;(require macro-util)

(import [copy [deepcopy]])
(import [functools [partial reduce]])
(import [json [loads]])
(import sys)

(import [dogma [keyword-rule
                fuzzy-keyword-rule
                rhyme-rule
                syllable-count-rule]])
(import [nltk-util [word->stem]])
(import [util [random-nth]])

; # General Utility
(defn pluck [col-of-dicts key]
  (list (map (fn [d] (.get d key)) col-of-dicts)))
(defn merge [d0 d1]
  (let [[d0-copy (deepcopy d0)]]
    (.update d0-copy d1)
    d0-copy))

; # Rules and Rulesets
(defclass rule-set []
  [[rules []]
   [__init__ (fn [self rules]
               (setv (. self rules) rules)
               nil)]
   [to-query (fn [self]
               (->> (. self rules)
                    (map (fn [r] (.to-query r)))
                    (reduce merge)))]
   [weaken! (fn [self]
              (.weaken! (random-nth (. self rules)))
              self)]])

(defn build-sound-cache [db]
  (.distinct (.find db) "rhyme_sound"))

(defn build-letters->sounds [db template &optional sound-cache]
  (let [[letters (list (set (pluck template "rhyme")))]
        [sounds  (if sound-cache
                   sound-cache
                   (build-sound-cache db))]]
        (->> letters
             (map (fn [l] [l (random-nth sounds)]))
             dict)))

(defn extract-rule [db l->s raw-pair]
  (let [[type (first raw-pair)]
        [arg  (second raw-pair)]]
    (cond
     [(= type "rhyme") (rhyme-rule (.get l->s arg))]
     [(= type "keyword") (keyword-rule arg db)]
     [(= type "syllables") (syllable-count-rule arg)]
     [(= type "fuzzy") (fuzzy-keyword-rule arg db)])))

;; need to transform dictionary -> list of rules
(defn extract-ruleset [db letters->sounds tmpl-line]
  (->> tmpl-line
       .items
       (map (partial extract-rule db letters->sounds))
       list
       rule-set))

(defn template->rulesets [db template &optional sound-cache]
  (let [[letters->sounds (build-letters->sounds
                          db template sound-cache)]]
  (list (map (partial extract-ruleset db letters->sounds) template))))

(defn ruleset->line [db ruleset]
  (loop [[line nil] [r ruleset]]
        (let [[query (.to-query r)]
              [lines (list (.find db query))]]
          (if (empty? lines)
            (recur nil (.weaken! ruleset))
            (random-nth lines)))))

; # Main entry point
(defn poem-from-template [template db]
  (let [[rulesets (template->rulesets db template)]]
    (list (map (partial ruleset->line db) rulesets))))
