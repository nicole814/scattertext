import scattertext as st
import pandas as pd

from scattertext.smoothing.lowess import Lowess

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.CorpusWithoutCategoriesFromParsedDocuments(
    df, parsed_col='parse'
).build().get_unigram_corpus().remove_infrequent_words(
    minimum_term_count=6
)

dispersion = st.Dispersion(corpus)

dispersion_df = dispersion.get_df().assign(
    X=lambda df: df.Frequency,
    Xpos=lambda df: st.Scalers.log_scale(df.X),
    Y=lambda df: dispersion.da(),
    Ypos=lambda df: st.Scalers.scale(df.Y),
    Expected=lambda df: Lowess().fit_predict(df.Xpos.values, df.Ypos.values),
    Residual=lambda df: df.Ypos - df.Expected,
    ColorScore=lambda df: st.Scalers.scale_center_zero_abs(df.Residual)
)

line_df = pd.DataFrame({
    'x': dispersion_df.Xpos.values,
    'y': dispersion_df.Expected.values,
}).sort_values(by='x')

html = st.dataframe_scattertext(
    corpus,
    plot_df=dispersion_df,
    metadata=corpus.get_df()['speaker'] + ' (' + corpus.get_df()['party'].str.upper() + ')',
    ignore_categories=True,
    x_label='Log Frequency',
    y_label='DA',
    y_axis_labels=['More Dispersion', 'Medium', 'Less Dispersion'],
    color_score_column='ColorScore',
    tooltip_columns=['Frequency', 'DA'],
    header_names={'upper': 'Lower than Expected', 'lower': 'More than Expected'},
    left_list_column='Residual',
    background_color='#e5e5e3',
    line_coordinates = line_df.to_dict('records')
)

fn = 'demo_dispersion.html'
open(fn, 'w').write(html)
print('open ./%s in Chrome' % fn)




residual_dispersion_df = dispersion_df.assign(
    Expected=lambda df: Lowess().fit_predict(df.X.values, df.Y.values),
    Y=lambda df: df.Y - df.Expected,
    Ypos=lambda df: st.Scalers.scale(df.Y),
    ColorScore=lambda df: st.Scalers.scale_center_zero_abs(df.Y)
)

line_df = pd.DataFrame({
    'x': dispersion_df.Xpos.values,
    'y': st.Scalers.scale(dispersion_df.Expected),
}).sort_values(by='x')

html = st.dataframe_scattertext(
    corpus,
    plot_df=residual_dispersion_df,
    unified_context=False,
    metadata=corpus.get_df()['speaker'] + ' (' + corpus.get_df()['party'].str.upper() + ')',
    x_label='Log Frequency',
    y_label='DA - E[DA] via Lowess',
    y_axis_labels=['More Dispersion', 'Medium', 'Less Dispersion'],
    color_score_column='ColorScore',
    tooltip_columns=['Frequency', 'DA - E[DA]'],
    header_names={'upper': 'Lower than Expected', 'lower': 'More than Expected'},
    left_list_column='Residual',
    background_color='#e5e5e3',
    line_coordinates = line_df.to_dict('records')
)



fn = 'demo_dispersion_residual.html'
open(fn, 'w').write(html)
print('open ./%s in Chrome' % fn)

