from flask import Flask, render_template, url_for, request, flash, redirect
from forms import RegistrationForm, LoginForm
import pandas as pd
from rake_nltk import Rake
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

app = Flask(__name__, template_folder="templates")

app.config["SECRET_KEY"] = "97787179b52dea978dcf3c0c474a76ac"

df = pd.read_csv("./data/tmdb_5000_movies.csv")

df = df[["Title", "Genre", "Plot", "vote_average"]]
df = df.astype(str)
df["Genre"] = df["Genre"].map(lambda x: x.lower().split(","))
df["Key_words"] = ""

for index, row in df.iterrows():
    plot = row["Plot"]

    # instantiating Rake, by default it uses english stopwords from NLTK
    # and discards all puntuation characters as well
    r = Rake()

    # extracting the words by passing the text
    r.extract_keywords_from_text(plot)

    # getting the dictionary whith key words as keys and their scores as values
    key_words_dict_scores = r.get_word_degrees()

    # assigning the key words to the new column for the corresponding movie
    row["Key_words"] = list(key_words_dict_scores.keys())

# dropping the Plot column
df.drop(columns=["Plot"], inplace=True)
df.set_index("Title", inplace=True)


df["bag_of_words"] = ""
columns = df.columns
for index, row in df.iterrows():
    words = ""
    for col in columns:
        words = words + " ".join(row["Genre"]) + " " + " ".join(row["Key_words"])

        row["bag_of_words"] = words
df.drop(columns=["Genre"], inplace=True)
df.drop(columns=["Key_words"], inplace=True)

count = CountVectorizer()
count_matrix = count.fit_transform(df["bag_of_words"])

# generating the cosine similarity matrix
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# creating a Series for the movie titles so they are associated to an ordered numerical
# list I will use in the function to match the indexes
indices = pd.Series(df.index)


#  defining the function that takes in movie title
# as input and returns the top 10 recommended movies
def recommendations(title, cosine_sim=cosine_sim):

    # initializing the empty list of recommended movies
    recommended_movies = []

    # gettin the index of the movie that matches the title
    idx = indices[indices == title].index[0]

    # creating a Series with the similarity scores in descending order
    score_series = pd.Series(cosine_sim[idx]).sort_values(ascending=False)

    # getting the indexes of the 10 most similar movies
    top_10_indexes = list(score_series.iloc[1:11].index)

    # populating the list with the titles of the best 10 matching movies
    for i in top_10_indexes:
        recommended_movies.append(list(df.index)[i])

    return recommended_movies


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template("login.html", title="Login", form=form)


@app.route("/predict", methods=["POST"])
def predict():

    if request.method == "POST":
        catch = request.form["catch"]
        my_prediction = recommendations(catch)

    return render_template("result.html", prediction=my_prediction, first=catch)


if __name__ == "__main__":
    app.run(debug=True)

