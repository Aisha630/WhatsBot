import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Sample data (replace with your own data)
english_texts = [
    "Hi",
    "Hello",
    "Helloo",
    "Hiii",
    "Hey",
    "Heyy",
    "Bye",
    "This is a book.",
    "How are you?",
    "The quick brown fox jumps over the lazy dog."
    "I am fine.",
    "What are you doing?",
    "I don't know.",
    "Do you know?",
    "I don't know either.",
    "What should we do now?",
    "Can you tell me?",
    "I don't think so.",
    "Can you help me?",
    "Can you help me with my pain",
    "Can you answer my questions",
    "Why is there so much pain in periods?",
    "The pain in periods is different",
    "Why does the body become lifeless during periods?",
    "Why does my head hurt during periods?",
    "Why do I feel so weak during periods?",
    "What do you do during periods?",
    "Hello, experiencing pain during menstruation is a common occurrence for many women.",
    "If this pain is manageable and doesn't significantly affect your daily activities such as attending school, work, or other tasks, and if you're able to carry on with these activities despite menstrual pain, then there might not be a necessity to visit a doctor",
    "Suggests pain management strategies, including over-the-counter tablets, maintaining bone strength through diet, and when to seek medical help based on the intensity of pain",
    "The level of pain during menstruation depends on several factors. What is your age? Are you married or not, and do you have children? Is the size of the uterus normal, and are there any abnormalities present? Is there any fluid inside or outside the uterus? These conditions contribute to the extent of pain experienced during menstruation. However, they are not directly related to consuming hot or cold foods",
    "If you're experiencing chronic body pain and seeking treatment, there are natural pain-relieving properties found in certain foods and remedies. Hot milk, tea, kahwa, dates, dried fruits, almonds, and a protein-rich diet like eggs are natural food items known to alleviate pain",
    "If this pain is manageable and doesn't significantly affect your daily activities such as attending school, work, or other tasks, and if you're able to carry on with these activities despite menstrual pain, then there might not be a necessity to visit a doctor",
    "Suggests pain management strategies, including over-the-counter tablets, maintaining bone strength through diet, and when to seek medical help based on the intensity of pain",
    "Can I use pain killer in periods",
    "What is the reason of pain in periods",
    "lol",
    "Thank you",
    "You are welcome",
    "I am grateful for your help",
    "Thank you for your patience",
    "Laughing out loud",
    "How can i make this work",
    "How can i make the bot work",
    "How can i check my balance",
    "How can i check my fever",
    "How can i check my life",
    "How can i monitor my pain",
    "Okay",
    "Okay thanks",
    "Okay thank you",
    "Sorry",
    "Oh sorry",
    "How are you",
    "How was your day",
    "Today i had a bad day",
    "Why do periods last for different days with different people",
    "Some people say it's not advisable to take a shower during the first 3 days of your cycle. Is it so? And if so, why?",
    "Mostly women use medicine in periods days any side effects the medicines",
    "This is incorrect",
    "Are you sure?",
    "Am i wrong about this?",
    "Give me corect answer",
    "Do not tell me",
    "Should i take these medicines",
    "Should i follow your advice",
    "Is your advice good advice?",
    "What is good and bad?",
    "I have to go to school.",
    "Will you come with me?",
    "It's raining today.",
    "I have eaten my food.",
    "How long will it take?",
    "What is your name?",

    "I didn't understand this.",
    "Can you help me?",
    "Thank you, I liked it.",
    "We'll meet again tomorrow morning.",





]

