# TriPal
旅行プランを提案し、宿泊施設などの予約を会話形式で提供するAIサービスです


## 環境構築
### 1. リポジトリのクローン
```bash
$ git clone https://github.com/KorRyu3/TriPal
$ cd TriPal
```

### 2. 仮想環境
#### 仮想環境の作成
```bash
$ python3 -m venv .venv
```
#### 仮想環境に入る場合
##### Windows(cmd)
```bash
> .venv\Scripts\activate.bat
```
##### MacOS
```bash
$ source .venv/bin/activate
```
#### 仮想環境を抜ける場合
```bash
$ deactivate
```

### 3. パッケージのインストール
```bash
(.venv) $ pip install -r requirements.txt
```

### 4. 環境変数について
環境変数ファイルには、Azure OpenAIのAPI-KEYなどの情報が入っているため、GitHub上には上げていません。  
プログラムを動かす際は、管理者から直接ファイルを
受け取ってください。
また、受け取ったファイルは、`Web-site/backend/`直下に置いてください。

## ファイル構成(将来的)
```bash
TriPal
├── README.md
├── .gitignore
├── requirements.txt
├── .venv
│   └── ...
├── drawio
│   ├── architecture.drawio
│   ├── first_design.drawio
│   └── work-flow.drawio
└── Web-site
    ├── .env
    ├── app.py
    ├── tripalgpt.py
    ├── functools.py
    ├── templates
    │   └── index.html
    └── static
        ├── css
        │   └── style.css
        ├── img
        │   └── favicon.ico
        └── js
            └── index.js
```


## Git/GitHubでのルール


- 新しいファイルを作る場合は、空のファイルを最初にpush
- 新しいファイルを編集する場合は、必ず`git branch`で新しいbranchを作成し、そこで編集<br>
### 例１
```bash
$ git branch ブランチ名
$ git checkout ブランチ名
```
### 例2
```bash
$ git checkout -b ブランチ名
```
<br>


- ファイルを編集する場合は、必ず各ブランチで`git pull`をしてから編集  
→ これをしないと、コンフリクトが起きる可能性がある  
<br>


- `git add` は変更を加えたら逐一、`git commit` は作業の区切り目の小さな単位で行う  
[**Gitのコミットメッセージの書き方 - Qiita**](https://qiita.com/itosho/items/9565c6ad2ffc24c09364#%E9%80%9A%E5%B8%B8%E7%89%88)  
- `git push` は出来るだけ積極的に
- "Pull requests"は大きな単位の編集が完了したら行う  
<br>

- 複数のファイルをGithubにアップロードする場合は1つずつコミット  
 ↓
 
<details><summary><h3>例</h3></summary>
hoge.pyとhoge.htmlを編集し、両方commitしたい場合

#### hoge.py
```bash
git add hoge.py
git commit -m "hoge.pyについてのコメント"
git push
```  

#### hoge.html
```bash
git add hoge.html  
git commit -m "hoge.htmlについてのコメント"  
git push
```
</details>
