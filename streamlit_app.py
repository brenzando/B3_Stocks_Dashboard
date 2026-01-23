import streamlit as st
from seaborn import heatmap
import matplotlib.pyplot as plt
from services import load_ticker_history, load_ticker_info_today, statistics_historical_data, df_stocks_close, df_returns, df_stocks_returns_ranking, df_stocks_returns_period, df_annualized_volatility, df_coefficient_variation
from config import STOCKS, STOCKS_DEFAULT, PERIODS

def main():
    
    """Main application entry point for the B3 Stocks Dashboard.
    
    Initializes and displays a comprehensive Streamlit dashboard for analyzing Brazilian stock market data.
    The dashboard includes:
    - Individual stock analysis with real-time quotes and historical statistics
    - Multiple stock comparison with returns, volatility, and correlation analysis
    - Interactive visualizations including price charts, heatmaps, and bar charts
    - Company information and key metrics
    
    The interface is organized in two main sections:
    1. Left column: Stock selection, period selection, and statistics display
    2. Main area: Charts, correlations, and comparative analysis of multiple stocks
    """


    st.set_page_config(page_title='B3 - Stocks Dashboard', layout='wide')

    col1, col2 = st.columns([0.25, 0.75])

    with col1:
        
        with st.container(width='stretch', vertical_alignment='center', horizontal_alignment='left'):
            st.image(image = 'image/B3_Logo.png', width=170)

        with st.container(border=True, width='stretch', height='content'):

            period = st.pills('Period', options=PERIODS, selection_mode='single', default='1y', key='period')
            stock_selected = st.selectbox('Stock Ticker', options=STOCKS)

            df_stock = load_ticker_history(stock_selected, period)
            stats = statistics_historical_data(df_stock)
            ticker_info = load_ticker_info_today(stock_selected)

            with st.popover(f'About', use_container_width = True): # About 
                
                st.markdown(f'## {ticker_info['Long Name']}')

                business_summary = ticker_info['Summary']
                for paragraph in business_summary.split('. '):
                   st.write(paragraph.strip() + '.')
                
                st.write(f'**Website:** {ticker_info['Web Site']}')
                st.write(f'**Sector:** {ticker_info['Sector']} | **Industry:** {ticker_info['Industry']}')

        with st.container(border=True, width='stretch', height='content'):

            cumulative_return = stats["Cumulative Return"]
            average_price = stats["Mean Price"]
            standard_deviation = stats["Standard Deviation"]
            high_price = stats["High Price"]
            volatility = stats["Volatility"]
            median_price = stats["Median Price"]
            coef_variation = stats["Coefficient Variation"]
            low_price = stats["Low Price"]

            st.markdown('#### Statistics for the period')

            col10, col20 = st.columns(2)

            with col10:
                
                st.metric(label='Cumulative Return', value=f'{cumulative_return:,.2f}%')
                st.metric(label='Average Price', value=f'R$ {average_price:,.2f}')
                st.metric(label='Standard Deviation', value=f'R$ {standard_deviation:,.2f}')
                st.metric(label='High Price', value=f'R$ {high_price:,.2f}')

            with col20:

                st.metric(label='Annualized Volatility', value=f'{volatility:.2f}%')
                st.metric(label='Median Price', value=f'R$ {median_price:,.2f}')
                st.metric(label='Coefficient Variation', value=f'{coef_variation:.2f}%')
                st.metric(label='Low Price', value=f'R$ {low_price:,.2f}')      
            
    with col2:

        with st.container(vertical_alignment='bottom', height='content', border=False, width='stretch'):

            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.16, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14], vertical_alignment='center')

            with col1:
                st.markdown(f'## {stock_selected} ')

            with col2:
                st.metric(label='Change %', value=f'{ticker_info['Pct Today']:,.2f}%')
                
            with col3:
                st.metric(label='Last Price', value=f'R$ {ticker_info['Last Price']:,.2f}')
                
            with col4:
                st.metric(label='Previous Close', value=f'R$ {ticker_info['Previous Close']:,.2f}')
                
            with col5:
                st.metric(label='Open Price', value=f'R$ {ticker_info['Open Price']:,.2f}')
                
            with col6:
                st.metric(label='Day High', value=f'R$ {ticker_info['Day High']:,.2f}')
                
            with col7:
                st.metric(label='Day Low', value=f'R$ {ticker_info['Day Low']:,.2f}')

        with st.container(border=True, height=685, width='stretch'):

            st.line_chart(data = df_stock, x = 'Date', y = 'Close', height='stretch', width='stretch', x_label='Dates', y_label='Close Prices (R$)')
        
    st.markdown('## Statistical Analyses')

    col1, col2 = st.columns([0.25, 0.75])

    with col1:

        with st.container(border=True, width='stretch', height='content'):

            stocks_selected = STOCKS_DEFAULT

            stocks_period = st.pills('Period', options=PERIODS, selection_mode='single', default='1y', key='stocks_period')
            stocks_list = st.multiselect('Stock Tickers', options=STOCKS, default=stocks_selected)
            st.caption('Select at least two or more stocks to analyze Cumulative Returns, Correlations, and Volatility Metrics.')

            df_close_prices = df_stocks_close(stocks_period, stocks_list)
            df_close_returns = df_returns(df_close_prices)
            df_returns_period = df_stocks_returns_period(df_close_returns) 
            df_cumulative_returns = df_stocks_returns_ranking(df_close_returns)
            corr_matrix = df_close_returns.corr()
            annualized_volatility = df_annualized_volatility(df_close_returns)
            coefficient_variation = df_coefficient_variation(df_close_prices)

    with col2:

        if not stocks_list or len(stocks_list) == 1:
            st.warning('Please, select at least two stocks for analysis.')
            st.stop()

        col1, col2 = st.columns([0.5, 0.5])

        with col1:

            with st.container(border=True, height=500, width='stretch'):

                st.markdown('### Cumulative Returns (%)')
                st.line_chart(data=df_returns_period, height='stretch', width='stretch', x_label='Dates', y_label='Cumulative Returns (%)')

        with col2:

            with st.container(border=True, height=500, width='stretch'):

                st.markdown('### Correlation Heatmap')

                plt.figure(figsize=(12, 6.5))
                heatmap(corr_matrix, annot=True, cmap='Blues', vmin=-1, vmax=1)
                st.pyplot(plt, width='stretch')
        
        with st.container():
            
            col1, col2, col3 = st.columns(3)

            with col1:

                with st.container(border=True, height=500, width='stretch'):

                    st.markdown('### Cumulative Returns (%)')

                    st.bar_chart(data= df_cumulative_returns, x = 'Ticker', y = 'Cumulative Return', horizontal = True, sort=False, y_label='Tickers', x_label='Cumulative Returns (%)', height='stretch', width='stretch')
                    
            with col2:

                with st.container(border=True, height=500, width='stretch'):

                    st.markdown('### Annualized Volatility (%)')

                    st.bar_chart(data=annualized_volatility, x = 'Ticker', y = 'Annualized Volatility', horizontal=True, sort=False, y_label= 'Tickers', x_label='Annualized Volatitlity (%)', height='stretch', width='stretch')
                    
            with col3:

                with st.container(border=True, height=500, width='stretch'):

                    st.markdown('### Coefficient Variation (%)')

                    st.bar_chart(data=coefficient_variation, x = 'Ticker', y = 'Coefficient Variation', horizontal=True, sort=False, y_label='Tickers', x_label='Coefficient Variation (%)', height='stretch', width='stretch')
                    
                    
if __name__ == '__main__':
    main()
    
    

 
    
    
    
    
    
    
    
    
    
    
    
    
    
    