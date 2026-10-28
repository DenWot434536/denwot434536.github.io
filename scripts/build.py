#!/usr/bin/env python3
"""Build the static recipe site using only the Python standard library."""

from datetime import date
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://denwot434536.github.io"
RECIPES = json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))

CATEGORIES = [
    ("breakfast", "Завтраки", "sun", "Начать день вкусно"),
    ("lunch", "Обеды", "soup", "Пауза среди дня"),
    ("dinner", "Ужины", "plate", "Собраться за столом"),
    ("salads", "Салаты", "leaf", "Свежие идеи"),
    ("baking", "Выпечка", "whisk", "Для уютных вечеров"),
]

ICONS = {
    "arrow": '<path d="M4 12h16M14 6l6 6-6 6"/>',
    "up-right": '<path d="M7 17 17 7M7 7h10v10"/>',
    "search": '<circle cx="10.8" cy="10.8" r="6.2"/><path d="m15.5 15.5 4.2 4.2"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    "users": '<path d="M16 20v-1a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v1M10.5 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM16.5 5a3.5 3.5 0 0 1 0 6.8M19 20v-1a4 4 0 0 0-2-3.5"/>',
    "menu": '<path d="M4 8h16M4 16h16"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "soup": '<path d="M4 12h16a8 8 0 0 1-16 0ZM6 21h12M9 3c-2 2 2 2 0 4M14 3c-2 2 2 2 0 4"/>',
    "plate": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="5"/><path d="M3 3v5M21 3v5"/>',
    "leaf": '<path d="M20 4c-8 0-14 3-14 10a5 5 0 0 0 5 5c7 0 10-6 9-15ZM4 21c3-4 6-7 11-10"/>',
    "whisk": '<path d="m8 16-5 5M8 16c-2-2-1-5 2-8 3-3 7-4 9-2s1 6-2 9c-3 3-7 4-9 1ZM8 16c1 1 4-1 7-4s5-6 4-7M8 16c-1-1 1-4 4-7s6-5 7-4"/>',
    "print": '<path d="M6 9V4h12v5M6 17H4V9h16v8h-2M7 14h10v6H7zM17 11h.01"/>',
    "sparkle": '<path d="M12 2c.6 5.5 2.5 7.4 8 8-5.5.6-7.4 2.5-8 8-.6-5.5-2.5-7.4-8-8 5.5-.6 7.4-2.5 8-8ZM19 17c.2 2 1 2.8 3 3-2 .2-2.8 1-3 3-.2-2-1-2.8-3-3 2-.2 2.8-1 3-3Z"/>',
}


def e(value):
    return escape(str(value), quote=True)


def icon(name, class_name="icon"):
    return f'<svg class="{e(class_name)}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def brand(prefix=""):
    return f'''<a class="brand" href="{prefix}index.html" aria-label="Ложка — на главную">
      <span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 38 38" fill="none"><circle cx="19" cy="19" r="18"/><path d="M15 8c-3.1 0-5.2 3.3-5.2 6.3 0 2.9 1.6 4.3 3.7 4.8L12.8 29c-.1 1.4 1 2.3 2.2 2.3s2.3-.9 2.2-2.3l-.7-9.9c2.1-.5 3.7-1.9 3.7-4.8C20.2 11.3 18.1 8 15 8ZM24 10v20M21.5 10v6.5c0 1.6 1 2.5 2.5 2.5s2.5-.9 2.5-2.5V10" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span class="brand-copy"><strong>ложка<span class="brand-dot">.</span></strong><small>рецепты для жизни</small></span>
    </a>'''


def header(prefix=""):
    return f'''<a class="skip-link" href="#main">Перейти к содержанию</a>
    <div class="announcement"><div class="shell announcement-inner"><span>ПРОСТЫЕ РЕЦЕПТЫ · ХОРОШИЕ МОМЕНТЫ</span><span>ВКУСНО БЫТЬ ДОМА {icon("sparkle")}</span></div></div>
    <header class="site-header"><div class="shell header-inner">
      {brand(prefix)}
      <button class="menu-toggle" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="site-nav">{icon("menu")}</button>
      <nav class="site-nav" id="site-nav" aria-label="Основная навигация">
        <a href="{prefix}index.html#recipes">Рецепты</a><a href="{prefix}index.html#categories">По категориям</a><a href="{prefix}about.html">О проекте</a>
      </nav>
      <a class="header-search" href="{prefix}index.html#recipes">{icon("search")} <span>Что приготовить?</span></a>
    </div></header>'''


