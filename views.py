from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('stopwords')
from django.contrib.staticfiles import finders

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

# Make `animation_view` accessible without login
def animation_view(request):
    if request.method == 'POST':
        text = request.POST.get('sen')
        # Lowercase and tokenize the sentence
        text = text.lower()
        words = word_tokenize(text)

        # Part of speech tagging and tense analysis
        tagged = nltk.pos_tag(words)
        tense = {
            "future": len([word for word in tagged if word[1] == "MD"]),
            "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
            "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
            "present_continuous": len([word for word in tagged if word[1] == "VBG"]),
        }

        # Stopwords removal and lemmatization
        stop_words = set(stopwords.words("english"))
        lr = WordNetLemmatizer()
        filtered_text = [
            lr.lemmatize(w, pos='v') if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']
            else lr.lemmatize(w, pos='a') if p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']
            else lr.lemmatize(w)
            for w, p in zip(words, tagged) if w not in stop_words
        ]

        # Add tense-indicating words
        probable_tense = max(tense, key=tense.get)
        if probable_tense == "past" and tense["past"] >= 1:
            filtered_text.insert(0, "Before")
        elif probable_tense == "future" and tense["future"] >= 1:
            if "Will" not in filtered_text:
                filtered_text.insert(0, "Will")
        elif probable_tense == "present" and tense["present_continuous"] >= 1:
            filtered_text.insert(0, "Now")

        # Check for word animations in static files
        final_words = []
        for w in filtered_text:
            path = f"{w}.mp4"
            if finders.find(path):
                final_words.append(w)
            else:
                final_words.extend(list(w))  # Split word into characters if animation isn't available

        return render(request, 'animation.html', {'words': final_words, 'text': text})
    else:
        return render(request, 'animation.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('animation')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('animation')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("home")
