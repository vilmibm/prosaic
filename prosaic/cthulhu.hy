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
(loop [[x nil]] x) ; this is here to fix a threading / sys.modules issue

(import [concurrent.futures [ThreadPoolExecutor]])
(import [copy [deepcopy]])
(import [functools [partial reduce]])
(import [json [loads]])
(import sys)

(import [dogma [keyword-rule
                fuzzy-keyword-rule
                rhyme-rule
                syllable-count-rule]])
(import [util [random-nth]])

; # General Utility
(defn pluck [col-of-dicts key]
  (list (map (fn [d] (.get d key)) col-of-dicts)))
(defn merge [d0 d1]
  (let [[d0-copy (deepcopy d0)]]
    (.update d0-copy d1)
    d0-copy))

(defn merge! [d0 d1]
  (.update d0 d1)
  d0)

; # Rules and Rulesets
(defclass rule-set []
  [[rules []]
   [__init__ (fn [self rules]
               (setv (. self rules) rules)
               nil)]
   [to-query (fn [self]
               (->> (. self rules)
                    (map (fn [r] (.to-query r)))
                    (reduce merge!)))]
   [weaken! (fn [self]
              (.weaken! (random-nth (. self rules)))
              self)]])

(defn build-sound-cache [db]
  (.distinct (.find db) "rhyme_sound"))

(defn build-letters->sounds [db template &optional sound-cache]
  (let [[letters (list (set (pluck template "rhyme")))]]
    (if (empty? letters)
      {}
      (let [[sounds  (if sound-cache
                       sound-cache
                       (build-sound-cache db))]]
        (->> letters
             (map (fn [l] [l (random-nth sounds)]))
             dict)))))

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

(defn template->rulesets [db template executor &optional sound-cache]
  (let [[letters->sounds (build-letters->sounds
                          db template sound-cache)]]
  (list (.map executor (partial extract-ruleset db letters->sounds) template))))

(defn ruleset->line [db ruleset]
  (loop [[line nil] [r ruleset]]
        (let [[query (.to-query r)]
              [lines (list (.find db query))]]
          (if (empty? lines)
            (recur nil (.weaken! ruleset))
            (do
             (random-nth lines))))))

; # Main entry point
(defn poem-from-template [template db &optional sound-cache]
  (let [[executor (ThreadPoolExecutor 4)]
        [letters->sounds (build-letters->sounds db template sound-cache)]
        [poem-lines (.map executor (fn [tmpl-line]
                                     (->> tmpl-line
                                         (extract-ruleset db letters->sounds)
                                         (ruleset->line db)))
                          template)]]
    (.shutdown executor)
    (list poem-lines)))
