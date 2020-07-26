import markdown2
import random
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.files.storage import default_storage
from . import util

class SearchForm(forms.Form):
    query = forms.CharField(label="",
        widget=forms.TextInput(attrs={'placeholder': 'Search Wiki', 
            'style': 'width:100%'}))

class NewPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
            'placeholder': 'Enter title', 'id': 'new-entry-title'}))
    data = forms.CharField(label="", widget=forms.Textarea(attrs={
        'id': 'new-entry'}))

class EditPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        'id': 'edit-entry-title'}))
    data = forms.CharField(label="", widget=forms.Textarea(attrs={
        'id': 'edit-entry'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    entry = util.get_entry(title)
  
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "form": SearchForm()
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdown2.markdown(entry),
            "entry_raw": entry,
            "form": SearchForm()
        })

def search(request):
    if request.method == "POST":
        matching = [] 
        articles = util.list_entries()  
        form = SearchForm(request.POST)  
        if form.is_valid():
            query = form.cleaned_data["query"]
            for entry in articles:
                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    return HttpResponseRedirect(reverse("entry", args=[title]))
                if query.lower() in entry.lower():
                    matching.append(entry)
            return render(request, "encyclopedia/search.html", {
                "results": matching,
                "query": query,
                "form": SearchForm()
            })
    return render(request, "encyclopedia/search.html", {
        "results": "",
        "query": "",
        "form": SearchForm()
    })

def create(request):
    if request.method == "POST":
        article_added = NewPageForm(request.POST)
        if article_added.is_valid():
            title = article_added.cleaned_data["title"]
            description = article_added.cleaned_data["data"]
            articles = util.list_entries()
            for article in articles:
                if article.lower() == title.lower():
                    return render(request, "encyclopedia/create.html", {
                        "form": SearchForm(),
                        "newPageForm": NewPageForm(),
                        "error": "That entry already exists!"
                    })
            article_added_title = "# " + title
            article_added_description = "\n" + description
            article_added_content = article_added_title + article_added_description
            util.save_entry(title, article_added_content)
            entry = util.get_entry(title)
            msg_success = "New page added"
            
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "entry": markdown2.markdown(entry),
                "form": SearchForm(),
                "msg_success": msg_success
            })
    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "newPageForm": NewPageForm()
    })

def editEntry(request, title):
    if request.method == "POST":
        entry = util.get_entry(title)
        edit_form = EditPageForm(initial={'title': title, 'data': entry})
        
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "editPageForm": edit_form,
            "entry": entry,
            "title": title
        })

def submitEditEntry(request, title):
    if request.method == "POST":
        edit_entry = EditPageForm(request.POST)
        if edit_entry.is_valid():
            content = edit_entry.cleaned_data["data"]
            title_edit = edit_entry.cleaned_data["title"]
            articles = util.list_entries()
            correct = 1
            msg_success = "The entry has been edited"
            if title_edit != title:
                for article in articles:
                    if article.lower() == title_edit.lower():
                        correct = 0
                if correct == 1:
                    filename = f"entries/{title}.md"
                    if default_storage.exists(filename):
                        default_storage.delete(filename)
            entry = util.get_entry(title_edit)
            if correct == 1:
                util.save_entry(title_edit, content)
                entry = util.get_entry(title_edit)
                return render(request, "encyclopedia/entry.html", {
                    "title": title_edit,
                    "entry": markdown2.markdown(entry),
                    "form": SearchForm(),
                    "msg_success": msg_success
                })
            if correct == 0:
                entry = util.get_entry(title)
                return render(request, "encyclopedia/entry.html", {
                    "title": title,
                    "entry": markdown2.markdown(entry),
                    "form": SearchForm(),
                    "error": "There is an entry with the same name"
                })
            

def randomEntry(request):
    entries = util.list_entries()
    title = random.choice(entries)
    entry = util.get_entry(title)
    return HttpResponseRedirect(reverse("entry", args=[title]))