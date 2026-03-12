from django.shortcuts import render
#from django.http import HttpResponse

# Create your views here.
def sample(request):
    #return HttpResponse('<h1>THIS IS A SAMPLE PAGE</h1>')
    return render(request, 'trialapp/index.html')