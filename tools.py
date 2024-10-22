import requests,subprocess, json,time, os

def session_start():
    try:
        # Start Waydroid session in the background
        subprocess.Popen(["waydroid", "session", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Waydroid Session Started in the background")
    except Exception as e:
        print("Error while starting Waydroid session:", e)

def session_stop():
    try:
        subprocess.run(["waydroid", "session", "stop"], check=True)
        print("Waydroid Session Stopped")

    except Exception as e:
        print("Error:",e)

## For GAPPS #
def check_game(package_name):
    try:
        result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], capture_output=True, text=True)
        return package_name in result.stdout
    except Exception as e:
        print(f"Error checking package: {e}")
        return False

def install_app_from_play_store(package_name):
    try:
        session_start()
        command = [
            'adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', 
            '-d', f'https://play.google.com/store/apps/details?id={package_name}'
        ]
        
        subprocess.run(command, check=True)
        print(f"Opened Play Store for package: {package_name}")
        
        time.sleep(2)

        install_button_x = 105
        install_button_y = 657

        command_tap_install = [
            'adb', 'shell', 'input', 'tap', str(install_button_x), str(install_button_y)
        ]
        subprocess.run(command_tap_install, check=True)
        print("Clicked the Install button.")
        time.sleep(1)
        while True:
            if check_game(package_name):
                #print(f"Installed!")
                break
            else:
                #print("Installing...")
                time.sleep(5)


    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

def stop_installation_app_from_play_store(package_name):
    try:
        session_start()
        command = [
            'adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', 
            '-d', f'https://play.google.com/store/apps/details?id={package_name}'
        ]
        
        subprocess.run(command, check=True)
        print(f"Opened Play Store for package: {package_name}")
        
        time.sleep(2)

        install_button_x = 276
        install_button_y = 354

        command_tap_install = [
            'adb', 'shell', 'input', 'tap', str(install_button_x), str(install_button_y)
        ]
        subprocess.run(command_tap_install, check=True)
        print("Clicked the Cancel button.")
        time.sleep(1)
        return
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


def launch_game(package_name):
    try:
        subprocess.run(["waydroid", "app", "launch", package_name])
    except Exception as e:
        print("Error:", e)

def waydroid_app_uninstall(package_name):
    try:
        #adb shell pm uninstall com.HoYoverse.hkrpgoversea
        subprocess.run(["adb", "shell","pm", "uninstall",package_name])
    except Exception as e:
        print("Error:", e)

## For APK ##
def install_game_apk(apk_path):
    try:
        if apk_path:
            subprocess.run(["waydroid", "install", apk_path])
            print("Apk installed succesfully!")
        else:
            print("Apk Not Found!")
    except Exception as e:
        print("Error:", e)

def uninstall_game_apk(package_name):
    try:
        if package_name:
            subprocess.run(["waydroid", "remove", package_name])
            print("Game is uninstalled succesfully!")
        else:
            print("Game Not Found!")
    except Exception as e:
         print("Error:",e)

def launch_game_apk(package_name):
    try:
        if package_name:
            subprocess.run(["waydroid", "launch", package_name])
            print("Game Launched!")
        else:
            print("Game Not Found!")
    except Exception as e:
        print("Error:",e )


def download_game_apk(download_url, save_path):
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(save_path, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                downloaded_size += len(data)
                
                percentage = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                print(f"İndirme yüzdesi: {percentage:.2f}%") 

        print(f"APK dosyası başarıyla indirildi: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Hata: {e}")

def load_games(json_path):
    try:
        with open(json_path, 'r') as file:
            games = json.load(file)
        return games
    except Exception as e:
        print("Error:",e)

## Waydroid is Running?
def is_waydroid_running():
    try:
        result = subprocess.run(['waydroid', 'status'], stdout=subprocess.PIPE, text=True)

        output = result.stdout
        if "Session:\tRUNNING" in output and "Container:\tRUNNING" in output: 
            return True
        
    except Exception as e:
        print(f"Error checking Waydroid status: {e}")
        return False
    
## User has Waydroid?
def is_waydroid_installed():
    possible_paths = [
        "/usr/bin/waydroid",
        "/usr/local/bin/waydroid",
        "/usr/bin/waydroid-session"
    ]
    return any(os.path.exists(path) for path in possible_paths)