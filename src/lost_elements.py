# type: ignore
"""
seleniumでtarget 属性をクリックしてタブが遷移をしても１つ目のタブの要素がゼロにならない方法
https://teratail.com/questions/d6bl0tg488h8fd
"""
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@dataclass(slots=True, frozen=True)
class Crawler:
    url: str

    @property
    def _driver(self) -> webdriver.Chrome:
        "chromedriver"
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        return driver

    def main(self) -> list[str]:
        """
        Click the link in the first page,
        then extract data on the new tab.
        Back to the first page and click next link.

        Loop this until the links of first page are exhausted.
        """
        with self._driver as driver:
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)

            # 最初のページのウィンドウ情報を記録しておく
            original_window = driver.current_window_handle

            results: list[str] = []

            elements = driver.find_elements(
                By.CSS_SELECTOR, "#techblog ul li a"
            )

            for element in elements:
                driver.execute_script("arguments[0].click();", element)

                # 新しいウインドウかタブが開くまで待機
                wait.until(EC.number_of_windows_to_be(2))

                # 新しいウインドウハンドルを見つけるまでループする
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        result = driver.title
                        results.append(result)
                        break

                # 抽出が終わったタブを閉じる
                driver.close()

                # サイトへの負荷軽減のため数秒待機
                time.sleep(2)

                # 一番最初のタブに戻る
                driver.switch_to.window(original_window)

            return results


if __name__ == "__main__":
    URL: str = "https://gihyo.jp/"
    crawler = Crawler(URL)
    result: list[str] = crawler.main()
    print(result)
