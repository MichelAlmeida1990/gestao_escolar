# Guia de Deploy - Sistema de Gestão Escolar

Este guia te ajudará a fazer o deploy da aplicação Django em diferentes plataformas.

## 📋 Pré-requisitos

- Python 3.11+
- Git
- Conta no GitHub
- Conta na plataforma de deploy escolhida

## 🚀 Opções de Deploy

### 1. Heroku (Recomendado para iniciantes)

#### Passo a Passo:

1. **Criar conta no Heroku**
   - Acesse [heroku.com](https://heroku.com)
   - Crie uma conta gratuita

2. **Instalar Heroku CLI**
   ```bash
   # Windows (com chocolatey)
   choco install heroku-cli
   
   # Ou baixe do site oficial
   ```

3. **Fazer login no Heroku**
   ```bash
   heroku login
   ```

4. **Criar aplicação no Heroku**
   ```bash
   heroku create sua-app-gestao-escolar
   ```

5. **Configurar variáveis de ambiente**
   ```bash
   heroku config:set SECRET_KEY="sua-chave-secreta-muito-segura"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="sua-app-gestao-escolar.herokuapp.com"
   ```

6. **Adicionar banco PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

7. **Fazer deploy**
   ```bash
   git push heroku master
   ```

8. **Executar migrações**
   ```bash
   heroku run python manage.py migrate
   ```

9. **Criar superusuário**
   ```bash
   heroku run python manage.py createsuperuser
   ```

### 2. Railway (Alternativa gratuita)

1. **Criar conta no Railway**
   - Acesse [railway.app](https://railway.app)
   - Conecte com GitHub

2. **Deploy automático**
   - Conecte o repositório
   - Configure as variáveis de ambiente
   - Railway detecta automaticamente que é Django

### 3. PythonAnywhere (Para aprendizado)

1. **Criar conta no PythonAnywhere**
   - Acesse [pythonanywhere.com](https://pythonanywhere.com)
   - Crie conta gratuita

2. **Configurar projeto**
   - Clone o repositório
   - Configure WSGI
   - Configure variáveis de ambiente

## 🔧 Configurações Importantes

### Variáveis de Ambiente

Copie o arquivo `env.example` para `.env` e configure:

```bash
# Configurações do Django
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com

# Configurações do Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco

# Configurações de Segurança
SECURE_SSL_REDIRECT=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
```

### Comandos de Deploy

```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

## 📁 Estrutura de Arquivos para Deploy

```
gestao_escolar/
├── requirements.txt      # Dependências Python
├── Procfile             # Configuração Heroku
├── runtime.txt          # Versão Python
├── config/
│   ├── settings.py      # Configurações desenvolvimento
│   └── settings_production.py  # Configurações produção
├── static/              # Arquivos estáticos
├── templates/           # Templates HTML
└── manage.py           # Script Django
```

## 🔒 Segurança

### Antes do Deploy:

1. **Alterar SECRET_KEY**
   ```python
   # Gere uma nova chave
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Configurar DEBUG=False**
   ```python
   DEBUG = False
   ```

3. **Configurar ALLOWED_HOSTS**
   ```python
   ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']
   ```

4. **Configurar HTTPS**
   ```python
   SECURE_SSL_REDIRECT = True
   CSRF_COOKIE_SECURE = True
   SESSION_COOKIE_SECURE = True
   ```

## 🐛 Troubleshooting

### Problemas Comuns:

1. **Erro de arquivos estáticos**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Erro de migração**
   ```bash
   python manage.py migrate --run-syncdb
   ```

3. **Erro de dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Erro de configuração**
   - Verifique se todas as variáveis de ambiente estão configuradas
   - Verifique se o arquivo `settings_production.py` está sendo usado

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs da aplicação
2. Teste localmente com `settings_production.py`
3. Verifique se todas as dependências estão no `requirements.txt`

## 🎯 Próximos Passos

Após o deploy bem-sucedido:

1. Configure um domínio personalizado
2. Configure backup automático do banco
3. Configure monitoramento
4. Configure CI/CD para deploy automático 