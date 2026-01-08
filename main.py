import tkinter as tk
from tkinter import ttk
from back_end.db.init import initialize_database 


def run_app() -> None:
    """Launch the Tkinter GUI with calendar on left and menu on right."""
    try:
        from front_end.calender import CalendarWindow
        from front_end.menu import MainMenu
    except Exception as e:
        print("front_end のインポートに失敗しました:", e)
        print("front_end/ 配下のファイルが存在するか確認してください。")
        return

    initialize_database()
    root = tk.Tk()
    root.title("Freedom - Todo/カレンダー/シフト管理")
    root.geometry("1100x700")

    # メインコンテナ
    main_container = tk.Frame(root)
    main_container.pack(fill=tk.BOTH, expand=True)

    # 左側: カレンダー
    left_frame = tk.Frame(main_container, relief=tk.SOLID, bd=1)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)

    calendar_widget = CalendarWindow(left_frame)

    # 右側: メニュー
    right_frame = tk.Frame(main_container, relief=tk.SOLID, bd=1)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 10), pady=10)

    # メニューを右側に配置（rootではなくright_frameを渡す）
    menu_widget = MainMenu(right_frame)

    root.mainloop()


if __name__ == "__main__":
    run_app()
