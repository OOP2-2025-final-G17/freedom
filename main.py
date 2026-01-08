import tkinter as tk


def run_app() -> None:
    """Launch the Tkinter GUI main menu."""
    try:
        # front_end はパッケージとして構成済み
        from front_end.menu import MainMenu
    except Exception as e:  # ImportError など
        print("front_end.menu のインポートに失敗しました:", e)
        print("front_end/ 配下のファイルが存在するか確認してください。")
        return

    root = tk.Tk()
    MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
