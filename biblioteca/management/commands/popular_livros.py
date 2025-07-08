from django.core.management.base import BaseCommand
from biblioteca.models import Livro, Autor, Editora, Categoria
import random

LIVROS_REAIS = [
    {
        'titulo': 'Dom Casmurro',
        'autor': 'Machado de Assis',
        'editora': 'Editora Globo',
        'ano_publicacao': 1899,
        'isbn': '9788525044649',
    },
    {
        'titulo': 'O Pequeno Príncipe',
        'autor': 'Antoine de Saint-Exupéry',
        'editora': 'Agir',
        'ano_publicacao': 1943,
        'isbn': '9788522005230',
    },
    {
        'titulo': 'Capitães da Areia',
        'autor': 'Jorge Amado',
        'editora': 'Companhia das Letras',
        'ano_publicacao': 1937,
        'isbn': '9788535914849',
    },
    {
        'titulo': 'Harry Potter e a Pedra Filosofal',
        'autor': 'J.K. Rowling',
        'editora': 'Rocco',
        'ano_publicacao': 1997,
        'isbn': '9788532511010',
    },
    {
        'titulo': 'A Menina que Roubava Livros',
        'autor': 'Markus Zusak',
        'editora': 'Intrínseca',
        'ano_publicacao': 2005,
        'isbn': '9788580575393',
    },
    {
        'titulo': 'O Alquimista',
        'autor': 'Paulo Coelho',
        'editora': 'Paralela',
        'ano_publicacao': 1988,
        'isbn': '9788575428770',
    },
    {
        'titulo': '1984',
        'autor': 'George Orwell',
        'editora': 'Companhia das Letras',
        'ano_publicacao': 1949,
        'isbn': '9788535902774',
    },
    {
        'titulo': 'O Senhor dos Anéis: A Sociedade do Anel',
        'autor': 'J.R.R. Tolkien',
        'editora': 'Martins Fontes',
        'ano_publicacao': 1954,
        'isbn': '9788533603147',
    },
    {
        'titulo': 'A Revolução dos Bichos',
        'autor': 'George Orwell',
        'editora': 'Companhia das Letras',
        'ano_publicacao': 1945,
        'isbn': '9788535909551',
    },
    {
        'titulo': 'O Diário de Anne Frank',
        'autor': 'Anne Frank',
        'editora': 'Record',
        'ano_publicacao': 1947,
        'isbn': '9788501045181',
    },
]

class Command(BaseCommand):
    help = 'Popula a biblioteca com livros reais famosos.'

    def handle(self, *args, **kwargs):
        criados = 0
        categoria, _ = Categoria.objects.get_or_create(nome='Literatura', defaults={'descricao': 'Livros de literatura'})
        for idx, livro in enumerate(LIVROS_REAIS):
            autor_obj, _ = Autor.objects.get_or_create(nome=livro['autor'])
            editora_obj, _ = Editora.objects.get_or_create(nome=livro['editora'])
            codigo_barras = f"{random.randint(1000000000000, 9999999999999)}{idx}"
            livro_obj, created = Livro.objects.get_or_create(
                titulo=livro['titulo'],
                isbn=livro['isbn'],
                defaults={
                    'codigo_barras': codigo_barras,
                    'categoria': categoria,
                    'editora': editora_obj,
                    'ano_publicacao': livro['ano_publicacao'],
                    'localizacao': 'Estante A',
                    'exemplares_total': 3,
                    'exemplares_disponiveis': 3,
                }
            )
            if created:
                livro_obj.autores.add(autor_obj)
                criados += 1
        self.stdout.write(self.style.SUCCESS(f'{criados} livros reais adicionados à biblioteca!')) 