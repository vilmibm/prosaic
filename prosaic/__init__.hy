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
(import [argparse [ArgumentParser FileType]])
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
  (let [[path (if (.startswith name "/")
                name
                (join TEMPLATES (+ name "." DEFAULT_TMPL_EXT)))]]
        (slurp path)))

;; Datbase interaction
(defn db-connect [dbhost dbport dbname]
  (. (MongoClient dbhost dbport) [dbname] phrases))

(defn args->db [parsed-args]
  (db-connect (. parsed-args host)
              (. parsed-args port)
              (. parsed-args dbname)))

(defn args->template [parsed-args]
  (-> (if (. parsed-args tmpl-raw)
        (->> (. parsed-args infile)
             .readlines
             (.join ""))
        (read-template (. parsed-args tmpl)))
      loads))

(defn corpus-loadfile* [parsed-args]
  (let [[db (args->db parsed-args)]
        [path (. parsed-args path)]
        [txt (slurp path)]]
    (process-txt! txt path db)))

(defn corpus-ls* [] "corpus ls")

(defn corpus-rm* [] "corpus rm")

(defn poem-new* [parsed-args]
  (let [[template (args->template parsed-args)]
        [db (args->db parsed-args)]
        [poem-lines (poem-from-template template db)]]
    (for [line poem-lines]
      (print (.get line "raw")))))

(defn poem-ls* [] "poem ls")
(defn poem-rm* [] "poem rm")
(defn poem-clean* [] "poem clean")

(defn template-ls* [] "tmpl ls")
(defn template-new* [] "tmpl new")
(defn template-rm* [] "tmpl rm")
(defn install* [] "install")

(defn arg-parser [] (ArgumentParser))
(defn add-argument! [arg-parser args kwargs]
  (apply .add_argument (+ [arg-parser] args) kwargs)
  arg-parser)
(defn set-defaults! [arg-parser defaults]
  (apply .set_defaults [arg-parser] defaults)
  arg-parser)

(defn init-arg-parser []
  ;; TODO pass in defaults, env
  (let [[top-level-parser (apply ArgumentParser [] {"prog" "prosaic"})]
        [add-db-args! (fn [ap] (-> ap
                                   (add-argument! ["-n" "--host"]
                                                  {"type" str
                                                   "default" DEFAULT-HOST
                                                   "action" "store"})

                                   (add-argument! ["-p" "--port"]
                                                  {"type" int
                                                   "default" DEFAULT-PORT
                                                   "action" "store"})

                                   (add-argument! ["-d" "--dbname"]
                                                  {"type" str
                                                   "default" DEFAULT-DB
                                                   "action" "store"})))]

        [subparsers (.add_subparsers top-level-parser)]

        [corpus-parser (.add_parser subparsers "corpus")]
        [corpus-subs (.add_subparsers corpus-parser)]
        [poem-parser (.add_parser subparsers "poem")]
        [poem-subs (.add_subparsers poem-parser)]
        [template-parser (.add_parser subparsers "template")]
        [template-subs (.add_subparsers template-parser)]]

    (add-argument! top-level-parser ["infile"] {"nargs" "?"
                                                "type" (FileType "r")
                                                "default" sys.stdin})

    ;; corpus ls
    (-> (.add_parser corpus-subs "ls")
        (set-defaults! {"func" corpus-ls*})
        add-db-args!)

    ;; corpus rm
    (-> (.add_parser corpus-subs "rm")
        (set-defaults! {"func" corpus-rm*})
        add-db-args!)

    ;; corpus loadfile
    (-> (.add_parser corpus-subs "loadfile")
        (set-defaults! {"func" corpus-loadfile*})
        (add-argument! ["path"]
                       {"type" str "action" "store"})
        add-db-args!)

    ;; poem new
    (-> (.add_parser poem-subs "new")
        (set-defaults! {"func" poem-new*})
        (add-argument! ["-r" "--tmpl-raw"]
                       {"action" "store_true"})
        (add-argument! ["-t" "--tmpl"]
                       {"type" str
                        "default" "haiku"
                        "action" "store"})
        add-db-args!)

    ;; poem ls
    (-> (.add_parser poem-subs "ls")
        (set-defaults! {"func" poem-ls*}))

    ;; poem rm
    (-> (.add_parser poem-subs "rm")
        (set-defaults! {"func" poem-rm*}))

    ;; poem clean
    (-> (.add_parser poem-subs "clean")
        (set-defaults! {"func" poem-clean*}))

    ;; template ls
    (-> (.add_parser template-subs "ls")
        (set-defaults! {"func" template-ls*}))

    ;; template rm
    (-> (.add_parser template-subs "rm")
        (set-defaults! {"func" template-rm*}))

    ;; template new
    (-> (.add_parser template-subs "new")
        (set-defaults! {"func" template-new*}))

    ;; install
    (-> (.add_parser subparsers "install")
        (set-defaults! {"func" install*}))

    top-level-parser))

;; Driver code
(defn main []
  (let [[argument-parser (init-arg-parser)]
        [parsed-args (.parse_args argument-parser)]]
    ((. parsed-args func) parsed-args)
    0))

(if (= __name__ "__main__")
  (.exit sys (main)))
