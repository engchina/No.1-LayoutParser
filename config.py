#!/usr/bin/env python3
"""
アプリケーション設定ファイル
Unstructured.ioレイアウト解析の設定を管理
"""

# OCR言語設定
# Tesseractの言語コードを使用
# 参考: https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html
DEFAULT_LANGUAGES = ["jpn", "eng"]  # 日本語と英語

# サポートされている言語のマッピング
SUPPORTED_LANGUAGES = {
    "jpn": "日本語",
    "eng": "英語",
    "chi_sim": "中国語（簡体字）",
    "chi_tra": "中国語（繁体字）",
    "kor": "韓国語",
    "fra": "フランス語",
    "deu": "ドイツ語",
    "spa": "スペイン語",
    "ita": "イタリア語",
    "rus": "ロシア語",
    "ara": "アラビア語",
    "hin": "ヒンディー語",
    "tha": "タイ語",
    "vie": "ベトナム語",
}

# Unstructured.io設定
UNSTRUCTURED_CONFIG = {
    "languages": DEFAULT_LANGUAGES,
    "strategy": "hi_res",  # 高解像度戦略を使用
    "infer_table_structure": True,  # テーブル構造を推論
    "extract_images": True,  # 画像を抽出
    "include_page_breaks": True,  # ページブレークを含める
    # 新しいsize形式を使用（max_sizeの代替）
    "size": {"longest_edge": 4096},  # 最大辺長を4096ピクセルに設定
}

# UI設定
UI_CONFIG = {
    "title": "レイアウトパーサー",
    "description": "画像をアップロードして、レイアウト解析を実行してください。",
    "theme": "soft",
    "server_name": "0.0.0.0",
    "server_port": 7860,
    "share": False,
    "debug": True,
}

# 画像処理設定
IMAGE_CONFIG = {
    "max_image_size": (4096, 4096),  # 最大画像サイズ
    "supported_formats": ["PNG", "JPEG", "JPG", "BMP", "TIFF", "WEBP"],
    "temp_file_suffix": ".png",
    "default_dpi": 300,
}

# 可視化設定
VISUALIZATION_CONFIG = {
    "bbox_width": 2,  # 境界ボックスの線幅
    "font_size": 12,  # フォントサイズ
    "label_offset": 15,  # ラベルのオフセット
    "fallback_box_height": 30,  # フォールバック時のボックス高さ
    "fallback_box_width": 200,  # フォールバック時のボックス幅
}

# ログ設定
LOG_CONFIG = {
    "timestamp_format": "%H:%M:%S",
    "max_log_lines": 1000,
    "log_element_details": True,
    "log_coordinates": True,
}

def get_language_display_names(language_codes):
    """
    言語コードから表示名を取得

    Args:
        language_codes: 言語コードのリスト

    Returns:
        表示名のリスト
    """
    return [SUPPORTED_LANGUAGES.get(code, code) for code in language_codes]

def validate_languages(language_codes):
    """
    言語コードの妥当性を検証

    Args:
        language_codes: 言語コードのリスト

    Returns:
        tuple: (有効な言語コード, 無効な言語コード)
    """
    valid_codes = []
    invalid_codes = []

    for code in language_codes:
        if code in SUPPORTED_LANGUAGES:
            valid_codes.append(code)
        else:
            invalid_codes.append(code)

    return valid_codes, invalid_codes

def get_unstructured_config(custom_languages=None):
    """
    Unstructured.ioの設定を取得

    Args:
        custom_languages: カスタム言語設定（オプション）

    Returns:
        設定辞書
    """
    config = UNSTRUCTURED_CONFIG.copy()

    if custom_languages:
        valid_langs, invalid_langs = validate_languages(custom_languages)
        if invalid_langs:
            print(f"警告: 無効な言語コード: {invalid_langs}")
        if valid_langs:
            config["languages"] = valid_langs
        else:
            print("警告: 有効な言語コードがありません。デフォルト設定を使用します。")

    return config

def get_language_info():
    """
    現在の言語設定情報を取得

    Returns:
        言語設定の詳細情報
    """
    config = get_unstructured_config()
    languages = config["languages"]
    display_names = get_language_display_names(languages)

    return {
        "codes": languages,
        "names": display_names,
        "count": len(languages),
        "primary": languages[0] if languages else None,
        "primary_name": display_names[0] if display_names else None,
    }

if __name__ == "__main__":
    # 設定情報の表示
    print("📋 アプリケーション設定")
    print("=" * 40)

    # 言語設定
    lang_info = get_language_info()
    print(f"🌐 言語設定:")
    print(f"  - 言語数: {lang_info['count']}")
    print(f"  - 主言語: {lang_info['primary_name']} ({lang_info['primary']})")
    print(f"  - 全言語: {', '.join(lang_info['names'])}")

    # Unstructured設定
    print(f"\n🔧 Unstructured.io設定:")
    unstructured_config = get_unstructured_config()
    for key, value in unstructured_config.items():
        print(f"  - {key}: {value}")

    # UI設定
    print(f"\n🖥️  UI設定:")
    for key, value in UI_CONFIG.items():
        print(f"  - {key}: {value}")

    # サポート言語一覧
    print(f"\n🌍 サポートされている言語:")
    for code, name in SUPPORTED_LANGUAGES.items():
        status = "✅" if code in DEFAULT_LANGUAGES else "⚪"
        print(f"  {status} {code}: {name}")

    print(f"\n✅ = デフォルト言語, ⚪ = 利用可能")
