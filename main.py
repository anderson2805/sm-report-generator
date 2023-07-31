import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from src.generate import create_prompt_info, create_prompt_final
from src.chat import get_chat_response


st.set_page_config(
    layout="wide",
    page_title="SM-GPT",
    page_icon="📃",
)

if "grid_key" not in st.session_state:
    st.session_state.grid_key = 0

st.header("SM-GPT 📃")
st.markdown("""To generate draft SM write-ups, based on selected topics, carefully selected meta data will be send to ChatGPT for generation of draft write-ups.
""")


st.session_state.grid_key += 1

# Read to dataframe from pkl file at data/samples.pkl
sample_df = pd.read_pickle('data/samples.pkl')
sample_df['publishFrom'] = pd.to_datetime(sample_df['publishFrom'])
sample_df['publishTo'] = pd.to_datetime(sample_df['publishTo'])

sample_df.sort_values(by='publishFrom', ascending=False, inplace= True)
st.session_state.sample_df = sample_df
    

# If st.session_state contain nrs_repository_df
if isinstance(st.session_state.get('sample_df', False), pd.DataFrame):
    sample_df = st.session_state.get('sample_df', pd.DataFrame())

    # JsCode that return index of selected rows
    st.write('Select Topics to generate write-ups:')
    
    # All indicies in integer
    gb = GridOptionsBuilder.from_dataframe(sample_df[['publishFrom', 'publishTo', 'topic', 'threadCount', 'postCount', 'mostPopularSentiment','mainZone']])
    gb.configure_pagination(enabled= True, paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_grid_options(domLayout='normal')
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_auto_height(True)
    
    gridOptions = gb.build()

    grid_response = AgGrid(
        sample_df, gridOptions, columns_auto_size_mode=ColumnsAutoSizeMode(2), update_on=['selectionChanged'], enable_enterprise_modules=True, allow_unsafe_jscode=True, reload_data=False)

    def generate_chart(grid_response_selected_rows):
        # Generate a stacked bar charts showing the sentiment distribution of the selected topic
        # grid_response_selected_rows is a list of selected rows
        # Return a chart object

        # Create a dataframe from the selected rows
        chartDf = pd.DataFrame(grid_response_selected_rows)
        # Turn df into stacked bar chart with totalPositiveCount, totalNeutralCount and totalNegativeCount sentiment
        chartDf = chartDf.set_index('chartLabelY')[['pctPositive', 'pctNeutral', 'pctNegative']].stack().reset_index()
        chartDf.columns = ['chartLabelY', 'sentiment', 'count']
        chartDf['sentiment'] = chartDf['sentiment'].str.replace('pct', '')
        chartDf['sentiment'] = chartDf['sentiment'].str.replace('positive', 'Positive')
        chartDf['sentiment'] = chartDf['sentiment'].str.replace('neutral', 'Neutral')
        chartDf['sentiment'] = chartDf['sentiment'].str.replace('negative', 'Negative')
        # Remove decimal places on count
        chartDf['count'] = chartDf['count'].astype(int)
        chartDf['count_label'] = chartDf['count'].astype(str) + '%'

        base = alt.Chart(chartDf)
        chart = base.mark_bar().encode(
            x=alt.X('count', axis=None, stack='normalize'),
            y = alt.Y('chartLabelY', axis=alt.Axis(labelLimit=500), title=None),
            color=alt.Color('sentiment', scale=alt.Scale(
                range=["#3BBD00", "#AAA9A2", "#CF1709"],
                domain=["Positive", "Neutral", "Negative"])),
            order=alt.Order('sentiment'),
        ).properties(
            height=300
        )
        text = base.mark_text(dx=-15, dy=3, align = 'center', color='black', fontSize = 12, fontWeight = 'bold'
            ).encode(
            x=alt.X('count', axis=None, stack='normalize'),
            y = alt.Y('chartLabelY', axis=alt.Axis(labelLimit=500), title=None),
            order=alt.Order('sentiment'),
            text=alt.Text('count_label')
            ).properties(
            height=300
        )


        return (chart + text)


    st.markdown('---')
    if st.session_state.get('prev_selection', 0) != len(grid_response.selected_rows):
        st.session_state['prompt1'] = create_prompt_info(grid_response.selected_rows)
        c = generate_chart(grid_response.selected_rows)
        st.altair_chart(c, use_container_width=True, theme="streamlit")
    st.session_state['prev_selection'] = len(grid_response.selected_rows)
    st.slider('Temperature', min_value=0.0, max_value=2.0, value=0.5, step=0.1, key='temperature', help = 'What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.')
    with st.form("form_1"):
        prompt1 = st.text_area('Prompt 1: Generate summary for each topics', height=500, key='prompt1', disabled = False)
        send1 = st.form_submit_button('Generate Summary for each topics', use_container_width=True)
        if (send1):
            st.session_state['first_cut'] = get_chat_response(st.session_state['prompt1'], st.session_state.temperature)
            st.session_state['prompt2'] = create_prompt_final(st.session_state['first_cut'])

    with st.form("form_2"):
        prompt2 = st.text_area('Prompt 2: Summarised for write-ups detail level', height=500, key='prompt2', disabled = False)
        send2 = st.form_submit_button('Generate write-up', use_container_width=True)
        if (send2):
            st.session_state['final_cut'] = get_chat_response(prompt2, st.session_state.temperature)       
    

    # with st.form("form_2"):
    #     if send1 or st.session_state.get('prompt2', False) or st.session_state.get('send2_save', False):
    #         prompt2 = st.text_area('Prompt 2: Add information to generate the NR.', height=500, key='prompt2', disabled = False)
    #         send2_1, blank2, send2_2 = st.columns([5,1,1])
    #         with send2_2:
    #             st.write('\n \n ')
    #             send2 = st.form_submit_button('Generate Draft Report', use_container_width=True)
    #         with send2_1:
    #             st.slider('Temperature', min_value=0.0, max_value=1.0, value=0.0, step=0.1, key='temperature')
    #         if send2:
    #             st.session_state['send2_save'] = True
    #             with st.spinner('Calling ChatGPT... Generating report...'):
    #                 st.session_state['draft_report'] = get_chat_response(prompt2, st.session_state.temperature)
    if st.session_state.get('final_cut'):
        st.text_area('Draft Write-ups:', height=500, key='final_cut', disabled = False)