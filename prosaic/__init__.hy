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
    (process-txt! txt txt-filename db)
    (print "done.")))

(defn create [template-filename db]
  (let [[template (->> template-filename
                       slurp
                       loads)]
        [poem-lines (poem-from-template template db)]]
    (for [line poem-lines]
      (print (.get line "raw")))))

;; Datbase interaction
(defn db-connect [dbname &optional dbhost]
  (. (MongoClient dbhost) [dbname] phrases))

;; Driver code
(defn dispatch [action args]
  (let [[fun (cond [(= action "load") load]
                   [(= action "create") create])]]
    (apply fun args)
    0))
    ;;(try (do
    ;;      (print (apply fun args))
    ;;      0)
    ;;     (catch [e Exception]
    ;;       (raise e)
    ;;       (main-err e)))))

(defmulti main
  ([action filename dbname dbhost]
   (dispatch action [filename (db-connect dbname dbhost)]))
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
