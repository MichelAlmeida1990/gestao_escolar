from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Professor
from .forms import ProfessorForm

class ProfessorListView(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'professores/professor_list.html'
    context_object_name = 'professores'
    
    def get_queryset(self):
        return Professor.objects.all()

class ProfessorDetailView(LoginRequiredMixin, DetailView):
    model = Professor
    template_name = 'professores/professor_detail.html'
    context_object_name = 'professor'

class ProfessorCreateView(LoginRequiredMixin, CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'professores/professor_form.html'
    success_url = reverse_lazy('professor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Professor cadastrado com sucesso!')
        return super().form_valid(form)

class ProfessorUpdateView(LoginRequiredMixin, UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'professores/professor_form.html'
    success_url = reverse_lazy('professor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Professor atualizado com sucesso!')
        return super().form_valid(form)

class ProfessorDeleteView(LoginRequiredMixin, DeleteView):
    model = Professor
    template_name = 'professores/professor_confirm_delete.html'
    success_url = reverse_lazy('professor_list')
    context_object_name = 'professor'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Professor excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
