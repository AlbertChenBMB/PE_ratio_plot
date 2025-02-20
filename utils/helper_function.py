import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def plot_pe_analysis(df,symbol,std=1):
    """
    繪製 PE ratio 分析圖
    包含：PE 走勢、平均線、±1倍標準差線

    Parameters:
    df: 包含 'Date' 和 'Forward_PE' 的 DataFrame
    """
    # 計算統計值
    mean_pe = df['Forward_PE'].mean()
    std_pe = df['Forward_PE'].std()
    upper_band = mean_pe + std*std_pe
    lower_band = mean_pe - std*std_pe

    # 創建圖表
    fig = go.Figure()

    # 添加 PE ratio 主線
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Forward_PE'],
            name='Forward PE',
            line=dict(color='blue'),
            mode='lines'
        )
    )

    # 添加平均線
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=[mean_pe] * len(df),
            name='Mean',
            line=dict(color='red', dash='dash'),
            mode='lines'
        )
    )

    # 添加上方標準差線
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=[upper_band] * len(df),
            name='Mean + 1σ',
            line=dict(color='gray', dash='dot'),
            mode='lines'
        )
    )

    # 添加下方標準差線
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=[lower_band] * len(df),
            name='Mean - 1σ',
            line=dict(color='gray', dash='dot'),
            mode='lines'
        )
    )

    # 更新布局
    fig.update_layout(
        title=dict(
            text=f'{symbol} Forward PE Ratio Analysis',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Date',
        yaxis_title='Forward PE Ratio',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        # 添加網格線
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
        # 設置背景顏色
        plot_bgcolor='white'
    )

    # 添加統計資訊的註解
    fig.add_annotation(
        text=f'Mean: {mean_pe:.2f}<br>Std Dev: {std_pe:.2f}',
        xref='paper',
        yref='paper',
        x=0.02,
        y=0.98,
        showarrow=False,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='gray',
        borderwidth=1
    )

    return fig




def get_pe_history(ticker):
    """
    從 GuruFocus 獲取股票的歷史 Forward PE ratio 數據

    Parameters:
    ticker (str): 股票代號，例如 'AAPL'

    Returns:
    DataFrame: 包含歷史 Forward PE ratio 數據的 DataFrame
    """
    try:
        # 建立 headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 構建 URL
        url = f'https://www.gurufocus.com/term/forward-pe-ratio/{ticker}'

        # 發送請求
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 解析網頁內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有的 strong 標籤
        all_strongs = soup.find_all('strong')
        company_data = None
        for strong in all_strongs:
            if strong.string and 'Quarterly Data' in strong.string:
                company_data = strong
                break

        if not company_data:
            print(f"無法找到 {ticker} 的季度數據表格")
            return None

        # 找到表格主體
        table = company_data.find_parent('table')
        if not table:
            print("無法找到數據表格")
            return None

        # 初始化列表來存儲數據
        dates = []
        pe_values = []

        # 找到所有日期
        for strong in table.find_all('strong'):
            if strong.string and '-' in strong.string:
                dates.append(strong.string.strip())

        # 找到包含 "Forward PE Ratio" 的行
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if tds and tds[0].string and 'Forward PE Ratio' in tds[0].string:
                # PE 值在同一行的其他 td 元素中
                pe_values = [td.string.strip() for td in tds[1:] if td.string]
                break

        # 印出找到的原始數據以便偵錯
        print(f"找到的日期: {dates}")
        print(f"找到的 PE 值: {pe_values}")

        # 確保數據長度相同
        min_length = min(len(dates), len(pe_values))
        dates = dates[:min_length]
        pe_values = pe_values[:min_length]

        # 創建 DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Forward_PE': pe_values
        })

        # 轉換日期格式
        df['Date'] = pd.to_datetime(df['Date'])

        # 轉換 PE 值為浮點數
        df['Forward_PE'] = pd.to_numeric(df['Forward_PE'], errors='coerce')

        # 按日期排序
        df = df.sort_values('Date', ascending=False)

        # 重設索引
        df = df.reset_index(drop=True)

        print(f"成功獲取 {ticker} 的 Forward PE ratio 歷史數據")

        return df

    except Exception as e:
        print(f"處理 {ticker} 時發生錯誤: {e}")
        print("錯誤詳細資訊:", e.__class__.__name__)
        import traceback
        print(traceback.format_exc())
        return None

# 測試函數
def test_pe_history():
    ticker = 'AAPL'
    df = get_pe_history(ticker)

    if df is not None:
        print("\n資料預覽:")
        print(df.head())
        print(f"\n總資料筆數: {len(df)}")

        # 檢查是否有遺漏值
        print("\n遺漏值統計:")
        print(df.isnull().sum())

if __name__ == "__main__":
    test_pe_history()
