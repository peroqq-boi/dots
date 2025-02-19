#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

source ~/.cache/wal/colors.sh


alias ls='ls --color=auto'
alias grep='grep --color=auto'

fastfetch
export PATH="$HOME/.cargo/bin:$PATH"

PS1='\[\033[01;32m\]\u\[\033[00m\] \[\033[01;34m\]\w\[\033[00m\] \[\033[01;33m\]> \[\033[00m\]'

export QT_STYLE_OVERRIDE=kvantum
export PIPEWIRE_LATENCY=64/48000
