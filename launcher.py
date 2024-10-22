import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage
import subprocess
from tools import (
    install_game_apk, uninstall_game_apk, is_waydroid_installed,
    is_waydroid_running, launch_game, install_app_from_play_store,
    download_game_apk, check_game, load_games, stop_installation_app_from_play_store, session_start,
    session_stop, waydroid_app_uninstall
)
import os
import threading
import time
from PIL import Image

class GameLauncher(ctk.CTk):
    def __init__(self, games):
        super().__init__()
        self.title("A Mobile Gacha Game Launcher")
        self.geometry("1200x800")
        self.games = games
        self.installation_running = False

        self.loading_screen()

    def loading_screen(self):
        try:
            self.loading_gif = CTkImage(dark_image=Image.open("tools/images/loading.gif"), size=(520, 520))
            self.gif_label = CTkLabel(self, image=self.loading_gif, text="")
            self.gif_label.pack(pady=20)

            self.loading_label = CTkLabel(self, text="Wait! Meow, Checking Existing Waydroid Installations...", font=("Arial", 24))
            self.loading_label.pack(pady=20)

            threading.Thread(target=self.check_waydroid_installation, daemon=True).start()
        except Exception as e:
            print(f"Error in loading_screen: {e}")

    def check_waydroid_installation(self):
        try:
            if not is_waydroid_installed():
                self.loading_label.configure(text="Meow says, You dont have any copy of waydroid.")
                time.sleep(3)
                return
            else:
                time.sleep(3)
                self.loading_label.configure(text="Meow Found, a copy of waydroid! ")
                self.after(2000, self.show_game_launcher)

        except Exception as e:
            print(f"Error in check_waydroid_installation: {e}")

    def show_game_launcher(self):
        try:
            self.loading_label.pack_forget()
            self.gif_label.pack_forget()
            self.create_widgets()
        except Exception as e:
            print(f"Error in show_game_launcher: {e}")

    def show_uninstall_window(self, package_name):
        try:
            uninstall_window = ctk.CTkToplevel(self)
            uninstall_window.title("Uninstall Game")
            uninstall_window.geometry("300x150")

            label = CTkLabel(uninstall_window, text=f"Are you sure you want to uninstall {package_name}?", font=("Arial", 16))
            label.pack(pady=10)

            uninstall_button = CTkButton(uninstall_window, text="Uninstall", command=lambda: self.uninstall_game(package_name))
            uninstall_button.pack(pady=20)

            cancel_button = CTkButton(uninstall_window, text="Cancel", command=uninstall_window.destroy)
            cancel_button.pack(pady=10)
        except Exception as e:
            print(f"Error in show_uninstall_window: {e}")

    def uninstall_game(self, package_name):
        try:
            waydroid_app_uninstall(package_name)
            self.create_widgets()
            print(f"{package_name} has been uninstalled.")
        except Exception as e:
            print(f"Error in uninstall_game: {e}")

    def create_widgets(self):
        try:
            title_label = CTkLabel(self, text="Available games", font=("Arial", 24))
            title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

            start_row = 1
            self.configure(bg_color="#2B2B2B")

            for index, game in enumerate(self.games):
                frame = CTkFrame(self, corner_radius=10, fg_color="#2B2B2B")
                row = start_row + (index // 5)
                column = index % 5
                frame.grid(row=row, column=column, padx=10, pady=10)

                abs_image_path = os.path.abspath(game["image"])
                img = Image.open(abs_image_path)

                if self.is_game_installed(game["package_name"]):
                    img = CTkImage(dark_image=img, size=(200, 320))
                else:
                    img = img.convert("L")
                    img = img.resize((200, 320), Image.LANCZOS)
                    img = CTkImage(dark_image=img, size=(200, 320))

                img_button = CTkButton(
                    frame,
                    image=img,
                    command=lambda g=game, f=frame: self.handle_game_action(g["package_name"], f),
                    text="",
                    border_width=0,
                    corner_radius=10,
                    hover_color="#404040",
                    fg_color="transparent",
                    width=0,
                    height=0
                )
                img_button.image = img
                img_button.grid(row=0, column=0, rowspan=3)

                name_label = CTkLabel(frame, text=game["name"], font=("Arial", 12), text_color="#FFFFFF")
                name_label.grid(row=3, column=0, pady=(5, 0))

                game["loading_label"] = CTkLabel(frame, text="", font=("Arial", 16), text_color="#FFFFFF", fg_color="transparent")
                game["loading_label"].grid(row=1, column=0, sticky="s")

                img_button.bind("<Button-3>", lambda e, g=game: self.show_uninstall_window(g["package_name"]))
        except Exception as e:
            print(f"Error in create_widgets: {e}")

    def installation_screen(self, package_name, frame):
        try:
            loading_label = [game["loading_label"] for game in self.games if game["package_name"] == package_name][0]
            loading_label.configure(text="Installing...  ")
            loading_label.grid(row=0, column=0)

            loading_label.bind("<Button-1>", lambda e: self.on_installing_label_click(package_name))

            self.installation_running = True
            self.installation_thread = threading.Thread(target=self.install_and_check, args=(package_name, loading_label), daemon=True)
            self.installation_thread.start()
        except Exception as e:
            print(f"Error in installation_screen: {e}")

    def on_installing_label_click(self, package_name):
        try:
            print("Label clicked!")

            stop_installation_app_from_play_store(package_name)
            self.installation_running = False

            loading_label = [game["loading_label"] for game in self.games if game["package_name"] == package_name][0]

            loading_label.after(1000, loading_label.grid_forget)
        except Exception as e:
            print(f"Error in on_installing_label_click: {e}")

    def install_and_check(self, package_name, loading_label):
        try:
            loading_label.configure(text="Installing... ")
            """if package_name == "com.m648sy.yhdzzldyzaqlmzf.coolplay":
                download_game_apk(,"apk_folder")
            else:"""''
            install_app_from_play_store(package_name)

            while self.installation_running:
                if check_game(package_name):
                    print(f"Installed!")
                    loading_label.configure(text="Installation complete!")
                    time.sleep(1)
                    self.create_widgets()
                    break
                else:
                    print("Installing...")
                    loading_label.configure(text="Installing... Please wait.")
                    time.sleep(5)

            if not self.installation_running:
                loading_label.configure(text="Installation cancelled.")
                time.sleep(1)
                loading_label.grid_forget()
        except Exception as e:
            print(f"Error in install_and_check: {e}")
            loading_label.configure(text="Installation failed.")
            loading_label.grid_forget()

    def handle_game_action(self, package_name, frame):
        try:
            if self.is_game_installed(package_name):
                launch_game(package_name)
            else:
                self.installation_screen(package_name, frame)
        except Exception as e:
            print(f"Error in handle_game_action: {e}")

    def is_game_installed(self, package_name):
        try:
            return check_game(package_name)
        except Exception as e:
            print(f"Error in is_game_installed: {e}")
            return False

def main():
    def check_waydroid():
        try:
            session_stop()
            if not is_waydroid_running():
                print("Waydroid is not running. Starting the Waydroid container...")
                session_start()

                while True:
                    result = subprocess.run(['waydroid', 'status'], stdout=subprocess.PIPE, text=True)
                    output = result.stdout

                    if "Session:\tRUNNING" in output and "Container:\tRUNNING" in output:
                        print("Waydroid is running.")
                        app_list_result = subprocess.run(["waydroid", "app", "list"], stdout=subprocess.PIPE, text=True)
                        if app_list_result.stdout.strip():
                            print("Apps are available.")
                            time.sleep(3)
                            break
                        else:
                            print("No apps found. Waiting for apps to be available...")
                            time.sleep(1)
                    else:
                        print("Waiting for Waydroid to start...")
                        time.sleep(5)

                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("dark-blue")
                games = load_games("tools/json/games.json")
                app = GameLauncher(games)
                app.mainloop()
        except Exception as e:
            print(f"Error in check_waydroid: {e}")

    threading.Thread(target=check_waydroid).start()

if __name__ == "__main__":
    main()
