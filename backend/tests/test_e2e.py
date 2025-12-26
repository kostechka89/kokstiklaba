import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.e2e
def test_news_flow_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5173/")
        page.click("text=Войти")
        page.fill("input[placeholder='Email']", "author@example.com")
        page.fill("input[placeholder='Пароль']", "password")
        page.click("text=Войти")
        page.goto("http://localhost:5173/")
        page.fill("input[placeholder='Заголовок']", "E2E News")
        page.fill("textarea[placeholder='Контент']", "Hello")
        page.click("text=Создать новость")
        page.click("text=E2E News")
        page.fill("textarea", "Updated")
        page.click("text=Сохранить")
        page.click("text=Удалить")
        browser.close()
