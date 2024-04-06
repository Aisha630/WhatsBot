from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

english_sentences = [
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
    "What is reason that I don't have period in ramzam",
    "Mostly women use medicine in periods days any side effects the medicines",
    "Can I use pain killer in periods",
    "What is the reason of pain in periods",
    
    

]

urdu_sentences = [
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
    
    
    
    


]

# Labels: 0 for English, 1 for Urdu written in English script
data = english_sentences + urdu_sentences
labels = np.array([0] * len(english_sentences) + [1] * len(urdu_sentences))

# X_train, X_test, y_train, y_test = train_test_split(
#     data, labels, test_size=0.2, random_state=42)

y_train = labels

vectorizer = TfidfVectorizer()
X_train_vectors = vectorizer.fit_transform(data)
# X_test_vectors = vectorizer.transform(X_test)

model = SVC(kernel='linear')
model.fit(X_train_vectors, y_train)

# y_pred = model.predict(X_test_vectors)

print(model.predict(vectorizer.transform(
    ["How can I check apna balance without internet?"])))

# print("Accuracy:", accuracy_score(y_test, y_pred))
# print("Classification Report:\n", classification_report(y_test, y_pred))
