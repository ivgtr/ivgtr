# Mac 初期設定
- 参考:[Mac を買ったら必ずやっておきたい初期設定](https://qiita.com/ucan-lab/items/c1a12c20c878d6fb1e21)

## 最初にやること

- ソフトウェア・アップデート
  - (appleマーク) > このmacについて > ソフトウェアアップデート
- App Store
  - (appleマーク) > App Store > すべてアップデート

## シェルの確認

```
$ echo $SHELL
/bin/zsh
```

zsh でなければ
```
brew install zsh
```

### 隠しファイルを表示する

```
$ defaults write com.apple.finder AppleShowAllFiles -boolean true

# 補足: 元に戻す場合
$ defaults delete com.apple.finder AppleShowAllFiles
```

`command` + `shift` + `.` で表示/非表示の切り替えもできます。

### 共有フォルダで .DS_Store ファイルを作成しない

```
$ defaults write com.apple.desktopservices DSDontWriteNetworkStores true

# 補足: 元に戻す場合
$ defaults write com.apple.desktopservices DSDontWriteNetworkStores false
```

## 権限設定

```
$ sudo chown -R $(whoami):admin /usr/local/*
$ sudo chmod -R g+w /usr/local/*
```

Homebrewでインストールする際は /usr/local のパーミッションエラー対策。
追加されたユーザーでHomebrewを実行する時などにパーミッションエラーが起きるので予め権限設定しておく

## Homebrew

- https://brew.sh
- macOS CLI用のパッケージマネージャー
- Xcode Command Line Tools
  - Homebrewを入れるために別途必要でしたが、最近のインストーラは自動的にインストールしてくれます。

```
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

```
$ brew -v
Homebrew 2.2.11
Homebrew/homebrew-core (git revision 31624; last commit 2020-04-05)
Homebrew/homebrew-cask (git revision 9372fac; last commit 2020-04-05)
```

### Homebrew Cask

- https://github.com/Homebrew/homebrew-cask
- macOS GUI用のパッケージマネージャー
- 最近の Homebrew をインストールしていれば同梱されている

### Homebrew Update & Upgrade

```
# Homebrew本体のアップデート
$ brew update

# Homebrewでインストールしたパッケージのアップデート
$ brew upgrade
$ brew cask upgrade
```

### Homebrew 補足

- [homebrewとは何者か。仕組みについて調べてみた](https://qiita.com/omega999/items/6f65217b81ad3fffe7e6)

```
# 古いformulaを削除
$ brew cleanup

# Homebrewの診断
$ brew doctor
```

## アニメーションの削除
- [【決定版】MacOS X 高速化テクニック](https://qiita.com/soushiy/items/b56d4961d54972bc4b9e)

### Dockが表示/非表示になる時間を0.15秒にする

```
defaults write com.apple.dock autohide-time-modifier -float 0.15;killall Dock
```

### マウスを画面端に持っていってからDockが表示されるまでの待ち時間を0秒にする

```
defaults write com.apple.dock autohide-delay -float 0;killall Dock
```

## Macシステム環境設定

### 一般

- 外観モード > ダーク
- スクロールバーの表示 > 常に表示

### Dock

- サイズ: 小さめに
- Dockを自動的に表示 > 表示

### 省エネルギー

- バッテリー
  - ディスプレイをオフにするまでの時間
    - 短めに
  - バッテリー電源使用時はディスプレイを少し暗くする
    - チェックを外す
- メニューバーにバッテリーの状況を表示
  - チェックを入れる
  - メニューバーの電池マークをクリック「割合(%)を表示」にチェックを入れる

### 日付と時刻

- 時計 
  - 日付のオプション
    - 日付を表示にチェックを入れる

### トラックパッド

- クリック 
    - 弱いに

### キーボード

- キーボード 
  - Touch Barに表示する項目
    - F1、F2などのキーを表示
- ユーザ辞書 
  - 英字入力中にスペルを自動変換
    - チェックを外す
  - スペースバーを2回押してピリオドを入力
    - チェックを外す
  - スマート引用符とスマートダッシュを使用
    - チェックを外す

### セキュリティとプライバシー
- スリープとスクリーンセーバの解除にパスワードを要求
  - すぐに
- ダウンロードしたアプリケーションの実行許可
    - Mac App Store と確認済みの開発元からのアプリケーションを許可
- ファイアウォール > ファイアウォールをオン にする

### 共有

- コンピュータ名を変更(AirDropに表示される名前)
- リモートログイン > 必要になったらチェックを入れる

### Touch ID

- 登録
- Touch IDを使用 > 全部にチェックを入れる

## Finder

### デスクトップに表示させるアイコン

- 一般
  - デスクトップに表示させる項目
    - 接続中のサーバ にチェックを入れる

### ファイルの拡張子を表示する

- 環境設定
  - 詳細
    - すべてのファイル名拡張子を表示 にチェックする
    - 拡張子を変更する前に警告を表示 のチェックを外す

### AirDrop

- このMacを検出可能な相手 > 都度変える
  - 基本は`連絡先のみ`
- Bluetooth, Wi-Fiを有効にする。

## Shell
### Iceberg
- Terminalのテーマ設定
- [Iceberg-iTerm2](https://github.com/Arc0re/Iceberg-iTerm2)
- readmeを見ながらinstall

### prezto
- zshのframework
- [prezto](https://github.com/sorin-ionescu/prezto)
- readmeを見ながらinstall
  - .zshrc
    - aliasなどを設定する
  - .zpreztorc
    - modulesの部分に書き加える
```
# Set the Prezto modules to load (browse modules).
# The order matters.
zstyle ':prezto:load' pmodule \
  'environment' \
  'terminal' \
  'editor' \
  'history' \
  'directory' \
  'spectrum' \
  'utility' \
  'completion' \
  'syntax-highlighting' \
  'autosuggestions' \
  'prompt'
```

## CLI Tool
### Git

- Macに標準で入ってるらしい

```
$ brew install git
```

### anyenv

- https://github.com/anyenv/anyenv
- 様々な `**env` 系ツールをまとめて管理する

```
$ brew install anyenv
$ anyenv init
$ echo 'eval "$(anyenv init -) >> ~/.zshrc
$ exec $SHELL -l
```

### anyenv-update
- https://github.com/znz/anyenv-update
- `**env` 系ツールを一括アップデートするプラグイン

```
$ mkdir -p $(anyenv root)/plugins
$ git clone https://github.com/znz/anyenv-update.git $(anyenv root)/plugins/anyenv-update
```

### anyenv-git

- https://github.com/znz/anyenv-git


### nodenv

- https://github.com/nodenv/nodenv
- 複数のNode.jsのバージョンを管理する
- ローカルでのバージョンの切り替えが楽

```
$ anyenv install nodenv
$ exec $SHELL -l
```

### pyenv

- 複数のPythonのバージョンを管理する

```
$ anyenv install pyenv
$ exec $SHELL -l
```

### gibo

- .gitignore作成の補助

```
$ brew install gibo
```

### jq

- json整形

```
$ brew install jq
```

### npm

- デフォルトでinstall されてそう
```
$ brew install npm
```

### yarn

- 個人開発は基本的にyarnを使う
- `--ignore-dependencies`をつけておくと、複数nodeの依存関係を無視させることができる。

```
brew install yarn --ignore-dependencies
```

### GUI tool
### Visual Studio Code

- エディター

```
$ brew cask install visual-studio-code
```

- install 後にsetting sync で設定をダウンロード
- id/token はbitwarden で管理
- [VScodeの設定共有（SettingSync）](https://qiita.com/torun225/items/e6823fc22e5ae79247fe)

### Chrome

- ブラウザ
- https://www.google.com/intl/ja_jp/chrome

```
$ brew cask install google-chrome
```

### Postman

- API開発のためのコラボレーションプラットフォーム
- https://www.postman.com/postman

```
$ brew cask install postman
```

### Docker for Mac

- コンテナ仮想化プラットフォーム
- https://docs.docker.com

```
$ brew cask install docker
```

### Slack

- https://slack.com/intl/ja-jp

```
$ brew cask install slack
```

### bitwarden

- https://bitwarden.com/
- パスワードマネージャー
- brew でinstall する必要はない

```
$ brew cask install bitwarden
```

## NPM Package

- global package は基本npm (深い意味は無い)
- 基本`npx **`で呼べばいいのでよっぽど頻繁に使うもの以外はinstall しない

### gitmoji-cli

- 個人開発のcommit は基本絵文字をつける
  - 見栄えがいいので

```
npm install -g gitmoji-cli
```

## ssh設定

- `ssh-keygen`で鍵を作り、github に登録

