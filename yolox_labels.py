#!/usr/bin/env python3
"""
YOLOX標準ラベルマッピング
unstructured-inference/models/yolox.pyのYOLOX_LABEL_MAPと100%統一

このモジュールは、Unstructured.ioのunstructured-inferenceライブラリで使用される
YOLOXモデルの標準ラベルマッピングを提供します。

参照: https://github.com/Unstructured-IO/unstructured-inference/blob/main/unstructured_inference/models/yolox.py
"""

from enum import Enum
from typing import Dict, Tuple, Optional

class ElementType(Enum):
    """
    文書レイアウト要素のタイプ定義
    unstructured.documents.elementsのElementTypeと互換性を保つ
    """
    CAPTION = "Caption"
    FOOTNOTE = "Footnote" 
    FORMULA = "Formula"
    LIST_ITEM = "ListItem"
    PAGE_FOOTER = "PageFooter"
    PAGE_HEADER = "PageHeader"
    PICTURE = "Picture"
    SECTION_HEADER = "SectionHeader"
    TABLE = "Table"
    TEXT = "Text"
    TITLE = "Title"
    
    # 後方互換性のための追加タイプ
    NARRATIVE_TEXT = "NarrativeText"
    IMAGE = "Image"
    HEADER = "Header"
    FOOTER = "Footer"

# YOLOX_LABEL_MAP: unstructured-inference/models/yolox.pyと100%統一
YOLOX_LABEL_MAP: Dict[int, ElementType] = {
    0: ElementType.CAPTION,        # キャプション
    1: ElementType.FOOTNOTE,       # 脚注
    2: ElementType.FORMULA,        # 数式
    3: ElementType.LIST_ITEM,      # リストアイテム
    4: ElementType.PAGE_FOOTER,    # ページフッター
    5: ElementType.PAGE_HEADER,    # ページヘッダー
    6: ElementType.PICTURE,        # 画像
    7: ElementType.SECTION_HEADER, # セクションヘッダー
    8: ElementType.TABLE,          # テーブル
    9: ElementType.TEXT,           # テキスト
    10: ElementType.TITLE,         # タイトル
}

# 逆マッピング: ElementType -> ラベルID
ELEMENT_TYPE_TO_LABEL: Dict[ElementType, int] = {
    v: k for k, v in YOLOX_LABEL_MAP.items()
}

# 可視化用の色マッピング（RGB）
ELEMENT_COLORS: Dict[ElementType, Tuple[int, int, int]] = {
    ElementType.CAPTION: (255, 0, 0),        # 赤 - キャプション
    ElementType.FOOTNOTE: (255, 165, 0),     # オレンジ - 脚注
    ElementType.FORMULA: (128, 0, 128),      # 紫 - 数式
    ElementType.LIST_ITEM: (0, 0, 255),      # 青 - リストアイテム
    ElementType.PAGE_FOOTER: (128, 128, 128), # グレー - ページフッター
    ElementType.PAGE_HEADER: (255, 192, 203), # ピンク - ページヘッダー
    ElementType.PICTURE: (255, 0, 255),      # マゼンタ - 画像
    ElementType.SECTION_HEADER: (255, 215, 0), # ゴールド - セクションヘッダー
    ElementType.TABLE: (255, 255, 0),        # 黄 - テーブル
    ElementType.TEXT: (0, 255, 0),           # 緑 - テキスト
    ElementType.TITLE: (255, 69, 0),         # 赤オレンジ - タイトル
    
    # 後方互換性
    ElementType.NARRATIVE_TEXT: (0, 255, 0),  # 緑 - 本文テキスト（TEXTと同じ）
    ElementType.IMAGE: (255, 0, 255),         # マゼンタ - 画像（PICTUREと同じ）
    ElementType.HEADER: (255, 192, 203),      # ピンク - ヘッダー（PAGE_HEADERと同じ）
    ElementType.FOOTER: (128, 128, 128),      # グレー - フッター（PAGE_FOOTERと同じ）
}

