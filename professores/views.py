from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Professor
from .forms import ProfessorForm

class ProfessorListView(ListView):
    model = Professor
    template_name = 'professores/professor_list.html'
    context_object_name = 'professores'

class ProfessorCreateView(CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'professores/professor_form.html'
    success_url = reverse_lazy('professores:professor_list')

class ProfessorDetailView(DetailView):
    model = Professor
    template_name = 'professores/professor_detail.html'

class ProfessorUpdateView(UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'professores/professor_form.html'
    success_url = reverse_lazy('professores:professor_list')

class ProfessorDeleteView(DeleteView):
    model = Professor
    template_name = 'professores/professor_confirm_delete.html'
    success_url = reverse_lazy('professores:professor_list')

def listar_professores(request):
    professores = Professor.objects.all()
    return render(request, 'professores/professor_list.html', {'professores': professores})
