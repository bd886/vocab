import random
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vocabulary, TestResult, VocabularyTestResult, Category
from .forms import CategoryForm, VocabularyForm
from django.db.models import Count
from django.core.paginator import Paginator

# Startseite
@login_required
def index(request):
    return render(request, 'vocab/index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")  # Nach dem Login zur Startseite
        else:
            error_message = "Ungültiger Benutzername oder Passwort."
            return render(request, "vocab/login.html", {"error": error_message})
    return render(request, "vocab/login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")  # Nach dem Logout zur Login-Seite
    
# Kategorien hinzufügen
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_vocab')  # Nach dem Anlegen zur Vokabeleingabe
    else:
        form = CategoryForm()
    return render(request, 'vocab/add_category.html', {'form': form})

# Vokabeln hinzufügen
@login_required
def add_vocab(request):
    if request.method == 'POST':
        form = VocabularyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        # Zuletzt angelegte Kategorie vorauswählen
        latest_category = Category.objects.last()
        form = VocabularyForm(initial={'category': latest_category})
    return render(request, 'vocab/add_vocab.html', {'form': form})

# Lernen
@login_required
def learn_vocab(request):
    # Kategorien abrufen
    categories = Category.objects.all().order_by('-id')

    # Standardmäßig keine Vokabeln anzeigen
    vocab_list = []

    # Wenn eine Kategorie ausgewählt wurde
    selected_category = request.GET.get('category')

    if selected_category:
        try:
            if selected_category == "all":
                vocab_list = Vocabulary.objects.all()
            else:
                category = Category.objects.get(id=selected_category)
                vocab_list = Vocabulary.objects.filter(category=category)
        except Category.DoesNotExist:
            vocab_list = []  # Wenn die Kategorie nicht existiert

    context = {
        'categories': categories,
        'vocab_list': vocab_list,
        'selected_category': selected_category
    }
    return render(request, 'vocab/learn.html', context)

# Test
@login_required
def test_vocab(request):
    if request.method == 'POST':
        question_id = int(request.POST.get('question_id'))
        answer = request.POST.get('answer')
        vocab = Vocabulary.objects.get(id=question_id)
        correct = (answer.strip().lower() == vocab.english.lower())

        # Bewertung aktualisieren
        if correct and vocab.rating < 5:
            vocab.rating += 1  # Punkt hinzufügen
        elif not correct and vocab.rating > 0:
            vocab.rating -= 1  # Punkt abziehen
        vocab.save()

        return render(request, 'vocab/test_result.html', {'vocab': vocab, 'correct': correct})

    # Zufällige Vokabel für den Test auswählen
    vocab = random.choice(Vocabulary.objects.all())
    return render(request, 'vocab/test.html', {'vocab': vocab})

@login_required
def start_test(request):
    # Kategorien und Auswahloption "Alle" abrufen
    categories = Category.objects.all().order_by('-id')

    if request.method == 'POST':
        selected_category = request.POST.get('category')
        if selected_category == "all" or not selected_category:
            vocab_list = Vocabulary.objects.filter(rating__lte=5)
        else:
            category = Category.objects.get(id=selected_category)
            vocab_list = Vocabulary.objects.filter(category=category, rating__lte=5)

        # Vokabeln priorisieren: Bewertung < 3 bevorzugt
        weak_vocab = vocab_list.filter(rating__lt=3)
        others = vocab_list.exclude(rating__lt=3)
        test_vocab = list(weak_vocab) + list(others)
        random.shuffle(test_vocab)

        # Testumfang auf 10 begrenzen
        test_vocab = test_vocab[:10]

        # TestResult erstellen und speichern
        test = TestResult.objects.create(
            category=category if selected_category != "all" else None,
            total_questions=len(test_vocab)
        )

        # IDs der Vokabeln und Test-ID speichern (Session)
        request.session['test_vocab'] = [v.id for v in test_vocab]
        request.session['test_id'] = test.id
        return redirect('run_test')

    return render(request, 'vocab/start_test.html', {'categories': categories})

@login_required
def run_test(request):
    test_vocab_ids = request.session.get('test_vocab', [])
    test_id = request.session.get('test_id')

    if not test_vocab_ids or not test_id:
        return redirect('start_test')  # Kein Test gestartet

    if request.method == 'POST':
        question_id = int(request.POST.get('question_id'))
        answer = request.POST.get('answer')
        vocab = Vocabulary.objects.get(id=question_id)
        test = TestResult.objects.get(id=test_id)

        correct = (answer.strip().lower() == vocab.english.lower())

        # Bewertung der Vokabel anpassen
        if correct and vocab.rating < 5:
            vocab.rating += 1
        elif not correct and vocab.rating > 0:
            vocab.rating -= 1
        vocab.save()

        # Ergebnis speichern
        VocabularyTestResult.objects.create(
            test=test,
            vocabulary=vocab,
            correct=correct
        )

        # Nächste Vokabel
        test_vocab_ids.pop(0)
        request.session['test_vocab'] = test_vocab_ids

        if not test_vocab_ids:
            # Test abgeschlossen
            correct_count = test.vocab_results.filter(correct=True).count()
            wrong_count = test.vocab_results.filter(correct=False).count()
            test.correct_answers = correct_count
            test.wrong_answers = wrong_count
            test.save()
            return redirect('test_summary', test_id=test.id)

    # Nächste Frage abrufen
    vocab = Vocabulary.objects.get(id=test_vocab_ids[0])
    return render(request, 'vocab/run_test.html', {'vocab': vocab})

@login_required
def test_summary(request, test_id):
    test = TestResult.objects.get(id=test_id)
    return render(request, 'vocab/test_summary.html', {'test': test})

@login_required
def test_overview(request):
    test_results = TestResult.objects.all().order_by('-date')  # Neueste zuerst
    paginator = Paginator(test_results, 10)  # 10 Tests pro Seite

    page_number = request.GET.get('page')  # Aktuelle Seite aus den GET-Parametern
    page_obj = paginator.get_page(page_number)

    return render(request, 'vocab/test_overview.html', {'page_obj': page_obj})