# Generated by Django 5.1.6 on 2025-06-25 14:43

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alunos', '0002_alter_aluno_options_remove_aluno_responsavel_and_more'),
        ('professores', '0002_alter_professor_turmas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150, verbose_name='Nome do Autor')),
                ('nacionalidade', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nacionalidade')),
                ('data_nascimento', models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')),
                ('biografia', models.TextField(blank=True, null=True, verbose_name='Biografia')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='autores/', verbose_name='Foto')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
            ],
            options={
                'verbose_name': 'Autor',
                'verbose_name_plural': 'Autores',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome da Categoria')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('cor', models.CharField(default='#007bff', help_text='Cor para identificação visual', max_length=7, verbose_name='Cor (Hex)')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='ConfiguracaoBiblioteca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dias_emprestimo_aluno', models.IntegerField(default=7, verbose_name='Dias de Empréstimo - Aluno')),
                ('dias_emprestimo_professor', models.IntegerField(default=14, verbose_name='Dias de Empréstimo - Professor')),
                ('max_renovacoes', models.IntegerField(default=2, verbose_name='Máximo de Renovações')),
                ('max_livros_aluno', models.IntegerField(default=3, verbose_name='Máximo de Livros por Aluno')),
                ('max_livros_professor', models.IntegerField(default=5, verbose_name='Máximo de Livros por Professor')),
                ('valor_multa_dia', models.DecimalField(decimal_places=2, default=1.0, max_digits=10, verbose_name='Valor da Multa por Dia')),
                ('dias_reserva', models.IntegerField(default=3, verbose_name='Dias de Validade da Reserva')),
                ('nome_biblioteca', models.CharField(default='Biblioteca Escolar', max_length=200, verbose_name='Nome da Biblioteca')),
                ('endereco', models.TextField(blank=True, null=True, verbose_name='Endereço')),
                ('horario_funcionamento', models.TextField(blank=True, null=True, verbose_name='Horário de Funcionamento')),
                ('telefone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefone')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail')),
            ],
            options={
                'verbose_name': 'Configuração da Biblioteca',
                'verbose_name_plural': 'Configurações da Biblioteca',
            },
        ),
        migrations.CreateModel(
            name='Editora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150, verbose_name='Nome da Editora')),
                ('endereco', models.TextField(blank=True, null=True, verbose_name='Endereço')),
                ('telefone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefone')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail')),
                ('site', models.URLField(blank=True, null=True, verbose_name='Site')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
            ],
            options={
                'verbose_name': 'Editora',
                'verbose_name_plural': 'Editoras',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Livro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('subtitulo', models.CharField(blank=True, max_length=200, null=True, verbose_name='Subtítulo')),
                ('isbn', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='ISBN')),
                ('codigo_barras', models.CharField(max_length=50, unique=True, verbose_name='Código de Barras')),
                ('ano_publicacao', models.IntegerField(validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(2100)], verbose_name='Ano de Publicação')),
                ('edicao', models.CharField(blank=True, max_length=50, null=True, verbose_name='Edição')),
                ('idioma', models.CharField(default='Português', max_length=50, verbose_name='Idioma')),
                ('paginas', models.IntegerField(blank=True, null=True, verbose_name='Número de Páginas')),
                ('tipo', models.CharField(choices=[('livro', 'Livro'), ('revista', 'Revista'), ('jornal', 'Jornal'), ('manual', 'Manual'), ('apostila', 'Apostila'), ('dvd', 'DVD'), ('cd', 'CD'), ('outro', 'Outro')], default='livro', max_length=20, verbose_name='Tipo')),
                ('status', models.CharField(choices=[('disponivel', 'Disponível'), ('emprestado', 'Emprestado'), ('reservado', 'Reservado'), ('manutencao', 'Manutenção'), ('perdido', 'Perdido'), ('danificado', 'Danificado')], default='disponivel', max_length=20, verbose_name='Status')),
                ('localizacao', models.CharField(help_text='Ex: Estante A, Prateleira 3', max_length=100, verbose_name='Localização')),
                ('exemplares_total', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Total de Exemplares')),
                ('exemplares_disponiveis', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Exemplares Disponíveis')),
                ('valor_livro', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor do Livro')),
                ('sinopse', models.TextField(blank=True, null=True, verbose_name='Sinopse')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('capa', models.ImageField(blank=True, null=True, upload_to='livros/capas/', verbose_name='Capa')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última atualização')),
                ('autores', models.ManyToManyField(to='biblioteca.autor', verbose_name='Autores')),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.categoria', verbose_name='Categoria')),
                ('editora', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.editora', verbose_name='Editora')),
            ],
            options={
                'verbose_name': 'Livro',
                'verbose_name_plural': 'Livros',
                'ordering': ['titulo'],
            },
        ),
        migrations.CreateModel(
            name='Emprestimo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_usuario', models.CharField(choices=[('aluno', 'Aluno'), ('professor', 'Professor')], max_length=10, verbose_name='Tipo de Usuário')),
                ('data_emprestimo', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data do Empréstimo')),
                ('data_prevista_devolucao', models.DateField(verbose_name='Data Prevista para Devolução')),
                ('data_devolucao', models.DateTimeField(blank=True, null=True, verbose_name='Data da Devolução')),
                ('status', models.CharField(choices=[('ativo', 'Ativo'), ('devolvido', 'Devolvido'), ('atrasado', 'Atrasado'), ('perdido', 'Perdido'), ('renovado', 'Renovado')], default='ativo', max_length=15, verbose_name='Status')),
                ('renovacoes', models.IntegerField(default=0, verbose_name='Número de Renovações')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('valor_multa', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Valor da Multa')),
                ('multa_paga', models.BooleanField(default=False, verbose_name='Multa Paga')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última atualização')),
                ('aluno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='alunos.aluno', verbose_name='Aluno')),
                ('professor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='professores.professor', verbose_name='Professor')),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblioteca.livro', verbose_name='Livro')),
            ],
            options={
                'verbose_name': 'Empréstimo',
                'verbose_name_plural': 'Empréstimos',
                'ordering': ['-data_emprestimo'],
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_usuario', models.CharField(choices=[('aluno', 'Aluno'), ('professor', 'Professor')], max_length=10, verbose_name='Tipo de Usuário')),
                ('data_reserva', models.DateTimeField(auto_now_add=True, verbose_name='Data da Reserva')),
                ('data_expiracao', models.DateTimeField(verbose_name='Data de Expiração')),
                ('status', models.CharField(choices=[('ativa', 'Ativa'), ('atendida', 'Atendida'), ('cancelada', 'Cancelada'), ('expirada', 'Expirada')], default='ativa', max_length=15, verbose_name='Status')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última atualização')),
                ('aluno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='alunos.aluno', verbose_name='Aluno')),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblioteca.livro', verbose_name='Livro')),
                ('professor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='professores.professor', verbose_name='Professor')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['-data_reserva'],
                'unique_together': {('livro', 'aluno', 'professor', 'status')},
            },
        ),
    ]
