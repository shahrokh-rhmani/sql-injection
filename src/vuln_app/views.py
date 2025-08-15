from django.shortcuts import render

def listview(request):
    context = {
         
    }
    return render(request, 'listview.html', context)