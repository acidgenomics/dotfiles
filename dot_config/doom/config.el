;;; $DOOMDIR/config.el -*- lexical-binding: t; -*-

(setq doom-font (font-spec :family "JetBrainsMono NF" :size 16))
(setq doom-theme 'doom-dracula)
;; > (setq doom-theme 'doom-nord)
;; Can use 'doom-nord-light' for light theme.
;; > (setq doom-theme 'doom-nord-light)

(setq display-line-numbers-type t)
(setq make-backup-files nil)
(setq org-directory "~/org/")

;; ESS / R configuration.
(setq
 ;; > inferior-R-program-name "/opt/koopa/bin/R"
 ess-ask-for-ess-directory nil
 ess-default-style 'DEFAULT
 ess-eval-visibly-p nil
 ess-fancy-comments nil
 ess-history-file nil
 ess-indent-level 4
 ess-indent-with-fancy-comments nil
 ess-language "R"
 ess-nuke-trailing-whitespace-p t
 ess-roxy-str "#'"
 inferior-R-args "--no-restore --no-save")

;; Start Doom maximized.
;; https://github.com/hlissner/doom-emacs/issues/397
(add-to-list 'initial-frame-alist '(fullscreen . maximized))
