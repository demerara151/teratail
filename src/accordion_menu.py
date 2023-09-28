# CSpell: disable
# type: ignore
"""
seleniumで、アコーディオンメニューをクリックしたい
https://teratail.com/questions/2fb5q29cd3ayee
"""
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# ロードを待機するので time.sleep() ではなく implicitly_wait() を使う
driver.implicitly_wait(5)

driver.maximize_window()
driver.get("https://www.bring-flower.com/blog/accordion-menu/")

# 最初の iframe を取得（埋め込まれた Code Pen の HTML）
frame_1 = driver.find_element(By.ID, "#cp_embed_JjMbEXY")

# 最初の iframe に切り替え
driver.switch_to.frame(frame_1)

# 切り替えた先の HTML 内にある実行結果の iframe を取得（Code Pen で 実行された結果のウィンドウ）
frame_2 = driver.find_element(By.ID, "result-iframe")

# 再度 iframe を切り替え
driver.switch_to.frame(frame_2)

# 要素が見つかる
button = driver.find_element(By.XPATH, "/html/body/ul[1]/li[1]/button")
button.click()

# 元のフレームに戻す
driver.switch_to.default_content()

driver.quit()