roman_urdu_texts = [
    "Mujhe school jana hai.",
    "Kya aap mere saath chalenge?",
    "Aaj barish ho rahi hai.",
    "Main ne khana kha liya hai.",
    "Kitni dair lagegi?",
    "Yeh ek kitaab hai.",
    "Aap kaise hain?",
    "Bara shor sunte hain aasman mein.",
    "Ghar kab jainge",
    "Kya kar rahe ho?",
    "Mujhe nahi pata.",
    "Kya tumhe pata hai?",
    "Mujhe bhi nahi pata.",
    "Ab hum kya karein?",
    "Kya tum mujhe bata sakte ho?",
    "Mujhe nahi lagta.",
    "Periods mein itni ziada pain kyun hoti hai? ",
    "Periods mein jo pain hai har aik khatoon ki perception different hai.",
    "Kya periods",
    "Jitni jiski bardasht kerne ki salahiyat hoti hai utni he utna he unko pain ka ehsaas kam ya ziada hota hai"
    "Periods mein jism be-jaan kyun ho jata hai?",
    "Khatti cheezain khanay ka first time period kay ziada jaldi honay k sath koi link nahin hai. First time periods ziada jaldi hojayen , iska taaluq female ki organ maturity or unkay reproductive system ki health k sath hai",
    "Menstrual periods ki date ka taluq khatoon ke internal reproductive system ke function ke sath bhi hai aur age ke sath bhi hai aur kisi bhi khatoon mein menstrual period ki date saari zindagi ek jaisi nahi rehti hai. Age ke sath menses late ya jaldi ho sakte hain",
    "Periods kyun hotay hain, iski reason hai her female k ander reproductive organs ka normal monthly function. ",
    "Her female jab mature hojati hain tou unkay reproductive organs main her mahinay aesi tabdeeliyaan aati hain k basically woh reproduction k liye ya bacha paida kernay keliye ya toleedi amal k liye uterus apnay ap ko tyar kerti hai aur phir uskay bad jab koi pregnency na hou ya aesi koi situation na hou tou hormones change ho jatay hain  aur hormones ki changes ki wajah se menses bleeding hoti.",
    "Yeh her female ki maturity or jab woh adult hojati hain, tou unkay reproductive organs ki normal functioning hai aur yeh normal physiology ka hissa hai",
    "Periods mein jo pain hai har aik khatoon ki perception different hai.",
    "Kya periods"
    "Jitni jiski bardasht kerne ki salahiyat hoti hai utni he utna he unko pain ka ehsaas kam ya ziada hota hai"
    "Periods mein jism be-jaan kyun ho jata hai?",
    "Khatti cheezain khanay ka first time period kay ziada jaldi honay k sath koi link nahin hai. First time periods ziada jaldi hojayen , iska taaluq female ki organ maturity or unkay reproductive system ki health k sath hai",
    "Menstrual periods ki date ka taluq khatoon ke internal reproductive system ke function ke sath bhi hai aur age ke sath bhi hai aur kisi bhi khatoon mein menstrual period ki date saari zindagi ek jaisi nahi rehti hai. Age ke sath menses late ya jaldi ho sakte hain",
    "Periods kyun hotay hain, iski reason hai her female k ander reproductive organs ka normal monthly function. ",
    "Her female jab mature hojati hain tou unkay reproductive organs main her mahinay aesi tabdeeliyaan aati hain k basically woh reproduction k liye ya bacha paida kernay keliye ya toleedi amal k liye uterus apnay ap ko tyar kerti hai aur phir uskay bad jab koi pregnency na hou ya aesi koi situation na hou tou hormones change ho jatay hain  aur hormones ki changes ki wajah se menses bleeding hoti.",
    "Yeh her female ki maturity or jab woh adult hojati hain, tou unkay reproductive organs ki normal functioning hai aur yeh normal physiology ka hissa hai",
    "Headache ko control k liye what medicines should I take?",
    "Headache ki koi tips kasy control kary without tablets",
    "Or BP jo hota hain wo high or low ki waja kya hoti aur ghr ma koi tips kasy control kary",
    "Migraine ki waja kya hoti hain or iska ilaj kya hota hain",
    "How can I control apne sar ka dard wihtout tablets",
    "Agr adhe sar me shadeed Dard ho to Kon c pain killer use krni chahiye ?",
    "Agar periods may fever hoo Jay to kya medicines use karnii cahiyah",
    "Gynecologic cancers Sy kesay bachay",
    "I am getting pains in my pait",
    "How can i mitigate sar ka dard",
    "How can i lessen pait ka dard",
    "Ap mujhse shaadi krogi kiya",
    "Ap mujhse baat krna chahoge",
    "Apne ghar kab jana hai",
    "Mein kiya kron",
    "Mein kron is mamlay k baray mein",
    "Mein ghar jana chahti hon",
    "Mein chahti hon mere sar ka dard kam hojaye",
    "Mein apne Mom Dad se kiya kahon is baray mein",

    "I want to get married when i am thora bara",
    "Apka shukriya",
    "Meharbani",
    "Khuda Hafiz",
    "Allah Hafiz",
    "I have bohat dard in my pait",
    "Ghussay kese control krien",
    "Ya koi illness toh nahi hai na",
    "Ya koi illness to nahi hana",
    "Mary papa ki Raat ko sony ky baad taangy main  bhht zyada pain hoti is ki koi tip",
    "Kudh ko maintain kasy rakhy health wise",
    "Hormones issue per koi ghar main hi tips",
    "Kuch bolny baat karny ko  dil nhi karta asy  lgata ky agla  bnda insult kardy ga yah judge kary ga to is ko kasy manage kary",
    "Oh sorry ap kiya suggest krein ge is baray mein",
    "Sahi",
    "Ghalat",



]

# Concatenate English and Roman Urdu texts
texts = english_texts + roman_urdu_texts
labels = [0] * len(english_texts) + [1] * len(roman_urdu_texts)  # 0 for English, 1 for Roman Urdu

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Vectorize the text data
vectorizer = TfidfVectorizer()
X_train_vectors = vectorizer.fit_transform(X_train)
X_test_vectors = vectorizer.transform(X_test)

# Initialize and train Random Forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train_vectors, y_train)

# Predict on the test set
y_pred = rf_classifier.predict(X_test_vectors)

print(rf_classifier.predict(vectorizer.transform(
    ["Ap mujhse shaadi krogi kiya"])))
print(rf_classifier.predict(vectorizer.transform(
    ["Stomach ache k lye kiya precautions zaroori hain"])))
print(rf_classifier.predict(vectorizer.transform(
    ["How can I check apna or baakion ka balance without internet?"])))

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
