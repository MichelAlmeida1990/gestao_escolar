from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Professor

class ProfessorListView(ListView):
    model = Professor
    context_object_name = 'professores'
    template_name = 'professores/professor_list.html'

class ProfessorDetailView(DetailView):
    model = Professor
    context_object_name = 'professor'
    template_name = 'professores/professor_detail.html'

class ProfessorCreateView(SuccessMessageMixin, CreateView):
    model = Professor
    template_name = 'professores/professor_form.html'
    fields = ['nome', 'email', 'telefone', 'formacao', 'especializacao', 'data_contratacao', 'usuario']
    success_url = reverse_lazy('professores:professor_list')
    success_message = "Professor cadastrado com sucesso!"

class ProfessorUpdateView(SuccessMessageMixin, UpdateView):
    model = Professor
    template_name = 'professores/professor_form.html'
    fields = ['nome', 'email', 'telefone', 'formacao', 'especializacao', 'data_contratacao', 'usuario']
    success_url = reverse_lazy('professores:professor_list')
    success_message = "Professor atualizado com sucesso!"

class ProfessorDeleteView(SuccessMessageMixin, DeleteView):
    model = Professor
    template_name = 'professores/professor_confirm_delete.html'
    success_url = reverse_lazy('professores:professor_list')
    success_message = "Professor excluído com sucesso!"
