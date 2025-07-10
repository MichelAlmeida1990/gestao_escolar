# Gestão Escolar

Sistema completo para gestão de escolas, incluindo módulos de alunos, professores, turmas, notas, frequência, biblioteca, financeiro, comunicados e muito mais. O objetivo é facilitar o controle acadêmico, financeiro e administrativo de instituições de ensino.

## Funcionalidades Principais
- **Gestão de Alunos:** Cadastro, edição, exclusão, listagem e detalhes dos alunos.
- **Gestão de Professores:** Cadastro, turmas, disciplinas e perfil dos professores.
- **Turmas:** Criação, gerenciamento de alunos e professores por turma.
- **Notas e Avaliações:** Lançamento de notas, boletim do aluno, desempenho por turma e disciplina.
- **Frequência:** Registro de presença, justificativas de falta, relatórios de frequência.
- **Financeiro:** Geração e controle de mensalidades, relatórios financeiros, painel de estatísticas.
- **Biblioteca:** Cadastro de livros, empréstimos, reservas e devoluções.
- **Comunicados:** Envio e gerenciamento de comunicados para a comunidade escolar.
- **Responsáveis:** Cadastro e vinculação de responsáveis aos alunos.
- **Autenticação e Perfis de Usuário:** Login, recuperação de senha, perfis diferenciados (admin, professor, responsável, aluno).

## Tecnologias Utilizadas
- **Backend:** Python 3, Django
- **Frontend:** Django Templates, Bootstrap, FontAwesome, Chart.js
- **Banco de Dados:** SQLite (padrão), compatível com PostgreSQL
- **Outros:** AOS (animações), comandos customizados de management

## Estrutura do Projeto
```
├── alunos/           # Módulo de alunos
├── professores/      # Módulo de professores
├── turmas/           # Módulo de turmas
├── notas/            # Módulo de notas e avaliações
├── frequencia/       # Módulo de frequência
├── biblioteca/       # Módulo de biblioteca
├── financeiro/       # Módulo financeiro
├── comunicados/      # Módulo de comunicados
├── responsaveis/     # Módulo de responsáveis
├── core/             # Configurações e utilitários centrais
├── usuarios/         # Autenticação e perfis de usuário
├── templates/        # Templates HTML globais e por app
├── static/           # Arquivos estáticos (CSS, JS, imagens)
├── manage.py         # Gerenciador Django
├── requirements.txt  # Dependências do projeto
```

## Instalação e Execução Local
1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd gestao_escolar
   ```
2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure as variáveis de ambiente:**
   - Copie o arquivo `env.example` para `.env` e ajuste conforme necessário.

5. **Aplique as migrações:**
   ```bash
   python manage.py migrate
   ```
6. **Crie um superusuário:**
   ```bash
   python manage.py createsuperuser
   ```
7. **Execute o servidor de desenvolvimento:**
   ```bash
   python manage.py runserver
   ```

Acesse em: http://127.0.0.1:8000/

## Populando o Banco de Dados com Dados de Exemplo
O projeto possui comandos customizados para popular o banco com dados de teste:

- **Popular sistema completo:**
  ```bash
  python manage.py popular_sistema_completo
  ```
- **Popular apenas alunos, professores, turmas, etc:**
  ```bash
  python manage.py popular_sistema
  ```
- **Popular biblioteca:**
  ```bash
  python manage.py popular_livros
  ```
- **Popular matrículas:**
  ```bash
  python manage.py popular_matriculas
  ```

## Rodando os Testes
Execute os testes de cada app com:
```bash
python manage.py test <nome_do_app>
# Exemplo:
python manage.py test alunos
```

## Deploy
O projeto está pronto para deploy em plataformas como **Railway** e **Render**. Veja os arquivos `RENDER_DEPLOY.md`, `railway.json`, `render.yaml` e `render_env.txt` para instruções específicas.

- **Configuração de ambiente:**
  - Defina as variáveis de ambiente conforme o arquivo `env.example`.
  - Configure o banco de dados (PostgreSQL recomendado para produção).

- **Coleta de arquivos estáticos:**
  ```bash
  python manage.py collectstatic
  ```

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Contato
Dúvidas, sugestões ou problemas? Entre em contato pelo e-mail do mantenedor ou abra uma issue no repositório.

---

**Gestão Escolar** © Todos os direitos reservados. 