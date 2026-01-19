# テストディレクトリ

Freedom プロジェクトのテストスイートです。

## テストファイル一覧

| ファイル                      | 説明                             | テスト数 |
| ----------------------------- | -------------------------------- | -------- |
| **test_backend_functions.py** | バックエンド関数のユニットテスト | 13       |
| **test_validators.py**        | バリデーション関数のテスト       | 11       |
| **test_integration.py**       | 統合テスト                       | 5        |
| **test_ui_components.py**     | UI コンポーネントのテスト        | 13       |
| **test_frontend.py**          | フロントエンド統合テスト         | 3        |
| **test_ui_behavior.py**       | UI 動作テスト                    | 8        |
| **合計**                      |                                  | **53**   |

## クイックスタート

### すべてのテストを実行

```bash
python -m pytest tests/ -v
```

### 特定のテストファイルを実行

```bash
# バックエンドテスト
python -m pytest tests/test_backend_functions.py -v

# バリデーションテスト
python -m pytest tests/test_validators.py -v

# 統合テスト
python -m pytest tests/test_integration.py -v

# UI テスト
python -m pytest tests/test_ui_components.py -v
```

### 特定のテストケースを実行

```bash
python -m pytest tests/test_backend_functions.py::BackendFunctionsTestCase::test_add_schedule_success -v
```

## テスト結果

最新のテスト結果（2026年1月19日）:

```
================================ test session starts ================================
53 items collected

test_backend_functions.py::BackendFunctionsTestCase
  ✓ test_add_schedule_end_before_start
  ✓ test_add_schedule_invalid_date_format
  ✓ test_add_schedule_success
  ✓ test_delete_schedule_no_id
  ✓ test_delete_schedule_not_found
  ✓ test_delete_schedule_success
  ✓ test_get_monthly_schedule
  ✓ test_get_schedule_empty_result
  ✓ test_get_schedule_no_date_param
  ✓ test_get_schedule_success
  ✓ test_schedule_to_dict_conversion
  ✓ test_update_schedule_not_found
  ✓ test_update_schedule_success

test_validators.py::ValidatorsTestCase
  ✓ test_empty_name
  ✓ test_end_before_start
  ✓ test_invalid_end_date_format
  ✓ test_invalid_end_time_format
  ✓ test_invalid_start_date_format
  ✓ test_invalid_start_time_format
  ✓ test_multiday_schedule
  ✓ test_same_start_and_end
  ✓ test_valid_mode_values
  ✓ test_valid_schedule_format
  ✓ test_whitespace_in_name

test_integration.py::IntegrationTestCase
  ✓ test_edge_case_midnight_schedule
  ✓ test_full_schedule_lifecycle
  ✓ test_multiday_schedule_retrieval
  ✓ test_multiple_schedules_same_day
  ✓ test_overlapping_schedules

test_ui_components.py
  ✓ TestCalendarWindow (6 tests)
  ✓ TestChangeWindow (4 tests)
  ✓ TestMainMenu (3 tests)

test_frontend.py::FrontendTestCase
  ✓ test_calendar_request
  ✓ test_change_submit
  ✓ test_menu_buttons_open

test_ui_behavior.py
  ✓ TestMainImport (1 test)
  ✓ TestCalendar (3 tests)
  ✓ TestChange (2 tests)
  ✓ TestMoney (2 tests)

============================= 53 passed in 43.30s ==============================
```

**成功率: 100% (53/53)**

## テストカテゴリ

### 1. バックエンド関数テスト

`test_backend_functions.py` - バックエンドのCRUD操作をテスト

**カバレッジ:**

- スケジュール追加（add_schedule）
- スケジュール取得（get_schedule）
- スケジュール更新（update_schedule）
- スケジュール削除（delete_schedule）
- 月別スケジュール取得（get_monthly_schedule）
- データ変換（schedule_to_dict）

### 2. バリデーションテスト

`test_validators.py` - 入力値検証をテスト

**カバレッジ:**

- 日付・時刻フォーマット検証
- 開始・終了時刻の妥当性チェック
- 空の入力値チェック
- モード（A, B, NULL）の検証

### 3. 統合テスト

`test_integration.py` - モジュール間の連携をテスト

**カバレッジ:**

- スケジュールのライフサイクル（追加→取得→更新→削除）
- 複数スケジュールの同時処理
- 重複・複数日スケジュールの処理
- エッジケース（深夜のスケジュール等）

### 4. UI コンポーネントテスト

`test_ui_components.py` - UIコンポーネントの動作をテスト

**カバレッジ:**

- カレンダーウィンドウ（初期化、ナビゲーション、日付選択）
- 変更ウィンドウ（新規追加、更新、バリデーション）
- メインメニュー（初期化、各機能の呼び出し）

### 5. フロントエンド統合テスト

`test_frontend.py` - フロントエンド全体の動作をテスト

### 6. UI 動作テスト

`test_ui_behavior.py` - ユーザーインタラクションをテスト

## 必要なパッケージ

```bash
pip install pytest
pip install -r requirements.txt
```

## CI/CD

このテストスイートは以下のタイミングで自動実行されます：

- プルリクエスト作成時
- mainブランチへのマージ前
- リリースタグ作成時

## トラブルシューティング

### データベースエラー

```bash
# データベースをリセット
rm my_database.db
python -c "from back_end.db.init import init_db; init_db()"
```

### JSON ファイルのクリーンアップ

```bash
# テスト用JSONファイルを削除
rm json/request.json json/response.json
```

### Tkinter エラー

テストは GUI なしで実行されます（`root.withdraw()`）。
X11 や macOS での表示エラーが発生する場合は、環境変数を設定：

```bash
export DISPLAY=:0  # Linux
```

## コントリビューション

新しいテストを追加する場合：

1. 適切なテストファイルに追加
2. テストケース名は `test_` で開始
3. ドキュメント文字列で説明を追加
4. すべてのテストが通ることを確認

## 詳細ドキュメント

詳しいテスト計画については [TEST_PLAN.md](TEST_PLAN.md) を参照してください。
