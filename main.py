from flet import *
import requests
from bs4 import BeautifulSoup
import eyed3
from eyed3.id3.frames import ImageFrame
import json
import time


def load_db():
    try:
        with open("setting.json") as file:
            data = json.load(file)
    except:
        with open("setting.json", "w") as file:
            data = {"path": "", "theme": "light"}
            json.dump(data, file, indent=2)
    return data


def save_db(data):
    with open("setting.json", "w") as file:
        json.dump(data, file, indent=2)


setting = load_db()

"""
Tasks:
    - build with flet
    DONE!!!
"""


path = setting["path"]


def main(page: Page):
    page.title = "Castbox Downloader"
    page.window.height = 520
    page.window.width = 320
    page.window.resizable = False
    page.window.maximizable = False
    page.horizontal_alignment = "center"
    page.padding = 10
    page.theme_mode = setting["theme"]
    page.fonts = {"Rubik": "/fonts/Rubik-VariableFont_wght.ttf"}

    github_img = Image(src="github-logo.png",
                       height=32, width=32, fit=ImageFit.CONTAIN)

    github_icon = IconButton(
        content=github_img,
        url="https://github.com/TKZ700/Castbox-Downloader",
        tooltip="لینک گیتهاب پروژه"
    )

    title_text = Text(
        "Castbox Downloader",
        size=32,
        text_align=TextAlign.CENTER,
        font_family="Rubik",
        weight=FontWeight.W_500,
        color="#ff6a00",
    )

    def download_episode(url, path):
        response = requests.get(url)
        if response.status_code == 200:
            page = BeautifulSoup(response.content, "html.parser")
            ep_name = page.find("h1", "trackinfo-title")["title"]
            ep_name = ep_name.replace(":", "_")
            ep_name = ep_name.replace("?", "")
            ep_name = ep_name.replace("/", "")
            ep_name = ep_name.replace("\\", "")
            cover_div = page.find("div", "coverImgContainer")
            cover_url = cover_div.find("img")["src"]
            cover = requests.get(cover_url)
            audio_tag = page.find("audio")
            source_tag = audio_tag.find("source")
            audio_url = source_tag["src"]
            print(f"Downloading episode: {ep_name}")
            audio = requests.get(audio_url)
            if audio.status_code == 200:
                filename = f"{path}{ep_name}.mp3"
                with open(filename, "wb") as file:
                    file.write(audio.content)
                    print(f"Successfully downloaded: {ep_name}")
                set_cover(filename, cover.content)
            else:
                print(f"Connection error code: {response.status_code}")

        else:
            print(f"Connection error code: {response.status_code}")

    def set_cover(file_path, cover):
        audiofile = eyed3.load(file_path)
        if (audiofile.tag == None):
            audiofile.initTag()

        audiofile.tag.images.set(ImageFrame.FRONT_COVER, cover, 'image/jpeg')

        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)

    def download_playlist(url):
        response = requests.get(url)
        if response.status_code == 200:
            page = BeautifulSoup(response.content, "html.parser")
            playlist_name = page.find("h1", "ch_feed_info_title")["title"]
            episodes = page.find_all("div", class_="ep-item-con")
            print(f"Downloading Playlist: {playlist_name}")
            for episode in episodes:
                episode_url = "https://castbox.fm/" + episode.find("a")["href"]
                download_episode(episode_url, path + f"/{playlist_name}/")
            print(f"Download finished: {playlist_name}")
        else:
            print(f"Connection error code: {response.status_code}")

    def handle_download(e):
        try:
            download_button.disabled = True
            download_button.tooltip = "Downloading the last one..."
            page.update()
            url = input_url.value
            if url.startswith("https://castbox.fm"):
                if url.startswith("https://castbox.fm/va") or url.startswith(
                    "https://castbox.fm/channel"
                ):
                    download_playlist(url)
                elif url.startswith("https://castbox.fm/vb") or url.startswith(
                    "https://castbox.fm/episode"
                ):
                    download_episode(url, path)
                else:
                    input_url.error_text = "Please enter a Playlist/Episode URL."
                    page.update()
            else:
                input_url.error_text = "Invalid URL."
                page.update()
        finally:
            input_url.value = ""
            download_button.disabled = False
            download_finished = SnackBar(
                content=Text("Download finished.", font_family="Rubik",
                             weight=FontWeight.W_500))
            page.overlay.append(download_finished)
            download_finished.open = True
            page.update()
            page.update()

    def save_new_path(e: FilePickerResultEvent):
        if e.path:
            setting["path"] = e.path + "/"
            save_db(setting)
            current_path.value = f"Path: {e.path}"
            success = SnackBar(
                content=Text("New path successfully saved.", font_family="Rubik",
                             weight=FontWeight.W_500))
            page.overlay.append(success)
            success.open = True
            page.update()

    def get_new_path(e):
        file_picker.get_directory_path()

    def change_theme(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        input_url.border_color = "black" if page.theme_mode == "light" else "white"
        setting["theme"] = page.theme_mode
        save_db(setting)
        page.update()
        time.sleep(0.2)
        theme_button.selected = not theme_button.selected
        page.update()

    if page.theme_mode == "light":
        theme_button = IconButton(
            icon=icons.DARK_MODE_ROUNDED,
            selected_icon=icons.LIGHT_MODE_ROUNDED,
            style=ButtonStyle(
                color={"": colors.BLACK, "selected": colors.WHITE}),
            on_click=change_theme,
        )
    else:
        theme_button = IconButton(
            icon=icons.LIGHT_MODE_ROUNDED,
            selected_icon=icons.DARK_MODE_ROUNDED,
            style=ButtonStyle(
                color={"": colors.WHITE, "selected": colors.BLACK}),
            on_click=change_theme,)

    bar = AppBar(
        bgcolor="#ff6a00",
        leading=github_icon,
        actions=[
            theme_button
        ]
    )

    if page.theme_mode == "light":
        input_url = TextField(
            border_radius=5,
            border_color="black",
            label="Playlist/Episode Url",
            label_style=TextStyle(font_family="Rubik", weight=FontWeight.W_500)
        )
    else:
        input_url = TextField(
            border_radius=5,
            border_color="white",
            label="Playlist/Episode Url",
            label_style=TextStyle(font_family="Rubik", weight=FontWeight.W_500)
        )

    download_button = FilledButton(
        text="Download",
        icon=icons.DOWNLOAD,
        width=page.width,
        height=40,
        style=ButtonStyle(bgcolor="#8462fc", text_style=TextStyle(font_family="Rubik", weight=FontWeight.W_500),
                          shape=RoundedRectangleBorder(radius=5)),
        on_click=handle_download
    )

    new_path = FilledButton(
        text="New Path",
        icon=icons.FOLDER,
        width=page.width,
        height=40,
        style=ButtonStyle(bgcolor="#03fc66", text_style=TextStyle(font_family="Rubik", weight=FontWeight.W_500),
                          shape=RoundedRectangleBorder(radius=5)),
        on_click=get_new_path
    )

    file_picker = FilePicker(on_result=save_new_path)

    current_path = Text(f"Path: {setting['path']}", font_family="Rubik",
                        weight=FontWeight.W_500,)

    buttons_column = Column(controls=[download_button, new_path], spacing=5)

    download_col = Column()

    page.add(bar, Container(height=5), title_text,
             Container(height=10), input_url, Container(), buttons_column, download_col, file_picker, current_path)


if __name__ == "__main__":
    app(target=main, assets_dir="assets")
