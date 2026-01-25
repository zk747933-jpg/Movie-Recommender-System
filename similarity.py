# similarity.py
import pickle

# ✅ Load your local large similarity matrix
# This will run locally or on Streamlit Cloud
similarity = pickle.load(open('similarity.pkl','rb'))
