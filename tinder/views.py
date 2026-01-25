from django.shortcuts import render, redirect
from user.forms import RegisterForm
 
def home(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'home.html', {'form': form})