def footer(prefix=""):
    return f'''<footer class="site-footer"><div class="shell">
      <div class="footer-main"><div class="footer-brand">{brand(prefix)}<p>Простая еда, красивые моменты<br>и немного вдохновения на каждый день.</p></div>
      <div class="footer-links"><div><span class="footer-label">НАВИГАЦИЯ</span><a href="{prefix}index.html#recipes">Все рецепты</a><a href="{prefix}index.html#categories">Категории</a><a href="{prefix}about.html">О проекте</a></div>
      <div><span class="footer-label">ПОЛЕЗНОЕ</span><a href="{prefix}privacy.html">Конфиденциальность</a><a href="https://github.com/DenWot434536/denwot434536.github.io/issues" target="_blank" rel="noopener noreferrer">Связаться с нами {icon("up-right")}</a></div></div>
      <div class="footer-note"><span class="footer-sun">✳</span><span>ГОТОВЬТЕ<br>В СВОЁ УДОВОЛЬСТВИЕ</span></div></div>
      <div class="footer-bottom"><span>© {date.today().year} Ложка. Сделано с теплом.</span><span>ВСТРЕТИМСЯ ЗА СТОЛОМ ♡</span></div>
    </div></footer>'''


def page(title, description, content, *, prefix="", path="/", image="assets/images/hero-pasta.jpg", structured=None):
    canonical = BASE_URL + path
    ld = ""
    if structured:
        ld = '<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace("</", "<\\/") + '</script>'
    return f'''<!doctype html>
<html lang="ru" class="no-js">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title><meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#f9f7f0"><link rel="canonical" href="{e(canonical)}">
  <meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="Ложка">
  <meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}"><meta property="og:image" content="{e(BASE_URL + '/' + image)}">
  <meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}assets/css/styles.css">
  <script>document.documentElement.classList.replace('no-js','js');</script>
  <script src="{prefix}assets/js/main.js" defer></script>{ld}
</head>
<body>{header(prefix)}
<main id="main">{content}</main>
{footer(prefix)}
</body></html>'''


def serving_label(n):
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} порция"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f"{n} порции"
    return f"{n} порций"


def recipe_card(recipe, prefix=""):
    search_text = " ".join([recipe["title"], recipe["description"], recipe["category"], *recipe["ingredients"]])
    categories = " ".join(recipe["categories"])
    return f'''<article class="recipe-card" data-recipe-card data-categories="{e(categories)}" data-search="{e(search_text)}">
      <a class="recipe-card-link" href="{prefix}recipes/{e(recipe['slug'])}.html">
        <div class="recipe-image"><img src="{prefix}assets/images/{e(recipe['image'])}" alt="{e(recipe['image_alt'])}" loading="lazy" width="928" height="1152"><span class="image-badge">{e(recipe['category'])}</span><span class="image-arrow" aria-hidden="true">{icon("up-right")}</span></div>
        <div class="recipe-card-body"><div class="card-meta"><span>{icon("clock")} {recipe['minutes']} МИН</span><span class="meta-dot"></span><span>{e(serving_label(recipe['servings']).upper())}</span></div>
        <h3>{e(recipe['title'])}</h3><p>{e(recipe['description'])}</p><span class="card-read">СМОТРЕТЬ РЕЦЕПТ {icon("arrow")}</span></div>
      </a></article>'''


