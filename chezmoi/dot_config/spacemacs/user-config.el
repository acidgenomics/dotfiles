;; -*- mode: emacs-lisp; lexical-binding: t -*-

;; Additional configuration for dotspacemacs/user-config.
;; Updated 2022-02-25.

(setq-default
 fci-rule-color "#FFB86C"
 fill-column 80
 show-paren-delay 0
 standard-indent 4
 tab-width 4
 tramp-default-method "ssh"
 )

;; Make HOME and END keys work like Vim, moving to start/end of line.
;; See also:
;; - https://stackoverflow.com/questions/4614150
;; - https://superuser.com/questions/710358
(global-set-key (kbd "<home>") 'beginning-of-line)
(global-set-key (kbd "<select>") 'end-of-line)

;; See matching pairs of parentheses and other characters.
(show-paren-mode 1)

;; Fix for mouse mode with Magic Trackpad on macOS.
;; https://github.com/syl20bnr/spacemacs/issues/4591
(xterm-mouse-mode -1)

;; Use polymodes for R Markdown and RONN files.
;; https://polymode.github.io/installation/
;; https://github.com/polymode/poly-R
(add-to-list 'auto-mode-alist '("\\.Rmd$" . poly-markdown+R-mode))
(add-to-list 'auto-mode-alist '("\\.ronn$" . poly-markdown-mode))
