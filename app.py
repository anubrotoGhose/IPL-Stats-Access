from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import search_results
import data_manipulation
app = Flask(__name__)
app.secret_key = 'your_secret_key'

def convert_dict_to_df(data):
    # Find the maximum length of the lists in the dictionary
    max_length = max(len(lst) for lst in data.values())

    # Pad shorter lists with None
    for key in data:
        data[key] += [None] * (max_length - len(data[key]))

    # Convert the dictionary into a pandas DataFrame
    df = pd.DataFrame(data)
    return df

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.form['user_input']
        search_dict = search_results.filter_dict_by_search(user_input)
        
        # Store search_dict in session
        session['search_dict'] = search_dict

        return redirect(url_for('searchresults', user_input=user_input))
    return render_template('home.html')

@app.route('/searchresults/<user_input>')
def searchresults(user_input):
    # Retrieve the search_dict from the session
    search_dict = session.get('search_dict', {})

    # Get the keys (column names)
    dict_keys = search_dict.keys()

    return render_template('searchresults.html', user_input=user_input, dict_keys=dict_keys, search_dict=search_dict)

@app.route('/profile_page/<column_name>')
def profile_page(column_name):
    cell_value = request.args.get('value')
    df_batter = pd.DataFrame()
    df_bowler = pd.DataFrame()
    if column_name == 'Players':
        df_batter = pd.DataFrame(data_manipulation.batter_stats(cell_value))
        df_bowler = pd.DataFrame(data_manipulation.bowler_stats(cell_value))
    else:
        df_batter = pd.DataFrame(data_manipulation.x_batter_stats(cell_value))
        df_bowler = pd.DataFrame(data_manipulation.x_bowler_stats(cell_value))

    # Convert the DataFrame to HTML
    table_html_batter = df_batter.to_html(classes='table')
    table_html_bowler = df_bowler.to_html(classes='table')
    return render_template('profile_page.html', column_name=column_name, cell_value=cell_value, table_html_batter=table_html_batter, table_html_bowler = table_html_bowler)



if __name__ == '__main__':
    app.run(debug=True)