def home():
    categories = "".join(f'''<a class="category-tile category-{ident}" href="index.html?category={ident}#recipes" data-category-link="{ident}"><span class="category-icon">{icon(symbol)}</span><span class="category-text"><strong>{e(name)}</strong><small>{e(detail)}</small></span>{icon("up-right", "category-arrow icon")}</a>''' for ident, name, symbol, detail in CATEGORIES)
    filters = [('all', 'Все рецепты'), *[(item[0], item[1]) for item in CATEGORIES], ('quick', 'До 30 минут')]
    buttons = "".join(f'<button type="button" class="filter-button{" is-active" if ident == "all" else ""}" data-filter="{ident}" aria-pressed="{"true" if ident == "all" else "false"}">{e(name)}</button>' for ident, name in filters)
    cards = "\n".join(recipe_card(r) for r in RECIPES)
    content = f'''
    <section class="hero shell" aria-labelledby="hero-title">
      <div class="hero-copy"><div class="eyebrow"><span></span> КУХНЯ, В КОТОРУЮ ХОЧЕТСЯ ВЕРНУТЬСЯ</div>
        <h1 id="hero-title">Счастье —<br>в <em>простых</em><br>вещах.</h1>
        <p class="hero-description">Вкусные рецепты для обычных дней, неспешных завтраков и тёплых встреч за столом.</p>
        <div class="hero-actions"><a class="button button-dark" href="#recipes">Найти рецепт {icon("arrow")}</a><a class="text-link" href="about.html">Немного о нас {icon("up-right")}</a></div>
        <div class="hero-caption"><span class="caption-flower">✳</span><span>ГОТОВИМ ПРОСТО.<br>ЖИВЁМ СО ВКУСОМ.</span></div>
      </div>
      <div class="hero-media"><img src="assets/images/hero-pasta.jpg" alt="Паста с томатами и базиликом на уютном столе" width="1264" height="848" fetchpriority="high">
        <div class="hero-image-label">ВКУСНЫЕ ИДЕИ <span>№ 01</span></div>
        <a class="hero-recipe" href="recipes/pasta-s-tomatami.html"><span class="hero-recipe-kicker">ИДЕЯ НА УЖИН <span>·</span> 25 МИН</span><strong>Паста с томатами<br>и базиликом</strong><span class="hero-recipe-arrow">{icon("arrow")}</span></a>
      </div>
    </section>
    <section class="categories shell section-space" id="categories" aria-labelledby="categories-title">
      <div class="section-topline"><div><div class="eyebrow"><span></span> НАЙДИТЕ СВОЁ НАСТРОЕНИЕ</div><h2 id="categories-title">Что приготовим?</h2></div><p>Немного вдохновения<br>для каждого момента.</p></div>
      <div class="category-grid">{categories}</div>
    </section>
    <section class="recipe-section section-space" id="recipes" aria-labelledby="recipes-title"><div class="shell">
      <div class="recipe-heading"><div><div class="eyebrow"><span></span> НА КАЖДЫЙ ДЕНЬ</div><h2 id="recipes-title">Рецепты, к которым<br><em>хочется возвращаться.</em></h2></div><p>Понятные ингредиенты, немного времени и много поводов собраться вместе.</p></div>
      <div class="recipe-tools"><div class="filter-list" aria-label="Категории рецептов">{buttons}</div><label class="search-field"><span class="visually-hidden">Поиск рецепта или ингредиента</span>{icon("search")}<input id="recipe-search" type="search" placeholder="Рецепт или ингредиент" autocomplete="off"></label></div>
      <div class="results-line"><p data-results-count aria-live="polite">{len(RECIPES)} рецептов</p><span>ВЫБИРАЙТЕ С ЛЮБОВЬЮ ✳</span></div>
      <div class="recipe-grid" data-recipe-grid>{cards}</div>
      <div class="no-results" data-no-results hidden><span>✳</span><h3>Ничего не нашлось</h3><p>Попробуйте другое название, ингредиент или категорию.</p><button type="button" class="button button-outline" data-clear-filters>Показать все рецепты {icon("arrow")}</button></div>
      <noscript><p class="noscript-note">Для поиска и фильтрации включите JavaScript. Все рецепты доступны выше.</p></noscript>
    </div></section>
    <section class="about-strip shell section-space"><div class="about-strip-inner"><div class="about-strip-copy"><div class="eyebrow light"><span></span> НАША МАЛЕНЬКАЯ ФИЛОСОФИЯ</div><h2>Неидеально.<br><em>Зато по-настоящему.</em></h2><p>Здесь не нужно быть шефом. Достаточно пары хороших продуктов, любимой тарелки и желания приготовить что-то для себя и близких.</p><a class="button button-light" href="about.html">О проекте {icon("arrow")}</a></div><div class="about-strip-image"><img src="assets/images/apples.jpg" alt="Домашняя яблочная галета на столе" loading="lazy" width="928" height="1152"><span>МАЛЕНЬКИЕ РАДОСТИ<br>КАЖДОГО ДНЯ ✳</span></div></div></section>
    '''
    structured = {"@context": "https://schema.org", "@type": "WebSite", "name": "Ложка", "url": BASE_URL + "/", "inLanguage": "ru-RU", "description": "Простые домашние рецепты на каждый день."}
    return page("Ложка — домашние рецепты на каждый день", "Простые рецепты для завтрака, обеда и ужина. Готовьте дома с удовольствием и находите новые идеи для каждого дня.", content, structured=structured)


