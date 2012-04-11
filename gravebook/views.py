from django.http import HttpResponse
from gravebook.models import Article, Category
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response

import re, md5, math


def index(request):
    articles = []
    if request.method == 'POST':
        title_words = filter(lambda x: len(x) > 0, 
                             request.POST['title_inp'].split(' '))
        if len(title_words) > 0:
            articles = Article.objects.filter(name__icontains=title_words[0])
            for k in title_words[1:]:
                articles = articles.filter(name__icontains=k)
    
    return render_to_response('gravebook/index.html',
                              {'articles':articles},
                              RequestContext(request))

def article_detail(request, article_name):
    art = Article.objects.get(name=article_name)
    img = art.image.replace(' ', '_')
    digest = md5.new(img).hexdigest()
    img = digest[0]+'/'+digest[:2]+'/'+img

    OVERLAP = 15

    influences = []
    influenced = []
    peers = []
    people = art.people.all()
    for person in people:
        if person.birth == -1 or person.death == -1:
            continue
        
        if art.birth > person.death:
            influences.append(person)
        elif art.death < person.birth:
            influenced.append(person)
        elif (math.fabs(person.birth-art.birth) > OVERLAP or 
              math.fabs(person.death-art.death) > OVERLAP):
            peers.append(person)
                  
    
    return render_to_response('gravebook/article_detail.html',
                              { 'article':art, 'image':img,
                                'categories':art.categories.all(),
                                'peers':peers,
                                'influences':influences,
                                'influenced':influenced},
                                RequestContext(request))

def category_detail(request, category_name):
    cat = Category.objects.get(name=category_name)
    articles = cat.article_set.all()
    
    return render_to_response('gravebook/category_detail.html',
                              {'articles':articles,
                               'category_name': category_name},
                              RequestContext(request))
        
        
