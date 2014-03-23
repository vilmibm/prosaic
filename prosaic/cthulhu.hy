(require hy.contrib.loop)
;(require macro-util)

(import [copy [deepcopy]])
(import [functools [partial]])
(import [json [loads]])
(import [random [randint]])
(import sys)

; # General Utility
(defn random-nth [l] (nth l (randint 0 (dec (len l)))))
(defn prepend [l item] (+ l [item]))
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
              (weaken! (rand-nth (. self rules))))]])

(defclass rule []
  [[strength 0]
   [weaken! (fn [self]
              (let [[str (. self strength)]]
                (if (> str 0)
                  (do (setv (. self strength) (dec str))
                      self))))]

   [to-query (fn [self]
               ; Typically there would be a cond over (. self
               ; strength) here, but this base class represents the
               ; trivial rule.
               {})]])

(defclass syllable-count-rule [rule]
   [[to-query (fn [self]
               (if (= 0 (. self strength))
                  (.to-query (super))
                  (let [[syllables (. self syllables)
                        [modifier  (- syllables (. self strength))]
                        [lte       (+ syllables modifier)]
                        [gte       (- syllables modifier)]]
                    {"num_syllables" {"$lte" lte "$gte" gte}})))]

   [__init__ (fn [self syllables]
               (setv (. self syllables) syllables)
               (setv (. self strength) syllables)
               nil)]])


(defclass keyword-rule [rule]
  [[strength 11]
   [to-query (fn [self]
               (if (= 0 (. self strength))
                 (.to-query (super))
                 (let [[str (. self strength)]]
                   (cond [(= str 11) {}]))))]])

; # Working with Rulesets
(defn ruleset->query [ruleset] "todo")
(defn weaken-ruleset [ruleset] "todo")
(defn template->rulesets [db template] "todo")

(defn foo [] 2)

(defn ruleset->line [db ruleset]
  (loop [[line nil] [r ruleset]]
        (if line
          line
          (let [[query (ruleset->query r)]
                [lines (list (.find db query))]]
            (if (empty? lines)
              (recur nil (weaken-ruleset ruleset))
              (recur (random-nth lines) ruleset))))))

; # Main entry point
(defn poem-from-template [template db]
  (let [[rulesets (template->rulesets db template)]]
    (map (partial ruleset->line db) rulesets)))


;(comment
; input: [{syllables: 5, rhyme: 'A', keyword:'funicular'},
;         {syllables: 7, rhyme: 'B', fuzzy: 'garbage'},
;         {syllables: 5, rhyme: 'A', keyword:'growth'}]
;)
;
;(comment
; prepreprocessing: convert each line to a ruleset (list of rules)
; preprocessing: keyword parsing, rhyme parsing
; processing: for each ruleset, reduce into a query
;             if a match is found, add it to poem
;             otherwise, weaken the ruleset and recur
;)