def recipe_page(recipe, next_recipe):
    ingredients = "".join(f'<li><label><input type="checkbox"><span>{e(item)}</span></label></li>' for item in recipe["ingredients"])
    steps = "".join(f'<li><span class="step-number">{i:02d}</span><p>{e(step)}</p></li>' for i, step in enumerate(recipe["steps"], 1))
    content = f'''
    <article class="recipe-detail shell"><div class="breadcrumbs"><a href="../index.html">Главная</a><span>/</span><a href="../index.html#recipes">Рецепты</a><span>/</span><span>{e(recipe['title'])}</span></div>
      <div class="detail-intro"><div class="detail-copy"><div class="eyebrow"><span></span> {e(recipe['category'].upper())} · ДОМАШНЯЯ КУХНЯ</div><h1>{e(recipe['title'])}</h1><p>{e(recipe['description'])}</p><div class="detail-meta"><span>{icon("clock")} <span><small>ВРЕМЯ</small><strong>{recipe['minutes']} минут</strong></span></span><span>{icon("users")} <span><small>КОЛИЧЕСТВО</small><strong>{e(serving_label(recipe['servings']))}</strong></span></span></div><button class="print-button" type="button" data-print>{icon("print")} Распечатать рецепт</button></div><div class="detail-image"><img src="../assets/images/{e(recipe['image'])}" alt="{e(recipe['image_alt'])}" width="928" height="1152"><span>ПРИЯТНОГО АППЕТИТА ✳</span></div></div>
      <div class="recipe-content"><aside class="ingredients-card"><span class="ingredients-kicker">ВСЁ, ЧТО ПОНАДОБИТСЯ</span><h2>Ингредиенты</h2><p>На {e(serving_label(recipe['servings']))}</p><ul>{ingredients}</ul><p class="ingredients-hint">Отмечайте то, что уже подготовили.</p></aside>
      <div class="directions"><div class="eyebrow"><span></span> ГОТОВИМ ВМЕСТЕ</div><h2>Приготовление</h2><p class="recipe-intro">{e(recipe['intro'])}</p><ol class="steps">{steps}</ol><div class="tip-box"><span class="tip-icon">✳</span><div><strong>Небольшой совет</strong><p>{e(recipe['tip'])}</p></div></div><p class="photo-note">Иллюстрация создана с помощью ИИ и может отличаться от результата. Рецепт подготовлен с помощью ИИ; учитывайте особенности продуктов и проверяйте готовность блюда.</p></div></div>
      <div class="detail-bottom"><div><span>ЕСТЬ ЕЩЁ ИДЕЯ</span><h2>А что дальше?</h2></div><a href="{e(next_recipe['slug'])}.html"><span>ПОПРОБУЙТЕ ТАКЖЕ</span><strong>{e(next_recipe['title'])}</strong>{icon("arrow")}</a></div>
    </article>'''
    path = f"/recipes/{recipe['slug']}.html"
    structured = {"@context": "https://schema.org", "@type": "Recipe", "name": recipe["title"], "description": recipe["description"], "image": [BASE_URL + "/assets/images/" + recipe["image"]], "totalTime": f"PT{recipe['minutes']}M", "recipeYield": serving_label(recipe["servings"]), "recipeCategory": recipe["category"], "recipeIngredient": recipe["ingredients"], "recipeInstructions": [{"@type": "HowToStep", "text": step} for step in recipe["steps"]], "inLanguage": "ru-RU", "url": BASE_URL + path}
    return page(recipe["title"] + " — Ложка", recipe["description"], content, prefix="../", path=path, image="assets/images/" + recipe["image"], structured=structured)


