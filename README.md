# Playground for question of teratail

質問の直接的な答えではなく、同じことをするとしたら自分ならどうするか、を試す場所

## Environment

-   Hyper-V
-   Windows 11 Home | Enterprise
-   Python 3.11.1
-   VSCode 1.74.3
-   Poetry 1.3.2

## Dependencies

-   playwright 1.29.1
-   selenium 4.7.2

## Note

セキュリティリスクを考慮し、`selenium` で `chromedriver` を使う際は、必ず仮想マシンで実行すること

参照：[ChromeDriver - WebDriver for Chrome - Security Considerations](https://chromedriver.chromium.org/security-considerations)

## Questions

### 1. selenium 入力ボックスの要素が見つからない

URL: <https://teratail.com/questions/2ir4j74anuefal>

#### 要約

セレクターは正しいはずなのに、`NoSuchElementException` (該当する要素が見つからない) というエラーが出力される

#### 解決策

このエラーの場合、最初に思いつくのはページロードを待機していないということ。要素がまだロードされないうちに要素を取得しようとすると大体このエラーになる。

しかし、今回の場合待機時間を設定しても要素が見つからなかった。

そのため、別の要因があるはずと原因を探ったが当初は原因を特定できず、`PlayWright` を使った解決策を提示。しかし、`PlayWright` で取得できるのに、`Selenium` だと取得できない理由がわからず納得がいかなかったため、再度該当ページの HTML を調査。すると、該当の要素は `Shadow DOM` の中にあることが判明。

そこで、`Selenium` での `Shadow DOM` の扱い方を調べたところ正解にたどり着いた。

```python
# 省略

driver.get(url)

# ShadowRoot 要素を取得
shadow = driver.find_element(By.XPATH, "//dm-calculator").shadowroot

# ShadowRoot 内で要素を検索
shadow.find_element(By.CSS_SELECTOR, "vs-h2")

```

`PlayWright` だとこの手順を踏む必要がないため、原因に気付くのが遅れた。

#### Code

[visa.py](/src/visa.py)

### 2. selenium でスクレイピング。ある部分が取れない

URL: <https://teratail.com/questions/kwcuzshawbpplv>

#### 要約

1593 ページある Web サイトのページ全てを、最初のページから順にスクレイピングしていくプログラム。抽出したデータを CSV 形式でファイルに書き込む。

しかし、途中でプログラムが止まるまたは、ページを飛ばしてしまう。ページを飛ばすことなく、全てのページのデータを収集したい。

#### 解決策

プログラムがの内容を見るに、特に `selenium` である必要がなさそう。

提示されている URL を見てみると、開発者ツールのネットワークタブに API らしき通信が確認できた。レスポンスの中身は質問者が要求している値を含んでいたため、このアドレスにリクエストを投げればいいのではと思った。

`httpx` を使って `json` レスポンスを返すサーバーにリクエストを送信し、受け取ったレスポンスを CSV 形式でファイルに書き込む。

実際に実行してみると、返されるデータの値にコンマが含まれていることがわかったため、CSV ではなく TSV 形式で保存することにした。

#### Code

[kamui.py](/src/kamui.py)

### 3. Python で selenium 次のページをクリック

URL: <https://teratail.com/questions/pgd3cgpf1toqit>

#### 要約

1 つ目のページのスクレイピングが終わったら、次のページに遷移してスクレイピングを続けたい。

その際、そのページがいくつあるかが事前にはわからないため、ページ下部の「次のページ」または「ページ番号」をクリックして次のページに遷移するプログラムを書いた。

プログラム自体はエラーもなく正常に動くが、最初のページだけ 2 度スクレイピングしてしまう。

#### 解決策

原因は、初期値の設定値とループ内の条件文の位置。

初期値の有無にかかわらず初回に必ず最初のページをスクレイピングするようになっていた。ループ 2 周目も同じ個所を通ってスクレイピングしたのち、初めて条件文に突き当たり条件分岐している。

なので、単純な解決策として初期値の値を 2 にするよう提案した。

しかし、そもそも `Selenium` である必要が感じられなかったため、`httpx` と `selectolax` で書き換えてみた。該当のページはクエリでページ番号を管理でき、存在しないページ番号を指定すると 404 が返ってくることが判明した。なので、リクエストを送信してステータスコードを取得、404 が返ってきたらプログラムを終了するようにした。

#### Code

[navitime.py](/src/navitime.py)
