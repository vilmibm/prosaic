(import [random [randint]])
(import re)

(defn match [regex str] (bool (.match regex str)))
(defn random-nth [l] (nth l (randint 0 (dec (len l)))))
