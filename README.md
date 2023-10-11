# TriPal
旅行プランを提案し、宿泊施設などの予約を会話形式で提供するAIサービスです


## 環境構築
### 1. リポジトリのクローン
```
$ git clone https://github.com/KorRyu3/TriPal
```

### 2. 仮想環境の作成
```
$ python3 -m venv .venv

# 仮想環境に入る場合
$ source .venv/bin/activate

# 仮想環境を抜ける場合
$ deactivate
```

### 3. パッケージのインストール
```
$ pip install -r requirements.txt
```

### 4. 環境変数について
環境変数ファイルには、Azure OpenAIのAPI-KEYなどの情報が入っているため、GitHub上には上げていません。  
プログラムを動かす際は、管理者から直接ファイルを
受け取ってください。
また、受け取ったファイルは、`Web-site/`直下に置いてください。

## Git/GitHubでのルール


- 新しいファイルを作る場合は、空のファイルを最初にpush
- 新しいファイルを編集する場合は、必ずgit branchで新しいbranchを作成し、そこで編集<br>
```
git branch ブランチ名
git checkout ブランチ名
```
<br>


- ファイルを編集する場合は、必ずmainブランチでgit pullをしてから編集
- これをしないと、コンフリクトが起きる可能性がある  
<br>


- "git add" は変更を加えたら逐一、"git commit" は作業の区切り目の小さな単位で行う  
[**Gitのコミットメッセージの書き方 - Qiita**](https://qiita.com/itosho/items/9565c6ad2ffc24c09364#%E9%80%9A%E5%B8%B8%E7%89%88)  
- "git push" は出来るだけ積極的に
- "pull request" は大きな単位の編集が完了したら行う  
<br>

- 複数のファイルをGithubにアップロードする場合は1つずつコミット
 ↓
 
<details><summary><h3>例</h3></summary>
hoge.pyとhoge.htmlを編集し、両方commitしたい場合

git add hoge.py  
git commit -m "hoge.pyについてのコメント"  
git push  

git add hoge.html  
git commit -m "hoge.htmlについてのコメント"  
git push  
</details>
