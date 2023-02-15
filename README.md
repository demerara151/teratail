# Playground for teratail

<https://teratail.com> での質問と回答の考えをまとめ、目的に対して同じことをするとしたら自分ならどうするか、を試す場所

## Environment

-   Hyper-V
-   Windows 11 Home | Enterprise
-   Python 3.11.2
-   VSCode 1.75.1
-   Poetry 1.3.2

## Dependencies

-   playwright 1.30.0
-   selenium 4.8.0

## Note

セキュリティリスクを考慮し、`selenium` で `chromedriver` を使う際は、必ず仮想マシンで実行すること

参照：[ChromeDriver - WebDriver for Chrome - Security Considerations](https://chromedriver.chromium.org/security-considerations)

## Questions

### 1. selenium 入力ボックスの要素が見つからない

URL: <https://teratail.com/questions/2ir4j74anuefal>

#### 要約

セレクターは正しいはずなのに、`NoSuchElementException` (該当する要素が見つからない) というエラーが出力される

#### 解決策

[visa.py](/src/visa.py)

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

### 2. selenium でスクレイピング。ある部分が取れない

URL: <https://teratail.com/questions/kwcuzshawbpplv>

#### 要約

1593 ページある Web サイトのページ全てを、最初のページから順にスクレイピングしていくプログラム。抽出したデータを CSV 形式でファイルに書き込む。

しかし、途中でプログラムが止まる、または、ページを飛ばしてしまう。ページを飛ばすことなく、全てのページのデータを収集したい。

#### 解決策

[kamui.py](/src/kamui.py)

プログラムの内容を見るに、特に `selenium` である必要がなさそう。

提示されている URL を見てみると、開発者ツールのネットワークタブに API らしき通信が確認できた。レスポンスの中身は質問者が要求している値を含んでいたため、このアドレスにリクエストを投げればいいのではと思った。

`httpx` を使って `json` レスポンスを返すサーバーにリクエストを送信し、受け取ったレスポンスを CSV 形式でファイルに書き込む。

実際に実行してみると、返されるデータの値にコンマが含まれていることがわかったため、CSV ではなく TSV 形式で保存することにした。

### 3. Python で selenium 次のページをクリック

URL: <https://teratail.com/questions/pgd3cgpf1toqit>

#### 要約

1 つ目のページのスクレイピングが終わったら、次のページに遷移してスクレイピングを続けたい。

その際、そのページがいくつあるかが事前にはわからないため、ページ下部の「次のページ」または「ページ番号」をクリックして次のページに遷移するプログラムを書いた。

プログラム自体はエラーもなく正常に動くが、最初のページだけ 2 度スクレイピングしてしまう。

#### 解決策

[navitime.py](/src/navitime.py)

原因は、初期値の設定値とループ内の条件文の位置。

初期値の有無にかかわらず初回に必ず最初のページをスクレイピングするようになっていた。ループ 2 周目も同じ個所を通ってスクレイピングしたのち、初めて条件文に突き当たり条件分岐している。

なので、単純な解決策として初期値の値を 2 にするよう提案した。

しかし、そもそも `Selenium` である必要が感じられなかったため、`httpx` と `selectolax` で書き換えてみた。該当のページはクエリでページ番号を管理でき、存在しないページ番号を指定すると 404 が返ってくることが判明した。なので、リクエストを送信してステータスコードを取得、404 が返ってきたらプログラムを終了するようにした。

### 4. selenium で target 属性をクリックしてタブが遷移をしても１つ目のタブの要素がゼロにならない方法

URL: <https://teratail.com/questions/d6bl0tg488h8fd>

#### 要約

リンクをクリックすると `target` 属性に `_blank` が設定されているため、新しく出現したタブへ遷移する。

その際、元のタブで取得した要素のリストが空になってしまう。再度元のタブへ戻って取得済みの別の要素のリンクをクリックしたい。

#### 解決策

[lost_elements](/src/lost_elements.py)

まず始めに、取得した要素の長さを計って、その長さの数だけ繰り返し処理をするという原始的な手法を用いていたため、これを修正。

```python
"Example"

elements = driver.find_elements(By.XPATH, "a[@target=_blank]")
for element in elements:
    element.click()
```

上記のように、全要素のリストを変数に格納し、格納されている全ての要素に対して処理を行う `for` 文を作成。

次に、`selenium` の [ドキュメント](https://www.selenium.dev/documentation/webdriver/interactions/windows/) を読むと、最初のページのウインドウハンドルを記録しておき、遷移先の処理が終わったら元のページへ `driver.switch_to.window()` すればいいと判明。

```python
"Example"

# 最初のページのウインドウハンドルを変数に格納
original_window = driver.current_window_handle

# 新しいウインドウハンドルを見つけるまでループする
for window_handle in driver.window_handles:
    # 最初のページ以外のページがあったら遷移
    if window_handle != original_window:
        driver.switch_to.window(window_handle)

        # 遷移先で行いたい処理
        result = extract_info(driver)
        results.append(result)

        # ループを止める
        break

# 処理が終わったタブを閉じる
driver.close()

# 一番最初のタブに戻る
driver.switch_to.window(original_window)
```

#### 注意点

今回のようにタブやウィンドウを移動するコードの場合、`driver.close()` は、タブやウィンドウを閉じる処理であって、ドライバーを終了する処理ではないため、全ての処理が終わった際に `driver.quit()` をする必要がある。これを実行しないとバックグラウンドプロセスが残ったままになりメモリリークが発生する危険がある。

以下のように、`try / finally` で閉じると安全。

```python
try:
    # ページ遷移を含む処理
except Exception:
    raise
finally:
    driver.quit()
```

また、`selenium 3.1.3` からドライバーをコンテキストマネージャーで定義できるようになったため、`with` 構文を使うとより安全に終了できる。

```python
with webdriver.Chrome() as driver:
    driver.get(url)
    driver.close()
# driver.quit() は不要
# with 文を抜けると自動的に全てのドライバーのプロセスが終了する
```

## LICENSE

This project is licensed under the terms of the [MIT license](./LICENSE).
