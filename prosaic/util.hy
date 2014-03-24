(import re)

(defn match [regex str] (bool (.match regex str)))
