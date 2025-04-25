from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Aluno
from .forms import AlunoForm

class AlunoListView(ListView):
    model = Aluno
    template_name = 'alunos/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | 
                Q(matricula__icontains=search) |
                Q(cpf__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class AlunoDetailView(DetailView):
    model = Aluno
    template_name = 'alunos/aluno_detail.html'
    context_object_name = 'aluno'

class AlunoCreateView(CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/aluno_form.html'
    success_url = reverse_lazy('aluno_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Cadastrar Novo Aluno'
        context['botao'] = 'Cadastrar'
        return context

class AlunoUpdateView(UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/aluno_form.html'
    success_url = reverse_lazy('aluno_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Aluno atualizado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Aluno'
        context['botao'] = 'Atualizar'
        return context

class AlunoDeleteView(DeleteView):
    model = Aluno
    template_name = 'alunos/aluno_confirm_delete.html'
    success_url = reverse_lazy('aluno_list')
    context_object_name = 'aluno'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Aluno excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

# Views baseadas em função (alternativa)
def aluno_list(request):
    search = request.GET.get('search', '')
    alunos_list = Aluno.objects.all()
    
    if search:
        alunos_list = alunos_list.filter(
            Q(nome__icontains=search) | 
            Q(matricula__icontains=search) |
            Q(cpf__icontains=search)
        )
    
    paginator = Paginator(alunos_list, 10)
    page = request.GET.get('page')
    alunos = paginator.get_page(page)
    
    return render(request, 'alunos/aluno_list.html', {
        'alunos': alunos,
        'search': search
    })

def aluno_detail(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    return render(request, 'alunos/aluno_detail.html', {'aluno': aluno})

def aluno_create(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno cadastrado com sucesso!')
            return redirect('aluno_list')
    else:
        form = AlunoForm()
    
    return render(request, 'alunos/aluno_form.html', {
        'form': form,
        'titulo': 'Cadastrar Novo Aluno',
        'botao': 'Cadastrar'
    })

def aluno_update(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno atualizado com sucesso!')
            return redirect('aluno_list')
    else:
        form = AlunoForm(instance=aluno)
    
    return render(request, 'alunos/aluno_form.html', {
        'form': form,
        'titulo': 'Editar Aluno',
        'botao': 'Atualizar'
    })

def aluno_delete(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    
    if request.method == 'POST':
        aluno.delete()
        messages.success(request, 'Aluno excluído com sucesso!')
        return redirect('aluno_list')
    
    return render(request, 'alunos/aluno_confirm_delete.html', {'aluno': aluno})

def dashboard(request):
    total_alunos = Aluno.objects.count()
    alunos_ativos = Aluno.objects.filter(status='ativo').count()
    alunos_inativos = Aluno.objects.filter(status='inativo').count()
    alunos_transferidos = Aluno.objects.filter(status='transferido').count()
    
    return render(request, 'alunos/dashboard.html', {
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'alunos_inativos': alunos_inativos,
        'alunos_transferidos': alunos_transferidos
    })