def about_page():
    content = f'''<section class="simple-page shell"><div class="breadcrumbs"><a href="index.html">Главная</a><span>/</span><span>О проекте</span></div><div class="simple-layout"><div><div class="eyebrow"><span></span> ПРИЯТНО ПОЗНАКОМИТЬСЯ</div><h1>Еда — это<br><em>про заботу.</em></h1><p class="simple-lead">«Ложка» — небольшая коллекция идей для домашней кухни и поводов собраться за одним столом.</p><div class="prose"><h2>Просто и с удовольствием</h2><p>Мы собрали рецепты из привычных продуктов, чтобы вам было легче придумать завтрак, обед или ужин. Выбирайте блюдо по настроению, пробуйте и меняйте детали под себя.</p><p>Материалы и фотографии этой первоначальной версии подготовлены с помощью искусственного интеллекта. Иллюстрации показывают возможный вариант подачи и могут отличаться от вашего результата. Учитывайте аллергии и особенности продуктов, проверяйте готовность блюд.</p><h2>Поделитесь идеей</h2><p>Заметили ошибку или хотите предложить рецепт? Напишите нам на странице проекта на GitHub. Для отправки сообщения понадобится аккаунт GitHub.</p><a class="button button-dark" href="https://github.com/DenWot434536/denwot434536.github.io/issues" target="_blank" rel="noopener noreferrer">Написать нам {icon("up-right")}</a></div></div><div class="simple-image"><img src="assets/images/pancakes.jpg" alt="Сырники с ягодами на уютном столе" width="928" height="1152"><span>ГОТОВЬТЕ В СВОЁ УДОВОЛЬСТВИЕ ✳</span></div></div></section>'''
    return page("О проекте — Ложка", "Знакомьтесь с «Ложкой»: коллекцией простых идей для домашней кухни.", content, path="/about.html", image="assets/images/pancakes.jpg")


def privacy_page():
    content = '''<section class="simple-page shell"><div class="breadcrumbs"><a href="index.html">Главная</a><span>/</span><span>Конфиденциальность</span></div><div class="policy-content"><div class="eyebrow"><span></span> ВАЖНАЯ ИНФОРМАЦИЯ</div><h1>Конфиденциальность</h1><p class="simple-lead">Что происходит с данными при использовании сайта «Ложка».</p><div class="prose"><h2>Данные на сайте</h2><p>В текущей версии сайт не содержит форм регистрации и не запрашивает имя, телефон или адрес электронной почты. Поиск и фильтрация рецептов выполняются в браузере; поисковые запросы на наш сервер не отправляются.</p><h2>Cookie и сторонние сервисы</h2><p>В этой версии сайт самостоятельно не устанавливает файлы cookie и не подключает рекламные сети или системы аналитики. Если они появятся, информация на этой странице должна быть обновлена до их подключения.</p><p>Сайт размещён на GitHub Pages. Хостинг может обрабатывать технические данные посетителей в соответствии со своей <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener noreferrer">политикой конфиденциальности</a>.</p><h2>Внешние ссылки</h2><p>При переходе на GitHub действуют правила этого сервиса. Чтобы задать вопрос через GitHub Issues, может потребоваться войти в свой аккаунт.</p><h2>Вопросы</h2><p>Если вы хотите связаться с владельцем сайта, воспользуйтесь <a href="https://github.com/DenWot434536/denwot434536.github.io/issues" target="_blank" rel="noopener noreferrer">страницей проекта на GitHub</a>.</p></div></div></section>'''
    return page("Конфиденциальность — Ложка", "Информация о данных посетителей и работе сайта «Ложка».", content, path="/privacy.html")


def build():
    if not RECIPES:
        raise ValueError("Add at least one recipe to data/recipes.json")
    slugs = set()
    valid_categories = {item[0] for item in CATEGORIES} | {"quick"}
    for recipe in RECIPES:
        slug = recipe["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
            raise ValueError(f"Invalid or duplicate recipe slug: {slug}")
        slugs.add(slug)
        if not set(recipe["categories"]) <= valid_categories:
            raise ValueError(f"Unknown category in {slug}")
        if not (ROOT / "assets" / "images" / recipe["image"]).is_file():
            raise ValueError(f"Missing image for {slug}")
    output = ROOT / "recipes"
    output.mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(home(), encoding="utf-8")
    (ROOT / "about.html").write_text(about_page(), encoding="utf-8")
    (ROOT / "privacy.html").write_text(privacy_page(), encoding="utf-8")
    for i, recipe in enumerate(RECIPES):
        (output / f"{recipe['slug']}.html").write_text(recipe_page(recipe, RECIPES[(i + 1) % len(RECIPES)]), encoding="utf-8")
    paths = ["/", "/about.html", "/privacy.html"] + [f"/recipes/{r['slug']}.html" for r in RECIPES]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE_URL}{path}</loc></url>\n" for path in paths) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(RECIPES)} recipes and {len(paths)} indexable pages.")


if __name__ == "__main__":
    build()
