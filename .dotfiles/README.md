# Mac 初期設定
クリーンインストールの手順は[macOS Catalinaをクリーンインストールする方法](https://qiita.com/PaSeRi/items/59e9785580dbd518ac93)を参考にした  
PCスペック:MacBook Air (Retina, 13-inch, 2018), メモリ16GB, SSD 256GB, JIS  

#### クリーンインストール後、ひとまずソフトウェア・アップデート
- `(appleマーク) > このmacについて > ソフトウェアアップデート`  

`homebrew`をインストールしようとしたら`xcode`が必要だったのでダウンロード、  
App storeの`xcode`は不要っぽい(?)のでターミナルより`xcode-select --install`でinstall
そして`homebrew`のinstall:  
```sh
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```
権限設定:  
```sh
$ sudo chown -R $(whoami):admin /usr/local/*
$ sudo chmod -R g+w /usr/local/*
```


#### ここら辺でターミナルの入力しにくさに不快感を覚えるので`zsh`をinstallしていく
```sh
$ brew install zsh
$ sudo echo '/usr/local/bin/zsh' >>  /etc/shells
$ chsh -s /usr/local/bin/zsh
```
ターミナルを再起動、`echo $SHELL`でPATHが`zsh`に向いてるか確認  
起動時に.zshrcがないよ的な事を聞かれるので適当に答える、後述の`zprezto`導入時に存在するとコマンドが通らないのでどうせ消す  
  
#### `zsh`を機能拡張したいので`zprezto`を導入する
```
$ git clone --recursive https://github.com/sorin-ionescu/prezto.git "${ZDOTDIR:-$HOME}/.zprezto"
```
gitを使っているがデフォルトで入っているはず、入っていなかったら`brew install git`  
設定ファイルを生成するコマンドを入力(*最初の一行目だけではなく全部入力)  
```sh
$ setopt EXTENDED_GLOB
for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
  ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
done
```
これで`.zshrc`などが生成される  
`exec $SHELL -l`でターミナルを再起動、コマンドラインの見た目が三本線のカラフルな感じになってたら成功  
##### modulesを追加する為に`.zpreztorc`を編集  
modulesっぽいのがズラッと並んでいる所を探し、`'syntax-highlighting`と`'autosuggestions`を追加する  
```rc:.zpreztorc
zstyle ':prezto:load' pmodule \
  'environment' \
  'terminal' \
  'editor' \
  'history' \
  'directory' \
  'spectrum' \
  'utility' \
  'completion' \
  'syntax-highlighting' \  # 追加した
  'autosuggestions' \      # 追加した
  'prompt'
```
  
`exec $SHELL -l`でターミナルを再起動、コマンドが存在するかで色が付いたりhistoryからコマンドを教えてくれたりする  

#### 必要そうなGUIツールをinstallする
- `homebrew`のアップデートでcaskのインストールコマンドが変わってるので注意
  - 従来は`brew cask install ○○`だったが、`brew install --cask ○○`になった
  - 割と最近のアップデートらしい

`brew install --cask visual-studio-code`でVSCodeをinstall  
`brew install --cask google-chrome`でChromeをinstall  
`brew install --cask bitwarden`でbitwardenをinstall(利用している場合)  

#### VSCodeをセットアップ
設定を同期、自分は拡張機能の`Settings Sync`を使って設定をimportした  
- 最近VSCodeの公式で[Settings Sync](https://code.visualstudio.com/docs/editor/settings-sync)が出たらしいのでこっちを使うべき
  - GistやTokenを用意する必要もなくGithubアカウントで共有できるっぽい

#### ターミナルを使いたくないので`hyper`を使いたい
`brew install --cask hyper`でinstall  
`hyper`の設定を弄る、  
上記メニューより`Hyper > Preferences`を選択し、`.hyper.js`を編集する(多分VSCodeで開かれる)  
日本語が文字化けする可能性があるので`env`を指定  

```js:hyper.js
env: {
  LANG: "ja_JP.UTF-8",
  LC_ALL: "ja_JP.UTF-8"
}
```

環境によるかもしれないが、一行目に`%`が表示される場合は、`.zshrc`に`unsetopt PROMPT_SP`を記述して消す  
##### `plugins`にinstallしたい物を記述(*`hyper i ○○`でもいい)  
自分の場合、下記を追加  

```js:hyper.js
plugins: [
  "hyper-statusline",
  "hyper-search",
  "hyper-opacity",
  "hyper-tab-icons-plus",
  "hyper-iceberg"
]
```
`config`内にopacityを指定(オタクは半透明が好き)  

```js:hyper.js
config: {
  opacity: 0.9
}
```
テーマはicebergを使うが、そのうち自作する  
`hyper-tab-icons-plus`の設定の為に`.zshrc`を編集する  
```sh
title() { export TITLE_OVERRIDDEN=1; echo -en "\e]0;$*\a"}
autotitle() { export TITLE_OVERRIDDEN=0 }; autotitle
overridden() { [[ $TITLE_OVERRIDDEN == 1 ]]; }
gitDirty() { [[ $(git status 2> /dev/null | grep -o '\w\+' | tail -n1) != ("clean"|"") ]] && echo "*" }
 
precmd() {
   pwd=$(pwd)
   cwd=${pwd##*/}
   print -Pn "\e]0;$cwd\a"
}
 
preexec() {
   printf "\033]0;%s\a" "${1%% *} | $cwd"
}
```
上記を追記、hyperを再起動すると反映される  
ただこのパッケージも最終更新が３年前だったりするので変えたい  
  
#### 忘れていたMacbook自体の設定をしていく(好みの問題でもある)
##### コマンドからしか設定できないやつ　
- 隠しファイルを表示  
  - `defaults write com.apple.finder AppleShowAllFiles -boolean true`
- 共有フォルダで .DS_Store ファイルを作成しない  
  - `defaults write com.apple.desktopservices DSDontWriteNetworkStores true`
- Dockが表示/非表示になる時間を0.15秒にする  
  - `defaults write com.apple.dock autohide-time-modifier -float 0.15;killall Dock`
- マウスを画面端に持っていってからDockが表示されるまでの待ち時間を0秒にする  
  - `defaults write com.apple.dock autohide-delay -float 0;killall Dock`
  
##### その他の細かい設定  
  
ここら辺に書く  
  
#### `nodenv`や`pyenv`を使う為に`anyenv`をinstallする  
`brew install anyenv`でinstall  
`anyenv init`をし、pathを通すのに`.zshrc`に追記  
```sh
if [ -e "$HOME/.anyenv" ]
then
    export ANYENV_ROOT="$HOME/.anyenv"
    export PATH="$ANYENV_ROOT/bin:$PATH"
    if command -v anyenv 1>/dev/null 2>&1
    then
        eval "$(anyenv init -)"
    fi
fi
```
`exec $SHELL -l`後に、`anyenv -v`でバージョンが出るか確認  
pluguinsをinstallしていく為にフォルダを作る  
```sh
$ mkdir -p $(anyenv root)/plugins
```
anyenv-updateをinstall  
```sh
$ git clone https://github.com/znz/anyenv-git.git $(anyenv root)/plugins/anyenv-git
```
anyenv-gitをinstall  
```sh
$ it clone https://github.com/znz/anyenv-git.git $(anyenv root)/plugins/anyenv-git
```
使い方は調べよう  
  
##### `nodenv`をinstallする  
`anyenv install nodenv`でinstall、`exec $SHELL -l`、`nodenv -v`で確認  
pluguinsをinstallしていく為にフォルダを作る  
```sh
$ mkdir -p "$(nodenv root)/plugins"
```
nodenv-default-packages  
```sh
$ git clone https://github.com/nodenv/nodenv-default-packages.git "$(nodenv root)/plugins/nodenv-default-packages"
```
`touch $(nodenv root)/default-packages`でファイルを作成  
```default-packages
yarn
vercel
gitmoji-cli
```
こんな感じに`default-packages`にパッケージ名を書くことで`nodenv`で新しいバージョンの`node`をinstallする際にそのパッケージもinstallしてくれる  
基本npxでinstallしなくていいから何をinstallすればいいか思いつかない  
既に追加しているバージョンにもinstallしたいときは  
`nodenv default-packages install <version>`でできる、全てにinstallしたいときは`--all`  
`Node.js`の最新の推奨版である14.15.3をinstallし、設定  
```sh
$ nodenv install 14.15.3
$ nodenv global 14.15.3
```
`nodenv install -l`でinstall可能なバージョンを確認できる  
`nodenv local <version>`でディレクトリ内で利用するnodeのバージョンを選択できる  
  
##### `pyenv`をinstallする  
`anyenv install pyenv`でinstall、`exec $SHELL -l`、`pyenv -v`で確認  
Pythonはバージョンを頻繁に変えることになりそう、とりあえず3.7.9をいれる  
```sh
$ pyenv install 3.7.9
$ pyenv grobal 3.7.9
```
`pyenv install -l`でinstall可能なバージョンを確認できる  
`pyenv local <version>`でディレクトリ内で利用するpythonのバージョンを選択できる  
  
#### 使いそうなツールをinstall  
##### 使いそうなCLIツールをinstall  
- gibo
  - .gitignore作成の補助
  - `brew install gibo`
- jq
  - json整形
  - `brew install jq`
- curl
  - HTTPリクエスト
  - `brew install curl`
- ngrok
  - local環境の外部公開
  - `brew install ngrok`

##### そのうち使いそうなGUIツールをinstall
- Docker for Mac
  - あれ
  - `brew install --cask docker`
- Slack
  - あれ
  - `brew install --cask slack`

#### ariasの設定をする
```sh
alias n='npm'
alias nr='npm run'
alias y='yarn'
 
alias p='python'
 
alias gitignore="touch .gitignore && gibo dump Node VisualStudioCode macOS >> .gitignore"
alias g='git'
alias gc='gitmoji -c'
alias gp='git push'
 
alias d='docker-compose'
 
alias c='code'
alias o="open"
alias www='open "/Applications/Google Chrome.app" --args --enable-xss-auditor'
alias s="source"
alias v="vim"
```
