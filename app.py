import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import time
import threading
import queue
import tempfile
import os
from unstructured.partition.image import partition_image
from unstructured.staging.base import elements_to_json
import json

# YOLOX標準ラベルマッピングをインポート
from yolox_labels import (
    YOLOX_LABEL_MAP,
    ELEMENT_COLORS,
    get_element_color,
    normalize_element_type
)

# 設定をインポート
from config import (
    get_unstructured_config,
    get_language_info,
    UI_CONFIG,
    VISUALIZATION_CONFIG
)

class LayoutParserApp:
    def __init__(self):
        # ログメッセージを保存するキュー
        self.log_queue = queue.Queue()
        self.current_logs = ""

    def add_log(self, message):
        """ログメッセージを追加"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.current_logs += log_entry
        return self.current_logs

    def verify_coordinates_integrity(self, original_coords, processed_coords):
        """
        座標の整合性を検証（原滋原味の確認）

        Args:
            original_coords: 元の座標
            processed_coords: 処理後の座標

        Returns:
            bool: 座標が変更されていない場合True
        """
        try:
            if isinstance(original_coords, (list, tuple)) and isinstance(processed_coords, (list, tuple)):
                if len(original_coords) != len(processed_coords):
                    return False

                # 数値の比較（小数点以下の誤差を考慮）
                for orig, proc in zip(original_coords, processed_coords):
                    if abs(float(orig) - float(proc)) > 0.001:  # 1ピクセル未満の誤差は許容
                        return False
                return True

            return str(original_coords) == str(processed_coords)
        except:
            return False

    def process_image(self, image, progress=gr.Progress()):
        """画像を処理してレイアウト解析を実行"""
        if image is None:
            return None, self.add_log("エラー: 画像がアップロードされていません")

        try:
            # ログを初期化
            self.current_logs = ""
            logs = self.add_log("レイアウト解析を開始しています...")
            yield None, logs

            # 一時ファイルに画像を保存
            progress(0.1, desc="画像を準備中...")
            logs = self.add_log("画像を一時ファイルに保存中...")
            yield None, logs

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                image.save(tmp_file.name, 'PNG')
                temp_image_path = tmp_file.name

            # Unstructured.ioを使用してレイアウト解析
            progress(0.3, desc="Unstructured.ioでレイアウト解析中...")
            logs = self.add_log("Unstructured.ioライブラリを使用してレイアウト解析を実行中...")

            # 言語設定情報を表示
            lang_info = get_language_info()
            lang_names = ", ".join(lang_info['names'])
            logs = self.add_log(f"言語設定: {lang_names} ({len(lang_info['codes'])}言語)")
            yield None, logs

            # 画像からエレメントを抽出（設定ファイルから言語を取得）
            unstructured_config = get_unstructured_config()
            logs = self.add_log("設定: 新しいsize形式を使用（max_size廃止対応）")
            yield None, logs

            elements = partition_image(
                filename=temp_image_path,
                **unstructured_config  # 設定ファイルからすべての設定を適用
            )

            progress(0.6, desc="解析結果を処理中...")
            logs = self.add_log("抽出されたエレメントを処理中...")
            yield None, logs

            # エレメントの詳細をログに出力
            element_counts = {}
            element_details = []

            for i, element in enumerate(elements):
                element_type = type(element).__name__
                element_counts[element_type] = element_counts.get(element_type, 0) + 1

                # エレメントの詳細情報を収集（原始座標情報を保持）
                metadata = getattr(element, 'metadata', None)
                metadata_info = "なし"
                coordinates_info = "座標なし"

                if metadata:
                    if hasattr(metadata, 'coordinates'):
                        coordinates = metadata.coordinates
                        metadata_info = f"座標あり: {type(coordinates).__name__}"

                        # 原始座標情報を記録
                        if hasattr(coordinates, 'points'):
                            points = coordinates.points
                            if len(points) <= 4:
                                coordinates_info = f"Points: {points}"
                            else:
                                coordinates_info = f"Points: {len(points)}個のポイント"
                        elif isinstance(coordinates, (list, tuple)):
                            coordinates_info = f"直接座標: {coordinates}"
                        else:
                            coordinates_info = f"座標オブジェクト: {type(coordinates).__name__}"
                    else:
                        metadata_info = f"メタデータあり: {type(metadata).__name__}"

                element_info = {
                    'type': element_type,
                    'text': str(element)[:100] + '...' if len(str(element)) > 100 else str(element),
                    'metadata': metadata_info,
                    'coordinates': coordinates_info
                }
                element_details.append(element_info)

            # ログに結果を出力
            logs = self.add_log(f"解析完了！検出されたエレメント数: {len(elements)}")
            for elem_type, count in element_counts.items():
                logs = self.add_log(f"  - {elem_type}: {count}個")

            progress(0.8, desc="結果画像を生成中...")
            logs = self.add_log("解析結果を可視化した画像を生成中...")
            logs = self.add_log("重要: 座標は原滋原味（オリジナルのまま）を保持します")
            yield None, logs

            # 結果を可視化した画像を生成
            processed_image = self.create_result_with_unstructured(image, elements)

            # 一時ファイルを削除
            os.unlink(temp_image_path)

            progress(1.0, desc="完了")
            logs = self.add_log("レイアウト解析が正常に完了しました！")

            # 詳細な解析結果をログに追加（座標情報も含む）
            for i, detail in enumerate(element_details[:5]):  # 最初の5個のエレメントのみ表示
                coord_info = detail.get('coordinates', '座標なし')
                logs = self.add_log(f"エレメント{i+1}: {detail['type']} ({detail['metadata']}) - {coord_info}")
                logs = self.add_log(f"  テキスト: {detail['text']}")

            if len(element_details) > 5:
                logs = self.add_log(f"... 他 {len(element_details) - 5} 個のエレメント")

            yield processed_image, logs

        except Exception as e:
            error_logs = self.add_log(f"エラーが発生しました: {str(e)}")
            # 一時ファイルがある場合は削除
            try:
                if 'temp_image_path' in locals():
                    os.unlink(temp_image_path)
            except:
                pass
            yield None, error_logs

    def create_result_with_unstructured(self, original_image, elements):
        """
        Unstructured.ioの解析結果を可視化した画像を生成
        重要: 座標は原滋原味（オリジナルのまま）を保持し、一切の拡張や縮小を行わない
        ラベル: 英語名を使用してエレメントタイプを表示
        """
        # 元の画像をコピー
        result_image = original_image.copy()
        draw = ImageDraw.Draw(result_image)

        # YOLOX_LABEL_MAPと100%統一された色マッピングを使用

        # デフォルトの色（未知のタイプ用）
        default_color = (128, 128, 128)  # グレー

        try:
            # フォントを設定（設定ファイルからサイズを取得）
            font_size = VISUALIZATION_CONFIG["font_size"]
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        except:
            font = None

        # 各エレメントに境界ボックスを描画
        for i, element in enumerate(elements):
            element_type_str = type(element).__name__

            # YOLOX標準ラベルマッピングを使用して色を取得
            element_type = normalize_element_type(element_type_str)
            if element_type:
                color = get_element_color(element_type)
                english_name = element_type.value  # 英語名を使用
            else:
                color = default_color
                english_name = element_type_str  # 元の英語名をそのまま使用

            # メタデータから座標情報を取得（もしあれば）
            metadata = getattr(element, 'metadata', None)
            coordinates = None

            if metadata:
                # ElementMetadataオブジェクトの場合
                if hasattr(metadata, 'coordinates'):
                    coordinates = metadata.coordinates
                elif hasattr(metadata, '__dict__') and 'coordinates' in metadata.__dict__:
                    coordinates = metadata.__dict__['coordinates']

            if coordinates:
                # 座標がある場合は実際の位置に描画
                try:
                    # coordinatesの構造を確認して適切に処理
                    points = None

                    if hasattr(coordinates, 'points'):
                        points = coordinates.points
                    elif hasattr(coordinates, '__dict__') and 'points' in coordinates.__dict__:
                        points = coordinates.__dict__['points']
                    elif isinstance(coordinates, (list, tuple)) and len(coordinates) >= 4:
                        # 直接座標リストの場合 [x1, y1, x2, y2] - 原滋原味を保持
                        x1, y1, x2, y2 = coordinates[:4]
                        # 原始座標をそのまま使用（整数変換のみ）
                        bbox_width = VISUALIZATION_CONFIG["bbox_width"]
                        label_offset = VISUALIZATION_CONFIG["label_offset"]
                        draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline=color, width=bbox_width)
                        if font:
                            draw.text((int(x1), int(y1)-label_offset), english_name, fill=color, font=font)
                        else:
                            draw.text((int(x1), int(y1)-label_offset), english_name, fill=color)
                        continue

                    if points and len(points) >= 2:
                        # pointsから座標を抽出（原滋原味を保持）
                        if len(points) >= 4:
                            # 4つ以上のポイントがある場合（矩形）
                            # 原始座標をそのまま使用し、ポリゴンとして描画
                            polygon_points = [(int(p[0]), int(p[1])) for p in points]
                            # ポリゴンの境界線を描画
                            bbox_width = VISUALIZATION_CONFIG["bbox_width"]
                            for j in range(len(polygon_points)):
                                start_point = polygon_points[j]
                                end_point = polygon_points[(j + 1) % len(polygon_points)]
                                draw.line([start_point, end_point], fill=color, width=bbox_width)

                            # ラベル用の座標（最初のポイントを使用）
                            x1, y1 = points[0]
                        else:
                            # 2つのポイントの場合（矩形として扱う）
                            x1, y1 = points[0]
                            x2, y2 = points[1]
                            # 原始座標をそのまま使用して矩形を描画
                            bbox_width = VISUALIZATION_CONFIG["bbox_width"]
                            draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline=color, width=bbox_width)

                        # エレメントタイプのラベルを描画（英語名を使用）
                        label_offset = VISUALIZATION_CONFIG["label_offset"]
                        if font:
                            draw.text((int(x1), int(y1)-label_offset), english_name, fill=color, font=font)
                        else:
                            draw.text((int(x1), int(y1)-label_offset), english_name, fill=color)
                except Exception as coord_error:
                    # 座標の処理でエラーが発生した場合は、デフォルトの配置にフォールバック
                    pass
            # 座標がない場合、またはエラーが発生した場合は、画像上に順番に配置
            if not coordinates or 'coord_error' in locals():
                _, img_height = original_image.size
                box_height = VISUALIZATION_CONFIG["fallback_box_height"]
                box_width = VISUALIZATION_CONFIG["fallback_box_width"]
                bbox_width = VISUALIZATION_CONFIG["bbox_width"]
                y_pos = (i * box_height) % (img_height - box_height)
                x_pos = 10

                # 簡単な境界ボックスを描画
                draw.rectangle([x_pos, y_pos, x_pos + box_width, y_pos + box_height],
                             outline=color, width=bbox_width)

                # エレメントタイプのラベルを描画（英語名を使用）
                if font:
                    draw.text((x_pos + 5, y_pos + 5), f"{english_name} {i+1}", fill=color, font=font)
                else:
                    draw.text((x_pos + 5, y_pos + 5), f"{english_name} {i+1}", fill=color)

        return result_image

    def create_demo_result(self, original_image):
        """デモ用の処理結果画像を生成（フォールバック用）"""
        # 元の画像をコピー
        img_array = np.array(original_image)

        # 簡単な境界ボックスを描画（デモ用）
        height, width = img_array.shape[:2]

        # 赤い境界ボックスを追加
        # 上部のテキスト領域
        img_array[50:52, 50:width-50] = [255, 0, 0]  # 上辺
        img_array[150:152, 50:width-50] = [255, 0, 0]  # 下辺
        img_array[50:150, 50:52] = [255, 0, 0]  # 左辺
        img_array[50:150, width-52:width-50] = [255, 0, 0]  # 右辺

        # 中央の画像領域（もし画像が十分大きい場合）
        if height > 300:
            img_array[200:202, 50:width//2-10] = [0, 255, 0]  # 上辺
            img_array[height//2:height//2+2, 50:width//2-10] = [0, 255, 0]  # 下辺
            img_array[200:height//2, 50:52] = [0, 255, 0]  # 左辺
            img_array[200:height//2, width//2-12:width//2-10] = [0, 255, 0]  # 右辺

        return Image.fromarray(img_array)

def create_interface():
    """Gradio インターフェースを作成"""
    app = LayoutParserApp()

    # 設定ファイルからUI設定を取得
    theme_map = {"soft": gr.themes.Soft()}
    theme = theme_map.get(UI_CONFIG["theme"], gr.themes.Soft())

    with gr.Blocks(title=UI_CONFIG["title"], theme=theme) as demo:
        gr.Markdown(f"# 📄 {UI_CONFIG['title']}")
        gr.Markdown(UI_CONFIG["description"])

        # 言語設定情報を表示
        lang_info = get_language_info()
        gr.Markdown(f"**🌐 言語設定**: {', '.join(lang_info['names'])} ({len(lang_info['codes'])}言語)")

        # 第1行: 1:3の比率で左右に分割
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 画像アップロード")
                image_input = gr.Image(
                    label="解析する画像をアップロード",
                    type="pil",
                    height=200
                )
                parse_button = gr.Button(
                    "🚀 解析開始",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=3):
                gr.Markdown("### 📋 実行ログ")
                log_output = gr.Textbox(
                    label="",
                    lines=10,
                    max_lines=15,
                    interactive=False,
                    show_label=False,
                    placeholder="ここに実行ログが表示されます..."
                )

        # 第2行: 1:1の比率で左右に分割
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🖼️ 元画像プレビュー")
                original_preview = gr.Image(
                    label="",
                    show_label=False,
                    interactive=False,
                    height=400
                )

            with gr.Column(scale=1):
                gr.Markdown("### ✨ 解析結果プレビュー")
                result_preview = gr.Image(
                    label="",
                    show_label=False,
                    interactive=False,
                    height=400
                )

        # イベントハンドラー
        def update_preview(image):
            """画像アップロード時にプレビューを更新"""
            return image

        # 画像アップロード時にプレビューを更新
        image_input.change(
            fn=update_preview,
            inputs=[image_input],
            outputs=[original_preview]
        )

        # 解析ボタンクリック時の処理
        parse_button.click(
            fn=app.process_image,
            inputs=[image_input],
            outputs=[result_preview, log_output],
            show_progress=True
        )

    return demo

if __name__ == "__main__":
    # インターフェースを作成して起動（設定ファイルから設定を取得）
    demo = create_interface()

    # 起動時に言語設定を表示
    lang_info = get_language_info()
    print(f"🌐 言語設定: {', '.join(lang_info['names'])} ({len(lang_info['codes'])}言語)")
    print(f"🚀 サーバーを起動中... http://{UI_CONFIG['server_name']}:{UI_CONFIG['server_port']}")

    demo.launch(**{k: v for k, v in UI_CONFIG.items() if k not in ['title', 'description', 'theme']})
