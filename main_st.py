import glob
import nltk
import streamlit as st
import plotly.express as px
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

st.set_page_config(
    page_title="EMP Sentiment checker",
    page_icon="favicon.ico",
)
class DiarySentimentAnalyzer:
    def __init__(self, diary_folder="diary"):
        self.filepaths = sorted(glob.glob(f"{diary_folder}/*.txt"))
        self.diary_folder = diary_folder
        self.analyzer = SentimentIntensityAnalyzer()
        self.negativity_scores = []
        self.positivity_scores = []
        self.dates = [self.extract_date(filepath) for filepath in self.filepaths]
        self.contents = self.read_diary_contents()

    def extract_date(self, filepath):
        return filepath.strip(".txt").replace(f"{self.diary_folder}/", "")

    def read_diary_contents(self):
        contents = []
        for filepath in self.filepaths:
            with open(filepath) as file:
                content = file.read()
                contents.append(content)
        return contents

    def analyze_sentiments(self):
        for content in self.contents:
            scores = self.analyzer.polarity_scores(content)
            self.positivity_scores.append(scores["pos"])
            self.negativity_scores.append(scores["neg"])

    def create_dataframe(self):
        result_labels = ["Positive" if pos > neg else "Negative" for pos, neg in zip(self.positivity_scores, self.negativity_scores)]

        data = {
            "Date": self.dates,
            "Result": result_labels,
            "Positivity": self.positivity_scores,
            "Negativity": self.negativity_scores,
            "Content": self.contents
        }

        df = pd.DataFrame(data)
        return df



    def display_positivity_chart(self):
        st.subheader("Positivity")
        pos_figure = px.line(x=self.dates, y=self.positivity_scores,
                             labels={"x": "Date", "y": "Positivity"})
        st.plotly_chart(pos_figure)

    def display_negativity_chart(self):
        st.subheader("Negativity")
        neg_figure = px.line(x=self.dates, y=self.negativity_scores,
                             labels={"x": "Date", "y": "Negativity"})
        st.plotly_chart(neg_figure)

    def display_dataframe(self, df):
        st.subheader("Data Table")
        st.table(df)

def run():
    diary_analyzer = DiarySentimentAnalyzer()
    diary_analyzer.analyze_sentiments()
    st.title("Diary Tone")
    diary_analyzer.display_positivity_chart()
    diary_analyzer.display_negativity_chart()
    df = diary_analyzer.create_dataframe()
    diary_analyzer.display_dataframe(df)

if __name__ == "__main__":
    run()
