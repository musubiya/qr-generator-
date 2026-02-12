"""
QRコード生成 Streamlit アプリケーション

URLからQRコードを生成し、短縮URL生成・PNGダウンロードができるWebアプリケーション。
"""

import io
from typing import Optional

import qrcode
import streamlit as st
from PIL import Image
from qrcode.image.pil import PilImage


# ---------------------------------------------------------------------------
# ページ設定
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="QRコード生成ツール",
    page_icon="",
    layout="centered",
)

# ---------------------------------------------------------------------------
# カスタムCSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 背景 */
    .stApp {
        background: linear-gradient(160deg, #e0f2fe 0%, #f0f9ff 40%, #e8f4fd 100%);
    }

    /* ヘッダー */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .main-header h1 {
        color: #0369a1;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .main-header p {
        color: #64748b;
        font-size: 1rem;
    }

    /* カード風コンテナ */
    .block-container {
        max-width: 680px;
    }

    /* 入力欄 */
    .stTextInput > div > div,
    .stSelectbox > div > div {
        background: #fff !important;
        border: 1.5px solid #bae6fd !important;
        border-radius: 10px !important;
        color: #1e293b !important;
    }
    .stTextInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15) !important;
    }

    /* ラベル */
    .stTextInput label, .stSelectbox label, .stCheckbox label {
        color: #334155 !important;
    }

    /* ボタン */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9, #38bdf8) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0284c7, #0ea5e9) !important;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* ダウンロードボタン */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0d9488, #14b8a6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 4px 16px rgba(13, 148, 136, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* 成功メッセージ */
    .stSuccess {
        background: #ecfdf5 !important;
        border: 1px solid #a7f3d0 !important;
        border-radius: 10px !important;
        color: #065f46 !important;
    }

    /* コードブロック */
    .stCode {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* 区切り線 */
    hr {
        border-color: #bae6fd !important;
    }

    /* QR画像 */
    .stImage {
        background: #fff;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 12px rgba(14, 165, 233, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# ユーティリティ関数
# ---------------------------------------------------------------------------
def generate_qr_image(
    data: str,
    fill_color: str = "black",
    box_size: int = 10,
    border: int = 4,
) -> Image.Image:
    """指定データからQRコード画像（PIL Image）を生成する。

    Args:
        data: QRコードに埋め込むデータ文字列。
        box_size: 各ボックスのピクセルサイズ。
        border: ボーダーのボックス数。

    Returns:
        PIL Image オブジェクト。
    """
    qr = qrcode.QRCode(
        version=None,  # 自動判定
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img: PilImage = qr.make_image(fill_color=fill_color, back_color="white")
    return img.get_image()


def image_to_bytes(img: Image.Image) -> bytes:
    """PIL Image を PNG バイト列に変換する。

    Args:
        img: PIL Image オブジェクト。

    Returns:
        PNGバイト列。
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def display_qr_and_download(
    img: Image.Image,
    download_filename: str = "qrcode.png",
    slider_key: str = "qr_size",
) -> None:
    """QRコード画像を表示し、サイズスライダーとダウンロードボタンを配置する。

    Args:
        img: QRコード画像。
        download_filename: ダウンロード時のファイル名。
        slider_key: スライダーのセッションステートキー。
    """
    qr_size = st.select_slider(
        "画像サイズ (px)",
        options=[200, 300, 400, 500, 600],
        value=400,
        key=slider_key,
    )
    display_width = min(qr_size, 600)
    st.image(img, width=display_width)
    resized = img.resize((qr_size, qr_size), Image.NEAREST)
    png_bytes = image_to_bytes(resized)
    st.caption(f"ダウンロードサイズ: {qr_size} x {qr_size} px")
    st.download_button(
        label="QRコードをダウンロード (PNG)",
        data=png_bytes,
        file_name=download_filename,
        mime="image/png",
        use_container_width=True,
    )


def shorten_url(url: str, service_name: str) -> Optional[str]:
    """指定サービスでURLを短縮する。

    Args:
        url: 短縮したいURL。
        service_name: 短縮サービス名。

    Returns:
        短縮URL文字列。失敗時は None。
    """
    import pyshorteners

    shortener = pyshorteners.Shortener()

    service_map = {
        "TinyURL": shortener.tinyurl,
        "Is.gd": shortener.isgd,
        "Da.gd": shortener.dagd,
        "Clck.ru": shortener.clckru,
    }

    svc = service_map.get(service_name)
    if svc is None:
        return None

    try:
        return svc.short(url)
    except Exception as e:
        st.error(f"URL短縮に失敗しました: {e}")
        return None


# ---------------------------------------------------------------------------
# ヘッダー
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>QR Code Generator</h1>
        <p>URLからQRコードと短縮URLを生成</p>
    </div>
    """,
    unsafe_allow_html=True,
)

url_input = st.text_input(
    "URLを入力",
    placeholder="https://example.com",
    key="url_input",
    help="QRコードに変換したいURLを入力してください。",
)

# --- QRコードの色 ---
color_options = {
    "ブラック": "#000000",
    "ネイビー": "#1e3a5f",
    "緑": "#15803d",
    "青": "#1d4ed8",
    "ピンク": "#db2777",
    "赤": "#dc2626",
}
qr_color_label = st.selectbox(
    "QRコードの色",
    options=list(color_options.keys()),
    key="qr_color",
)
qr_color = color_options[qr_color_label]

# --- URL短縮オプション ---
use_shortener = st.checkbox("短縮URLも生成する", key="use_shortener")

short_url: Optional[str] = None

if use_shortener:
    service = st.selectbox(
        "短縮サービスを選択",
        options=["Is.gd", "Da.gd", "Clck.ru"],
        key="shortener_service",
    )

# --- 生成ボタン ---
if st.button("QRコードを生成", key="btn_url", use_container_width=True):
    if not url_input:
        st.warning("URLを入力してください。")
    elif not url_input.startswith(("http://", "https://")):
        st.warning("URLは http:// または https:// で始めてください。")
    else:
        target_url = url_input

        # 短縮URL生成
        if use_shortener:
            with st.spinner("短縮URLを生成中..."):
                result = shorten_url(url_input, service)
            if result:
                short_url = result
                target_url = short_url

        # QRコード生成
        with st.spinner("QRコードを生成中..."):
            qr_img = generate_qr_image(target_url, fill_color=qr_color)

        # 結果をセッションステートに保存（リラン対策）
        st.session_state["url_qr_img"] = qr_img
        st.session_state["url_target"] = target_url
        if short_url:
            st.session_state["url_short"] = short_url
        else:
            st.session_state.pop("url_short", None)

# --- 結果表示 ---
if "url_qr_img" in st.session_state:
    if "url_short" in st.session_state:
        st.success(f"短縮URL: {st.session_state['url_short']}")
        st.code(st.session_state["url_short"], language=None)
    st.divider()
    display_qr_and_download(
        st.session_state["url_qr_img"],
        download_filename="qrcode_url.png",
        slider_key="url_qr_size",
    )

# ---------------------------------------------------------------------------
# フッター
# ---------------------------------------------------------------------------
st.markdown(
    '<div style="text-align:center; color:#475569; padding:2rem 0 1rem; font-size:0.85rem;">'
    "QR Code Generator v1.0</div>",
    unsafe_allow_html=True,
)
