(require hy.contrib.loop)
(require macro-util)

(import [functools [partial]])
(import [json [loads]])
(import [random [randint]])
(import sys)

; # General Utility
(defn random-nth [l] (nth l (randint 0 (dec (len l)))))

; # Working with Rulesets
(defn ruleset->query [ruleset] "todo")
(defn weaken-ruleset [ruleset] "todo")
(defn template->rulesets [db template] "todo")

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


(comment
 input: [{syllables: 5, rhyme: 'A', keyword:'funicular'},
         {syllables: 7, rhyme: 'B', fuzzy: 'garbage'},
         {syllables: 5, rhyme: 'A', keyword:'growth'}]
)

(comment
 prepreprocessing: convert each line to a ruleset (list of rules)
 preprocessing: keyword parsing, rhyme parsing
 processing: for each ruleset, reduce into a query
             if a match is found, add it to poem
             otherwise, weaken the ruleset and recur
)
