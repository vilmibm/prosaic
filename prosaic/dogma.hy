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
(import re)

(import [nlp [word->stem]])
(import [util [match random-nth]])

;; # General Utility
(defn smatch [pat str]
  (let [[wrapped-pat (+ ".*" pat ".*")]
        [reg-pat (.compile re wrapped-pat)]]
    (match reg-pat str)))

(defclass rule []
  [[__slots__ []]
   [strength 0]
   [weaken! (fn [self]
              (let [[str (. self strength)]]
                (if (> str 0)
                  (setv (. self strength) (dec str)))))]

   [to-query (fn [self]
               ; Typically there would be a cond over (. self
               ; strength) here, but this base class represents the
               ; trivial rule.
               {})]])

(defclass syllable-count-rule [rule]
   [[__slots__ ["syllables" "strength"]]
    [to-query (fn [self]
               (if (= 0 (. self strength))
                  (.to-query (super))
                  (let [[syllables (. self syllables)]
                        [modifier  (- syllables (. self strength))]
                        [lte       (+ syllables modifier)]
                        [gte       (- syllables modifier)]]
                    {"num_syllables" {"$lte" lte "$gte" gte}})))]

   [__init__ (fn [self syllables]
               (setv (. self syllables) syllables)
               (setv (. self strength) syllables)
               nil)]])


(defclass keyword-rule [rule]
  [[__slots__ ["keyword" "phrase_cache" "strength"]]
   [max-strength 11]
   [where-clause-tmpl "Math.abs({} - this.line_no) <= {}"]

   [__init__ (fn [self keyword db]
               (setv (. self strength) 11)
               (setv (. self keyword) (word->stem keyword))
               (.prime-cache! self db)
               nil)]

   [prime-cache! (fn [self db]
                   (print "building phrase cache")
                   (setv (. self phrase-cache)
                         (list (.find db {"stems" (. self keyword)})))
                   (if (empty? (. self phrase-cache))
                     (setv (. self strength) 0)))]

   [to-query (fn [self]
               (if (= 0 (. self strength))
                 (.to-query (super))
                 (let [[phrase      (random-nth (. self phrase-cache))]
                       [ok-distance (- (. self max-strength)
                                       (. self strength))]
                       [line-no     (. phrase ["line_no"])]]
                   {"source" (. phrase ["source"])
                    "$where" (.format (. self where-clause-tmpl)
                                      line-no
                                      ok-distance)})))]])

(defclass fuzzy-keyword-rule [keyword-rule]
  [[to-query (fn [self]
               (if (= 0 (. self strength))
                 (.to-query (super))
                 (let [[phrase      (random-nth (. self phrase-cache))]
                       [ok-distance (inc (- (. self max-strength)
                                            (. self strength)))]
                       [line-no     (. phrase ["line_no"])]]
                   {"source" (. phrase ["source"])
                    "line_no" {"$ne" line-no}
                    "$where" (.format (. self where-clause-tmpl)
                                      line-no
                                      ok-distance)})))]])

(defclass rhyme-rule [rule]
  [[__slots__ ["sound" "strength"]]
   [__init__ (fn [self rhyme]
               (setv (. self strength) 3)
               (setv (. self sound) rhyme)
               nil)]
   [next-sound (fn [self]
                 (let [[str   (. self strength)]
                       [sound (. self sound)]]
                   (cond [(= 3 str) sound]
                         [(= 2 str)
                          (cond [(smatch "0" sound)
                                 (.replace sound "0" "1")]
                                [(smatch "1" sound)
                                 (.replace sound "1" "2")]
                                [(smatch "2" sound)
                                 (.replace sound "2" "0")])]
                         [(= 1 str)
                          (cond [(smatch "0" sound)
                                 (.replace sound "0" "2")]
                                [(smatch "1" sound)
                                 (.replace sound "1" "0")]
                                [(smatch "2" sound)
                                 (.replace sound "2" "1")])])))]
   [to-query (fn [self]
               (if (= 0 (. self strength))
                 (.to-query (super))
                   {"rhyme_sound" (.next-sound self)}))]])
