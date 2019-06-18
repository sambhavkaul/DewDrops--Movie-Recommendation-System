from flask import Flask,render_template,url_for,request, flash, redirect
from forms import RegistrationForm, LoginForm
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

app = Flask(__name__, template_folder='templates')

app.config['SECRET_KEY'] = '97787179b52dea978dcf3c0c474a76ac'

md = pd.read_csv('./data/movies_metadata.csv', low_memory=False, dtype={'id': str})
links_small = pd.read_csv('./data/links_small.csv')
links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')

md = md.drop([19730, 29503, 35587])
md['id'] = md['id'].astype('int')
smd = md[md['id'].isin(links_small)]

smd['tagline'] = smd['tagline'].fillna('')
smd['description'] = smd['overview'] + smd['tagline']
smd['description'] = smd['description'].fillna('')

tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(smd['description'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
smd = smd.reset_index()
titles = smd['title']
indices = pd.Series(smd.index, index=smd['title'])

def get_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    temp = titles.iloc[movie_indices]
    dm = pd.DataFrame(temp).reset_index()
    dm.columns = ['Rating', 'Title']
    dm_toList = dm['Title'].tolist()
    return dm_toList

@app.route('/')																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				
def home():
	return render_template('home.html')

@app.route('/about')																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				
def about():
	return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods=['GET', 'POST'])																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				
def login():
    form = LoginForm()
    return render_template('login.html', title = 'Login', form = form)

@app.route('/predict',methods=['POST'])
def predict():
	
	if request.method == 'POST':
		catch = request.form['catch']
		my_prediction = get_recommendations(catch)
    
	return render_template('result.html',prediction = my_prediction, first = catch)

if __name__ == '__main__':
	app.run(debug=True)