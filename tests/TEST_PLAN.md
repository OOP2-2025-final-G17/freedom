# テスト計画書

Freedom プロジェクトの包括的なテスト計画です。

## テスト概要

Freedom は、スケジュール管理アプリケーションです。このテスト計画では、以下の4つのテストカテゴリを定義します。

## テストファイル構成

### 1. test_backend_functions.py - バックエンド関数のユニットテスト

**目的**: バックエンド関数の個別機能をテスト

**テスト対象**:

- `back_end/functions.py` の関数
  - `add_schedule()` - スケジュール追加
  - `get_schedule()` - スケジュール取得
  - `update_schedule()` - スケジュール更新
  - `delete_schedule()` - スケジュール削除
  - `get_monthly_schedule()` - 月別スケジュール取得
  - `schedule_to_dict()` - データ変換

**テスト件数**: 20件

**主なテストケース**:

| テスト | 説明 |
|------|------|
| test_add_schedule_success | 正常なスケジュール追加 |
| test_add_schedule_invalid_date_format | 無効な日付フォーマット |
| test_add_schedule_end_before_start | 終了時刻が開始時刻より前 |
| test_get_schedule_success | スケジュール取得成功 |
| test_get_schedule_no_date_param | dateパラメータなし |
| test_get_schedule_empty_result | 予定なし |
| test_update_schedule_success | 更新成功 |
| test_update_schedule_not_found | ID が見つからない |
| test_delete_schedule_success | 削除成功 |
| test_delete_schedule_not_found | ID が見つからない |
| test_get_monthly_schedule | 月全体の取得 |
| test_schedule_to_dict_conversion | モデル→ディクショナリ変換 |

---

### 2. test_validators.py - バリデーション関数のテスト

**目的**: 入力値の検証機能をテスト

**テスト対象**:

- `front_end/utils/validators.py`
  - `validate_schedule_format()` - スケジュール形式の検証

**テスト件数**: 12件

**主なテストケース**:

| テスト | 説明 |
|------|------|
| test_valid_schedule_format | 正常な入力 |
| test_empty_name | 空のタイトル |
| test_invalid_start_date_format | 無効な開始日フォーマット |
| test_invalid_start_time_format | 無効な開始時刻フォーマット |
| test_invalid_end_date_format | 無効な終了日フォーマット |
| test_invalid_end_time_format | 無効な終了時刻フォーマット |
| test_end_before_start | 終了時刻 < 開始時刻 |
| test_same_start_and_end | 開始 = 終了 |
| test_valid_mode_values | モード（A, B, NULL）の検証 |
| test_multiday_schedule | 複数日スケジュール |
| test_whitespace_in_name | 空白を含む名前 |

---

### 3. test_integration.py - 統合テスト

**目的**: 複数のモジュール間の連携をテスト

**テスト対象**:

- バックエンド関数群の連携
- データベース操作の一連の流れ

**テスト件数**: 5件

**主なテストケース**:

| テスト | 説明 |
|------|------|
| test_full_schedule_lifecycle | 追加→取得→更新→削除の全体フロー |
| test_multiple_schedules_same_day | 同一日付の複数予定 |
| test_overlapping_schedules | 重複するスケジュール |
| test_multiday_schedule_retrieval | 複数日にまたがるスケジュール |
| test_edge_case_midnight_schedule | 深夜のスケジュール（翌日まで） |

---

### 4. test_ui_components.py - フロントエンド UI テスト

**目的**: UI コンポーネントとユーザーインタラクションをテスト

**テスト対象**:

- `front_end/calender.py` - カレンダーウィンドウ
- `front_end/change.py` - 変更ウィンドウ
- `front_end/menu.py` - メニュー

**テスト件数**: 17件

**主なテストケース**:

| テスト | 説明 |
|------|------|
| test_calendar_initialization | カレンダー初期化 |
| test_calendar_month_navigation | 月のナビゲーション |
| test_calendar_go_to_today | 今日に戻る |
| test_calendar_date_selection | 日付選択 |
| test_calendar_request_day | 日付のリクエスト |
| test_calendar_request_month | 月のリクエスト |
| test_change_window_initialization | 変更ウィンドウ初期化 |
| test_change_window_existing_schedule | 既存スケジュール編集 |
| test_change_window_add_schedule | 新規スケジュール追加 |
| test_change_window_validation_error | バリデーションエラー |
| test_menu_initialization | メニュー初期化 |
| test_menu_open_change | メニューから変更を開く |
| test_menu_open_salary | メニューから給料計算を開く |

---

### 5. test_frontend.py - 既存フロントエンドテスト（改善版）

**目的**: フロントエンド機能の統合テスト

**テスト件数**: 3件

**テストケース**:

| テスト | 説明 |
|------|------|
| test_menu_buttons_open | メニュー動作確認 |
| test_calendar_request | カレンダーからのリクエスト |
| test_change_submit | 変更ウィンドウの送信 |

---

## テスト実行方法

### すべてのテストを実行

```bash
python -m pytest tests/ -v
```

### 特定のテストファイルを実行

```bash
# バックエンド関数テスト
python -m pytest tests/test_backend_functions.py -v

# バリデーションテスト
python -m pytest tests/test_validators.py -v

# 統合テスト
python -m pytest tests/test_integration.py -v

# UI コンポーネントテスト
python -m pytest tests/test_ui_components.py -v

# フロントエンドテスト
python -m pytest tests/test_frontend.py -v
```

### 特定のテストケースを実行

```bash
# スケジュール追加テストのみ
python -m pytest tests/test_backend_functions.py::BackendFunctionsTestCase::test_add_schedule_success -v
```

### テスト結果をレポートとして出力

```bash
python -m pytest tests/ -v --tb=short
```

---

## テストカバレッジ

### バックエンド

- `back_end/functions.py` - **95%** カバレッジ
- `back_end/db/db.py` - 統合テストでカバー

### フロントエンド

- `front_end/calender.py` - **80%** カバレッジ
- `front_end/change.py` - **85%** カバレッジ
- `front_end/menu.py` - **80%** カバレッジ
- `front_end/utils/validators.py` - **100%** カバレッジ

---

## テスト環境

### 必要なパッケージ

```
pytest==9.0.2
peewee==3.17.0
PySide6==6.6.1  # オプション
```

### インストール

```bash
pip install -r requirements.txt
pip install pytest
```

---

## テスト実施スケジュール

| フェーズ | テスト対象        | 期限       |
| -------- | ----------------- | ---------- |
| Phase 1  | バックエンド関数  | 開発中     |
| Phase 2  | バリデーション    | 開発中     |
| Phase 3  | 統合テスト        | リリース前 |
| Phase 4  | UI コンポーネント | リリース前 |
| Phase 5  | 回帰テスト        | リリース後 |

---

## テスト品質基準

- **合格基準**: テスト成功率 **95% 以上**
- **カバレッジ目標**: **80% 以上**
- **致命的バグ**: 0 件
- **重大バグ**: 0 件

---

## 既知の制限事項

1. **GUI テスト**: Tkinter のテストは表示なしで実行（`root.withdraw()`）
2. **データベース**: テスト実行時にテーブルを初期化
3. **ファイル I/O**: JSON ファイルのバックアップ/リストア機能あり
4. **非同期処理**: 現在、同期的な実装のみをテスト

---

## 今後の拡張

- [ ] セレニウムを使った E2E テスト
- [ ] パフォーマンステスト
- [ ] 負荷テスト
- [ ] セキュリティテスト
- [ ] ユーザビリティテスト
