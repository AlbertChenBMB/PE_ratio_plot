import streamlit as st
from utils.helper_function import *


# 或者使用更通用的方式隱藏所有警告
import warnings


def main():
    warnings.filterwarnings('ignore')
    # 設置頁面標題
    st.set_page_config(
        page_title="股票 Forward PE 分析工具",
        page_icon="📈",
        layout="wide"
    )

    # 標題
    st.title("股票 Forward PE 分析工具 📊")

    # 側邊欄說明
    with st.sidebar:
        st.header("使用說明")
        st.write("""
        1. 在下方輸入股票代號（例如：AAPL）
        2. 點擊分析按鈕
        3. 等待數據載入和圖表生成
        """)

        st.markdown("---")
        st.markdown("### 關於")
        st.write("本工具使用 GuruFocus 的數據")

    # 主要內容
    col1, col2 = st.columns([2, 3])

    with col1:
        # 輸入區域
        ticker = st.text_input("請輸入股票代號：", value="AAPL").upper()
        analyze_button = st.button("開始分析")

    # 當按下分析按鈕時
    if analyze_button:
        with st.spinner(f'正在分析 {ticker} 的數據...'):
            try:
                # 獲取數據
                df = get_pe_history(ticker)

                if df is not None and not df.empty:
                    # 顯示基本統計資訊
                    st.subheader("統計摘要")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("平均 PE", f"{df['Forward_PE'].mean():.2f}")
                    with col2:
                        st.metric("最大值", f"{df['Forward_PE'].max():.2f}")
                    with col3:
                        st.metric("最小值", f"{df['Forward_PE'].min():.2f}")

                    # 顯示圖表
                    st.subheader("PE 走勢分析")
                    fig = plot_pe_analysis(df,symbol=ticker)
                    st.plotly_chart(fig, use_container_width=True)

                    # 顯示原始數據
                    with st.expander("查看原始數據"):
                        st.dataframe(df)

                else:
                    st.error(f"無法獲取 {ticker} 的數據，請確認股票代號是否正確。")

            except Exception as e:
                st.error(f"發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()