# 日本語表示名マッピング
ELEMENT_JAPANESE_NAMES: Dict[ElementType, str] = {
    ElementType.CAPTION: "キャプション",
    ElementType.FOOTNOTE: "脚注",
    ElementType.FORMULA: "数式",
    ElementType.LIST_ITEM: "リストアイテム",
    ElementType.PAGE_FOOTER: "ページフッター",
    ElementType.PAGE_HEADER: "ページヘッダー",
    ElementType.PICTURE: "画像",
    ElementType.SECTION_HEADER: "セクションヘッダー",
    ElementType.TABLE: "テーブル",
    ElementType.TEXT: "テキスト",
    ElementType.TITLE: "タイトル",
    ElementType.NARRATIVE_TEXT: "本文テキスト",
    ElementType.IMAGE: "画像",
    ElementType.HEADER: "ヘッダー",
    ElementType.FOOTER: "フッター",
}

def get_element_type_from_label(label_id: int) -> Optional[ElementType]:
    """
    YOLOXラベルIDからElementTypeを取得
    
    Args:
        label_id: YOLOXモデルが出力するラベルID (0-10)
        
    Returns:
        対応するElementType、存在しない場合はNone
    """
    return YOLOX_LABEL_MAP.get(label_id)

def get_label_from_element_type(element_type: ElementType) -> Optional[int]:
    """
    ElementTypeからYOLOXラベルIDを取得
    
    Args:
        element_type: 要素タイプ
        
    Returns:
        対応するラベルID、存在しない場合はNone
    """
    return ELEMENT_TYPE_TO_LABEL.get(element_type)

def get_element_color(element_type: ElementType) -> Tuple[int, int, int]:
    """
    ElementTypeに対応する可視化用の色を取得
    
    Args:
        element_type: 要素タイプ
        
    Returns:
        RGB色タプル、デフォルトはグレー
    """
    return ELEMENT_COLORS.get(element_type, (128, 128, 128))

def get_element_japanese_name(element_type: ElementType) -> str:
    """
    ElementTypeの日本語表示名を取得
    
    Args:
        element_type: 要素タイプ
        
    Returns:
        日本語表示名、デフォルトは英語名
    """
    return ELEMENT_JAPANESE_NAMES.get(element_type, element_type.value)

def normalize_element_type(element_type_str: str) -> Optional[ElementType]:
    """
    文字列からElementTypeを正規化
    Unstructured.ioの様々な表記に対応
    
    Args:
        element_type_str: 要素タイプの文字列表現
        
    Returns:
        正規化されたElementType、存在しない場合はNone
    """
    # 大文字小文字を無視して検索
    element_type_str = element_type_str.strip()
    
    # 直接マッチング
    for element_type in ElementType:
        if element_type.value.lower() == element_type_str.lower():
            return element_type
    
    # 一般的な別名のマッピング
    aliases = {
        'narrativetext': ElementType.NARRATIVE_TEXT,
        'narrative_text': ElementType.NARRATIVE_TEXT,
        'text': ElementType.TEXT,
        'image': ElementType.PICTURE,  # ImageはPictureにマップ
        'picture': ElementType.PICTURE,
        'header': ElementType.PAGE_HEADER,  # HeaderはPageHeaderにマップ
        'footer': ElementType.PAGE_FOOTER,  # FooterはPageFooterにマップ
        'pageheader': ElementType.PAGE_HEADER,
        'page_header': ElementType.PAGE_HEADER,
        'pagefooter': ElementType.PAGE_FOOTER,
        'page_footer': ElementType.PAGE_FOOTER,
        'sectionheader': ElementType.SECTION_HEADER,
        'section_header': ElementType.SECTION_HEADER,
        'listitem': ElementType.LIST_ITEM,
        'list_item': ElementType.LIST_ITEM,
    }
    
    return aliases.get(element_type_str.lower())

def get_all_supported_types() -> Dict[int, str]:
    """
    サポートされているすべての要素タイプを取得
    
    Returns:
        ラベルID -> 日本語名のマッピング
    """
    return {
        label_id: get_element_japanese_name(element_type)
        for label_id, element_type in YOLOX_LABEL_MAP.items()
    }

if __name__ == "__main__":
    # テスト用のコード
    print("YOLOX標準ラベルマッピング:")
    print("=" * 50)
    
    for label_id, element_type in YOLOX_LABEL_MAP.items():
        japanese_name = get_element_japanese_name(element_type)
        color = get_element_color(element_type)
        print(f"ID {label_id:2d}: {element_type.value:15s} ({japanese_name}) - RGB{color}")
    
    print("\nサポートされている要素タイプ:")
    print("=" * 30)
    supported_types = get_all_supported_types()
    for label_id, name in supported_types.items():
        print(f"  {label_id}: {name}")
