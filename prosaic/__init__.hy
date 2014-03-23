;; These are here so this file can be used to programmatically include
;; the various prosaic modules
;; (eg (import [prosaic.nyarlathotep [process-txt!]]))
(import util)
(import cthulhu)
(import nyarlathotep)

;; Relevant includes for driver code
(require hy.contrib.multi)
(import [json [loads]])
(import sys)
(import [pymongo [MongoClient]])
(import [nyarlathotep [process-txt!]])
(import [cthulhu [poem-from-template]])

;; General utility
(defmulti main-err
  ([msg code] (print msg) code)
  ([msg] (print msg) 1)
  ([] (print "An error happened." 1)))

(defn slurp [filename] (->> (open filename)
                            (.readlines)
                            (map (fn [s] (.replace s "\r\n" " ")))
                            (.join "")))

;; Frontends
(defn load [txt-filename db]
  (let [[txt (slurp txt-filename)]]
    (process-txt! txt txt-filename db)))

(defn create [template-filename db]
  (let [[template (->> template-filename
                       slurp
                       loads)]]
    (poem-from-template template db)))

;; Datbase interaction
(defn db-connect [dbname]
  (. (MongoClient) [dbname] phrases))

;; Driver code
(defn dispatch [action args]
  (let [[fun (cond [(= action "load") load]
                   [(= action "create") create])]]
    (print (apply fun args))
    0))
    ;;(try (do
    ;;      (print (apply fun args))
    ;;      0)
    ;;     (catch [e Exception]
    ;;       (raise e)
    ;;       (main-err e)))))

(defmulti main
  ([action filename dbname]
   (dispatch action [filename (db-connect dbname)]))
  ([action filename]
   (dispatch action [filename (db-connect "prosaic")]))
  ([action]
   (main-err "Filename required" 2))
  ([]
   (main-err "Action and filename required")))

(if (= __name__ "__main__")
  (.exit sys (apply main (rest (. sys argv)))))
