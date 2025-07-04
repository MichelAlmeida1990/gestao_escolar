# Generated by Django 5.1.6 on 2025-06-25 14:48

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alunos', '0002_alter_aluno_options_remove_aluno_responsavel_and_more'),
        ('turmas', '0002_turmaaluno_turmaprofessor'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome da Categoria')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('cor', models.CharField(default='#007bff', max_length=7, verbose_name='Cor (Hex)')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
            ],
            options={
                'verbose_name': 'Categoria Financeira',
                'verbose_name_plural': 'Categorias Financeiras',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='ConfiguracaoFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_padrao_mensalidade', models.DecimalField(decimal_places=2, default=150.0, max_digits=10, verbose_name='Valor Padrão da Mensalidade')),
                ('dia_vencimento_mensalidade', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)], verbose_name='Dia de Vencimento da Mensalidade')),
                ('percentual_juros_mes', models.DecimalField(decimal_places=2, default=1.0, max_digits=5, verbose_name='Juros ao Mês (%)')),
                ('valor_multa_atraso', models.DecimalField(decimal_places=2, default=10.0, max_digits=10, verbose_name='Multa por Atraso (R$)')),
                ('dias_carencia_juros', models.IntegerField(default=5, verbose_name='Dias de Carência para Juros')),
                ('percentual_desconto_pontualidade', models.DecimalField(decimal_places=2, default=5.0, max_digits=5, verbose_name='Desconto por Pontualidade (%)')),
                ('percentual_desconto_irmao', models.DecimalField(decimal_places=2, default=10.0, max_digits=5, verbose_name='Desconto para Irmãos (%)')),
                ('nome_escola', models.CharField(default='Escola', max_length=200, verbose_name='Nome da Escola')),
                ('cnpj_escola', models.CharField(blank=True, max_length=20, null=True, verbose_name='CNPJ da Escola')),
                ('endereco_escola', models.TextField(blank=True, null=True, verbose_name='Endereço da Escola')),
            ],
            options={
                'verbose_name': 'Configuração Financeira',
                'verbose_name_plural': 'Configurações Financeiras',
            },
        ),
        migrations.CreateModel(
            name='PlanoContas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('nome', models.CharField(max_length=150, verbose_name='Nome')),
                ('tipo', models.CharField(choices=[('receita', 'Receita'), ('despesa', 'Despesa')], max_length=10, verbose_name='Tipo')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
            ],
            options={
                'verbose_name': 'Plano de Contas',
                'verbose_name_plural': 'Planos de Contas',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='Mensalidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes_referencia', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='Mês de Referência')),
                ('ano_referencia', models.IntegerField(validators=[django.core.validators.MinValueValidator(2000), django.core.validators.MaxValueValidator(2100)], verbose_name='Ano de Referência')),
                ('valor_base', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor Base')),
                ('valor_desconto', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Valor do Desconto')),
                ('tipo_desconto', models.CharField(choices=[('valor', 'Valor Fixo'), ('percentual', 'Percentual')], default='valor', max_length=10, verbose_name='Tipo de Desconto')),
                ('valor_juros', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Valor dos Juros')),
                ('valor_multa', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Valor da Multa')),
                ('valor_total', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor Total')),
                ('data_vencimento', models.DateField(verbose_name='Data de Vencimento')),
                ('data_pagamento', models.DateTimeField(blank=True, null=True, verbose_name='Data do Pagamento')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('pago', 'Pago'), ('vencido', 'Vencido'), ('cancelado', 'Cancelado')], default='pendente', max_length=15, verbose_name='Status')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('descricao_desconto', models.CharField(blank=True, max_length=200, null=True, verbose_name='Descrição do Desconto')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última atualização')),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alunos.aluno', verbose_name='Aluno')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turmas.turma', verbose_name='Turma')),
            ],
            options={
                'verbose_name': 'Mensalidade',
                'verbose_name_plural': 'Mensalidades',
                'ordering': ['-ano_referencia', '-mes_referencia', 'aluno__nome'],
                'unique_together': {('aluno', 'mes_referencia', 'ano_referencia')},
            },
        ),
    ]
