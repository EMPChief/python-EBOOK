import glob
import nltk
import streamlit as st
import plotly.express as px
import pandas as pd
import re
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

st.set_page_config(
    page_title="Diary Sentiment Analyzer",
    page_icon="favicon.ico",
)

class DiarySentimentAnalyzer:
    def __init__(self, diary_folder="diary"):
        self.diary_folder = diary_folder
        self.validate_diary_folder()  # Validate on initialization
        self.filepaths = sorted(glob.glob(f"{self.diary_folder}/*.txt"))
        self.analyzer = SentimentIntensityAnalyzer()
        self.analyze_and_extract()

    def validate_diary_folder(self):
        import os
        if not os.path.exists(self.diary_folder):
            raise ValueError(f"Diary folder '{self.diary_folder}' does not exist.")

    def extract_date(self, filepath):
        date_pattern = re.compile(r".*/(\d{4}-\d{2}-\d{2})\.txt") 
        match = date_pattern.search(filepath)
        if match:
            return match.group(1)
        else:
            return "Invalid Date Format"

    def read_diary_contents(self):
        contents = []
        for filepath in self.filepaths:
            try: 
                with open(filepath) as file:
                    content = file.read()
                    contents.append(content)
            except FileNotFoundError:
                st.error(f"File not found: {filepath}")
            except PermissionError:
                st.error(f"Insufficient permissions to read: {filepath}")
        return contents   

    def analyze_and_extract(self):
        self.contents = self.read_diary_contents()
        scores = self.analyzer.polarity_scores(self.contents)
        self.positivity_scores = [score['pos'] for score in scores]
        self.negativity_scores = [score['neg'] for score in scores]
        self.dates = [self.extract_date(filepath) for filepath in self.filepaths]

    def create_dataframe(self):
        sentiment_labels = ["Positive" if pos > neg else "Negative" for pos, neg in zip(self.positivity_scores, self.negativity_scores)]
        df = pd.DataFrame({
            "Date": self.dates,
            "Sentiment": sentiment_labels,
            "Positivity": self.positivity_scores,
            "Negativity": self.negativity_scores,
            "Content": self.contents
        })
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

    def display_combined_chart(self):
        st.subheader("Combined Sentiment")
        df = self.create_dataframe()  # In case it hasn't been created yet
        fig = px.line(df, x="Date", y=["Positivity", "Negativity"], labels={"value": "Score"})
        st.plotly_chart(fig)

    def display_dataframe(self, df):
        st.subheader("Data Table")
        st.table(df)

def run():
    st.title("Diary Sentiment Analyzer")
    diary_folder = st.text_input("Diary Folder Path", "diary")

    if st.button("Analyze"):  # Analyze on button click
        analyzer = DiarySentimentAnalyzer(diary_folder)
        analyzer.display_positivity_chart()
        analyzer.display_negativity_chart()
        analyzer.display_combined_chart()
        df = analyzer.create_dataframe()
        analyzer.display_dataframe(df)

if __name__ == "__main__":
    run()
