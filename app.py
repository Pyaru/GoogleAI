import streamlit as st
import pandas as pd
import google.generativeai as genai

# ১. গুগল এআই সেটআপ
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key খুঁজে পাওয়া যায়নি!")

model = genai.GenerativeModel('gemini-1.5-flash')

# ২. ফাইল পড়ার লজিক
@st.cache_data
def load_data():
    with open('books.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    books = []
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('http'):
            title = lines[i-1].strip()
            books.append({'book_name': title, 'download_link': line})
    return pd.DataFrame(books)

df = load_data()

# ৩. ইন্টারফেস
st.set_page_config(page_title="ইসলামিক লাইব্রেরি বট", page_icon="📚")
st.title("📚 ইসলামিক লাইব্রেরি চ্যাটবট")

user_query = st.text_input("বইয়ের নাম বা বিষয় লিখুন:", placeholder="যেমন: সদকা")

if user_query:
    # --- উন্নত সার্চ লজিক শুরু ---
    # ইউজার যা লিখেছে তাকে ছোট ছোট শব্দে ভাগ করা (যেমন: 'নেকী দাওয়াত' -> ['নেকী', 'দাওয়াত'])
    search_words = user_query.split()
    
    # সব বইয়ের লিস্ট থেকে ফিল্টার করা
    results = df.copy()
    for word in search_words:
        results = results[results['book_name'].str.contains(word, case=False, na=False)]
    # --- উন্নত সার্চ লজিক শেষ ---
    
    if not results.empty:
        st.success(f"আপনার জন্য {len(results)}টি বই পাওয়া গেছে:")
        for index, row in results.iterrows():
            with st.expander(f"📖 {row['book_name']}"):
                st.write(f"🔗 [বইটি ডাউনলোড করতে এখানে ক্লিক করুন]({row['download_link']})")
                st.info("লিংকে ক্লিক করে বইটি পড়তে পারবেন।")
    else:
        with st.spinner("এআই উত্তর খুঁজছে..."):
            try:
                prompt = f"ইউজার '{user_query}' নামের বই খুঁজছে যা আমাদের তালিকায় নেই। তাকে সংক্ষেপে বাংলায় জানাও যে বইটি নেই।"
                response = model.generate_content(prompt)
                st.info(response.text)
            except:
                st.error("দুঃখিত, বইটি আমাদের তালিকায় নেই।")

st.divider()
st.caption("Powered by Google Gemini AI")
