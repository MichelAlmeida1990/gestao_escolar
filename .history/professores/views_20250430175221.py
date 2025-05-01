from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Professor
from .forms import ProfessorForm

class ProfessorListView(ListView):
    model = Professor
    template_name = 'professores/professor_list.html'
    context_object_name = 'professores'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(email__icontains=search) |
                Q(disciplina__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class ProfessorDetailView(DetailView):
    model = Professor
    template_name = 'professores/professor_detail.html'
    context_object_name = 'professor'

class ProfessorCreateView(CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'professores/professor_form.html'
    success_url = reverse_lazy('professor_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Professor cadastrado com sucesso!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Cadastrar Novo Professor'
        context['botao'] = 'Cadastrar'
        return context

class ProfessorUpdateView(UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'professores/professor_form.html'
    success_url = reverse_lazy('professor_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Professor atualizado com sucesso!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Professor'
        context['botao'] = 'Atualizar'
        return context

class ProfessorDeleteView(DeleteView):
    model = Professor
    template_name = 'professores/professor_confirm_delete.html'
    success_url = reverse_lazy('professor_list')
    context_object_name = 'professor'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Professor excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
