# No.1-LayoutParser

Unstructured.ioを使用したレイアウト解析アプリケーション

## 🚀 セットアップ

### 1. 環境の作成
```bash
conda create -n no.1-layoutparser python=3.12 -y
conda activate no.1-layoutparser
```

### 2. 依存関係のインストール


```bash
pip install -r requirements.txt
# pip list --format=freeze > requirements.txt
```


## 🎯 使用方法

### アプリケーションの起動
```bash
python app.py
```

ブラウザで `http://localhost:7860` にアクセスしてください。

### UI機能
- **画像アップロード**: 解析したい画像をアップロード
- **解析開始**: Unstructured.ioを使用してレイアウト解析を実行
- **リアルタイムログ**: 解析の進行状況をリアルタイムで表示
- **結果表示**: 元画像と解析結果を並べて表示
- **ラベル表示**: 検出された要素に英語名でラベルを表示

## 🔧 技術仕様

- **フレームワーク**: Gradio
- **レイアウト解析**: Unstructured.io
- **画像処理**: PIL (Pillow)
- **UI言語**: 日本語
- **ログ言語**: 日本語
- **OCR言語**: 日本語（jpn）+ 英語（eng）デフォルト

## 🌐 言語設定

### デフォルト言語
- **日本語（jpn）**: 主要言語
- **英語（eng）**: 補助言語

### サポートされている言語
アプリケーションは以下の言語でのOCR処理をサポートしています：

| 言語コード | 言語名 | 状態 |
|-----------|--------|------|
| jpn | 日本語 | ✅ デフォルト |
| eng | 英語 | ✅ デフォルト |
| chi_sim | 中国語（簡体字） | ⚪ 利用可能 |
| chi_tra | 中国語（繁体字） | ⚪ 利用可能 |
| kor | 韓国語 | ⚪ 利用可能 |
| fra | フランス語 | ⚪ 利用可能 |
| deu | ドイツ語 | ⚪ 利用可能 |
| spa | スペイン語 | ⚪ 利用可能 |
| ita | イタリア語 | ⚪ 利用可能 |
| rus | ロシア語 | ⚪ 利用可能 |
| ara | アラビア語 | ⚪ 利用可能 |
| hin | ヒンディー語 | ⚪ 利用可能 |
| tha | タイ語 | ⚪ 利用可能 |
| vie | ベトナム語 | ⚪ 利用可能 |

### 言語設定のカスタマイズ
`config.py`ファイルの`DEFAULT_LANGUAGES`を編集することで、使用する言語を変更できます：

```python
# 例: 日本語、英語、中国語（簡体字）を使用
DEFAULT_LANGUAGES = ["jpn", "eng", "chi_sim"]
```

## ⚠️ 重要な更新情報

### max_size パラメータの廃止対応
Unstructured.io v4.26以降、`max_size`パラメータが廃止され、新しい`size`形式に変更されました。

**旧形式（廃止予定）:**
```python
max_size = 4096
```

**新形式（推奨）:**
```python
size = {"longest_edge": 4096}
```

本アプリケーションは新しい形式に対応済みです。`config.py`の`UNSTRUCTURED_CONFIG`で設定を変更できます。

## 📋 サポートされる画像形式

- PNG
- JPEG
- JPG
- BMP
- TIFF

## 🎨 解析結果の可視化

### YOLOX標準ラベルマッピング（100%統一）

本アプリケーションは、unstructured-inference/models/yolox.pyのYOLOX_LABEL_MAPと100%統一されています：

| ID | 要素タイプ（英語） | 日本語名 | 色 | 説明 | 表示ラベル |
|----|------------------|----------|-----|------|-----------|
| 0 | Caption | キャプション | 赤 | 図表のキャプション | Caption |
| 1 | Footnote | 脚注 | オレンジ | ページ下部の脚注 | Footnote |
| 2 | Formula | 数式 | 紫 | 数学的な式や方程式 | Formula |
| 3 | ListItem | リストアイテム | 青 | 箇条書きや番号付きリスト | ListItem |
| 4 | PageFooter | ページフッター | グレー | ページ下部の情報 | PageFooter |
| 5 | PageHeader | ページヘッダー | ピンク | ページ上部の情報 | PageHeader |
| 6 | Picture | 画像 | マゼンタ | 写真、図、イラスト | Picture |
| 7 | SectionHeader | セクションヘッダー | ゴールド | セクションの見出し | SectionHeader |
| 8 | Table | テーブル | 黄 | 表形式のデータ | Table |
| 9 | Text | テキスト | 緑 | 一般的な本文テキスト | Text |
| 10 | Title | タイトル | 赤オレンジ | 文書のタイトル | Title |

**注意**: 画像上のラベルは英語名（表示ラベル列）で表示されます。

### 後方互換性

以下の要素タイプも認識されます（Unstructured.ioの他のモデルとの互換性のため）：
- **NarrativeText**: 本文テキスト（Textと同じ扱い） → ラベル: "NarrativeText"
- **Image**: 画像（Pictureと同じ扱い） → ラベル: "Image"
- **Header**: ヘッダー（PageHeaderと同じ扱い） → ラベル: "Header"
- **Footer**: フッター（PageFooterと同じ扱い） → ラベル: "Footer"