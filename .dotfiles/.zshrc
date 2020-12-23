# PATH
# Preztoの読み込み
if [[ -s "${ZDOTDIR:-$HOME}/.zprezto/init.zsh" ]]; then
  source "${ZDOTDIR:-$HOME}/.zprezto/init.zsh"
fi

#anyenvの読み込み
if [ -e "$HOME/.anyenv" ]
then
    export ANYENV_ROOT="$HOME/.anyenv"
    export PATH="$ANYENV_ROOT/bin:$PATH"
    if command -v anyenv 1>/dev/null 2>&1
    then
        eval "$(anyenv init -)"
    fi
fi

unsetopt PROMPT_SP

# npm
alias n='npm'
alias nls='npm ls -g --depth=0'
alias y='yarn'
alias y add -g='npm i -g'

# git
alias gitignore="touch .gitignore && gibo dump Node VisualStudioCode macOS >> .gitignore"
alias g='git'
alias gmc='gitmoji -c'
alias gp='git push'
alias gre='git reset --soft'

# docker
alias d='docker-compose'
alias dup='docker-compose up -d --build'

# global
alias c='code'
alias o="open"
alias s="source"
alias v="vim"