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
;;(import prosaic.util)
;;(import prosaic.cthulhu)
;;(import prosaic.nyarlathotep)

;; Relevant includes for driver code
(import sys)
(import [argparse [ArgumentParser]])
(import [json [loads]])
(import [os [environ]])
(import [os.path [join]])
(import [pymongo [MongoClient]])
(import [prosaic.nyarlathotep [process-txt!]])
(import [prosaic.cthulhu [poem-from-template]])

(def DEFAULT-HOST "localhost")
(def DEFAULT-PORT 27017)
(def PROSAIC-HOME (.get environ "PROSAIC_HOME" "~/.prosaic"))
(def DEFAULT-DB "prosaic")
(def DEFAULT-TMPL "haiku")
(def DEFAULT-TMPL-EXT "json")

(def TEMPLATES (join PROSAIC-HOME "templates"))
(def POEMS (join PROSAIC-HOME "poems"))

;; CLI UI
;; prosaic corpus ls -hpd
;; prosaic corpus loadfile -h <host> -p <port> -d <db> <filename>
;; prosaic corpus rm -h <host> -p <port> -d <db>
;; prosaic poem new -h <host> -p <port> -d <db> -t <tmpl> (<name>)
;; prosaic poem ls
;; prosaic poem rm <filename>
;; prosaic poem clean
;; prosaic template new <name>
;; prosaic template ls
;; prosaic template rm <name>
;; prosaic install <path>
;; General utility
(defn slurp [filename] (->> (open filename)
                            (.readlines)
                            (map (fn [s] (.replace s "\r\n" " ")))
                            (.join "")))

(defn read-template [name]
  (-> (join TEMPLATES name DEFAULT_TMPL_EXT)
      slurp))

;; Datbase interaction
(defn db-connect [dbhost dbport dbname]
  (. (MongoClient dbhost dbport) [dbname] phrases))

(defn arg-parser [] (ArgumentParser))
(defn add-argument [arg-parser name type &optional default]
  (apply .add_argument [arg-parser name] {"type" type "default" (or default nil)})
  arg-parser)

(defn init-arg-parser []
  ;; TODO pass in defaults, env
  (let [[top-level-parser (apply ArgumentParser [] {"prog" "prosaic"})]
        [add-db-args! (fn [ap] (-> ap
                                   (add-argument "--host" str DEFAULT-HOST)
                                   (add-argument "--port" int DEFAULT-PORT)
                                   (add-argument "--dbname" str DEFAULT-DB)))]

        [subparsers (.add_subparsers top-level-parser)]

        [corpus-parser   (.add_parser subparsers "corpus")]
        [corpus-subs     (.add_subparsers corpus-parser)]

        [corpus-ls (-> (.add_parser corpus-subs "ls")
                       add-db-args!)]
        [corpus-rm (-> (.add_parser corpus-subs "rm")
                       add-db-args!)]
        [corpus-load (-> (.add_parser corpus-subs "loadfile")
                         add-db-args!)]

        [poem-parser (-> (.add_parser subparsers "poem")
                         add-db-args!)]
        [poem-subs (.add_subparsers poem-parser)]

        [poem-new  (-> (.add_parser poem-subs "new")
                       add-db-args!)]
        [poem-ls (.add_parser poem-subs "ls")]
        [poem-rm (.add_parser poem-subs "rm")]
        [poem-clean (.add_parser poem-subs "clean")]

        [template-parser (.add_parser subparsers "template")]
        [template-subs (.add_subparsers template-parser)]

        [template-ls (.add_parser template-subs "ls")]
        [template-rm (.add_parser template-subs "rm")]
        [template-new (.add_parser template-subs "new")]

        [install-parser  (.add_parser subparsers "install")]]

    top-level-parser))

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

;; Driver code
(defn main []
  (let [[argument-parser (init-arg-parser)]]
    (.parse_args argument-parser)))

(if (= __name__ "__main__")
  (.exit sys (main)))
