#!/bin/zsh

set -euo pipefail

if [[ "$#" -ne 3 ]]; then
  echo "usage: $0 <session> <url> <output>" >&2
  exit 1
fi

session="$1"
url="$2"
output="$3"

agent-browser --session "$session" open "$url" >/dev/null
agent-browser --session "$session" set viewport 1200 900 >/dev/null
agent-browser --session "$session" wait 800 >/dev/null
agent-browser --session "$session" eval '
  const selectors = [
    ".layer-ui__wrapper",
    ".App-menu_top",
    ".disable-zen-mode",
    ".main-menu-trigger",
    ".App-toolbar__extra-tools-trigger",
    ".collab-button",
    ".help-icon"
  ];
  for (const selector of selectors) {
    document.querySelectorAll(selector).forEach((el) => {
      el.style.display = "none";
    });
  }
  document.body.style.background = "white";
  document.documentElement.style.background = "white";
  "ok";
' >/dev/null
agent-browser --session "$session" wait 300 >/dev/null
agent-browser --session "$session" screenshot "$output" >/dev/null
agent-browser --session "$session" close >/dev/null
