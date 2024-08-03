from flask import Flask, url_for, request, redirect
from splinter import Browser
from pathlib import Path
from shutil import rmtree
from PIL import Image, ImageOps
from htpy import (
    input as input_,
    button,
    div,
    html,
    render_node,
    form,
    style,
    link,
    head,
    body,
    main,
    fieldset,
)

app = Flask(__name__)

THUMBNAIL_IMAGE_SIZE = (1200, 630)


@app.route("/")
def home():
    return render_node(
        html[
            head[
                link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
                )
            ],
            body[
                main(".container")[
                    form(method="POST", action=url_for("save"))[
                        fieldset(role="group")[
                            input_(type_="text", style="width: 25rem", name="url"),
                            button(type_="submit")["Save"],
                        ]
                    ],
                    # style[
                    #     """
                    #     """
                    # ],
                ]
            ],
        ]
    )


@app.route("/save", methods=["POST"])
def save():
    url = request.form["url"]
    assert "reddit" in url, "Received non-reddit url"
    browser = Browser(fullscreen=True)
    browser.visit(url)
    browser.execute_script("document.getElementsByClassName('author-name')[0].remove()")

    custom_style = """
        faceplate-tracker > a {
            color: rgba(0,0,0,0) !important;
        }
    """.replace("\n", "")
    browser.execute_script(f'document.head.appendChild(document.createElement("style")).innerHTML="{custom_style}"')
    # browser.execute_script(f'document.getElementsByTagName("html")[0].classList = ["theme-dark"]')

    post = browser.find_by_tag("shreddit-post")
    title = post["post-title"]

    screenshot_dir = Path(f"./screenshots/{title}")
    rmtree(screenshot_dir, ignore_errors=True)
    screenshot_dir.mkdir(parents=True)

    input("About to take screenshots. Modify page (expand and sort comments)")
    browser.driver.fullscreen_window()

    post_ss_path = post.screenshot(screenshot_dir / "post", unique_file=False)
    breakpoint()

    # with Image.open(post_ss_path) as img:
    #     ImageOps.pad(img, (1000, 800), color="#75269e").save(post_ss_path)
    # with Image.open(post_ss_path) as img:
    #     ImageOps.pad(img, THUMBNAIL_IMAGE_SIZE, color="#75269e").save(post_ss_path)

    comments = browser.find_by_tag("shreddit-comment")
    for idx, comment in enumerate(comments):
        if int(comment["depth"]) != 0 or comment["collapsed"] == "true" or comment["author"] == "AutoModerator":
            continue
        count = idx + 1
        item_number = str(count).zfill(3)  # Makes upload ordered if sorted by name
        comment.screenshot(screenshot_dir / f"comment-{item_number}", unique_file=False)

    return redirect("/")
