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
(import [subprocess [call]])
(import [argparse [ArgumentParser FileType]])
(import [json [loads]])
(import [os [environ listdir]])
(import [os.path [join exists dirname expanduser]])

(import nltk)
(import [sh [rm cp mkdir]])
(import [pymongo [MongoClient]])

(import [prosaic.nyarlathotep [process-txt!]])
(import [prosaic.cthulhu [poem-from-template]])

(def DEFAULT-HOST "localhost")
(def DEFAULT-PORT 27017)
(def PROSAIC-HOME (.get environ
                        "PROSAIC_HOME"
                        (join (expanduser "~") ".prosaic")))
(def DEFAULT-DB "prosaic")
(def DEFAULT-TMPL "haiku")
(def DEFAULT-TMPL-EXT "json")

(def TEMPLATES (join PROSAIC-HOME "templates"))

(def EXAMPLE-TMPL (join TEMPLATES ".example.template"))

;; CLI UI

;; prosaic poem new -h <host> -p <port> -d <db> -t <tmpl> -o <name>
;; prosaic corpus ls -hpd
;; prosaic corpus loadfile -h <host> -p <port> -d <db> <filename>
;; prosaic corpus rm -h <host> -p <port> -d <db>
;; prosaic template new <name>
;; prosaic template ls
;; prosaic template rm <name>

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

;; template installation
(defn installed? []
  (and
   (exists PROSAIC-HOME)
   (exists (join PROSAIC-HOME "templates"))))

(defn install! []
  (let [[install-path PROSAIC-HOME]
        [template-source (join (dirname (. sys modules ["prosaic"] __file__)) "templates")]]
    (mkdir install-path)
    (cp "-r" template-source install-path )))

;; Datbase interaction
(defn db-connect [dbhost dbport dbname]
  (. (MongoClient dbhost dbport) [dbname] phrases))

(defn args->mclient [parsed-args]
  (MongoClient (. parsed-args host)
               (. parsed-args port)))

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

(defn corpus-ls* [parsed-args]
  (let [[mc (args->mclient parsed-args)]]
    (for [db-name (.database_names mc)]
      (print db-name))))

(defn corpus-rm* [parsed-args]
  (let [[mc (args->mclient parsed-args)]
        [dbname (. parsed-args dbname)]]
    (.drop_database mc dbname)))

(defn poem-new* [parsed-args]
  (let [[template (args->template parsed-args)]
        [db (args->db parsed-args)]
        [poem-lines (poem-from-template template db)]
        [output-filename (. parsed-args output)]]
    ;; actually write poem to file if filename provided
    (if output-filename
      (with [[f (open output-filename "w")]]
            (.write f (+ (->> poem-lines
                              (map (fn [l] (.get l "raw")))
                              (.join "\n"))
                         "\n")))
      (for [line poem-lines]
        (print (.get line "raw"))))))

(defn template-ls* [parsed-args]
  (->> (listdir TEMPLATES)
       (filter (fn [s] (not (.startswith s "."))))
       (map (fn [s] (.replace s (+ "." DEFAULT-TMPL-EXT) "")))
       (map print)
       list))

(defn template-new* [parsed-args]
  (let [[tmpl-name (. parsed-args tmplname)]
        [tmpl-abspath (join TEMPLATES (+ tmpl-name "." DEFAULT-TMPL-EXT))]
        [editor (.get environ "EDITOR" "vi")]]
    (cp  EXAMPLE-TMPL tmpl-abspath)
    (call [editor tmpl-abspath])))

(defn template-edit* [parsed-args]
  (let [[tmpl-name (. parsed-args tmplname)]
        [tmpl-abspath (join TEMPLATES (+ tmpl-name "." DEFAULT-TMPL-EXT))]
        [editor (.get environ "EDITOR" "vi")]]
    (call [editor tmpl-abspath])))

(defn template-rm* [parsed-args]
  (let [[tmpl-name (. parsed-args tmplname)]
        [tmpl-abspath (join TEMPLATES (+ tmpl-name "." DEFAULT-TMPL-EXT))]]
    (rm tmpl-abspath)))

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
        [add-host-arg! (fn [ap] (add-argument! ap ["-n" "--host"]
                                               {"type" str
                                                "default" DEFAULT-HOST
                                                "action" "store"})
                         ap)]
        [add-port-arg! (fn [ap] (add-argument! ap ["-p" "--port"]
                                               {"type" int
                                                "default" DEFAULT-PORT
                                                "action" "store"})
                         ap)]
        [add-dbname-arg! (fn [ap] (add-argument! ap ["-d" "--dbname"]
                                                 {"type" str
                                                  "default" DEFAULT-DB
                                                  "action" "store"})
                           ap)]

        [add-db-args! (fn [ap] (-> ap
                                   add-host-arg!
                                   add-port-arg!
                                   add-dbname-arg!)
                        ap)]

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
        add-host-arg!
        add-port-arg!
        (add-argument! ["dbname"]
                       {"type" str
                        "default" "prosaic"
                        "action" "store"}))
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
        (add-argument! ["-o" "--output"]
                       {"action" "store"})
        (add-argument! ["-t" "--tmpl"]
                       {"type" str
                        "default" "haiku"
                        "action" "store"})
        add-db-args!)

    ;; template ls
    (-> (.add_parser template-subs "ls")
        (set-defaults! {"func" template-ls*}))

    ;; template rm
    (-> (.add_parser template-subs "rm")
        (add-argument! ["tmplname"]
                       {"action" "store"
                        "type" str})
        (set-defaults! {"func" template-rm*}))

    ;; template new
    (-> (.add_parser template-subs "new")
        (add-argument! ["tmplname"]
                       {"action" "store"
                        "type" str})
        (set-defaults! {"func" template-new*}))

    ;; template edit
    (-> (.add_parser template-subs "edit")
        (add-argument! ["tmplname"]
                       {"action" "store"
                        "type" str})
        (set-defaults! {"func" template-edit*}))

    top-level-parser))

;; Driver code
(defn main []

  (unless (installed?)
    (install!))

  (let [[argument-parser (init-arg-parser)]
        [parsed-args (.parse_args argument-parser)]]
    ((. parsed-args func) parsed-args)
    0))

(if (= __name__ "__main__")
  (.exit sys (main)))
