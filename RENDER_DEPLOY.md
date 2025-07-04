# 🚀 Deploy no Render - Guia Completo

## ✅ Por que Render?

- **Totalmente gratuito** para projetos pequenos
- **Deploy automático** do GitHub
- **Banco PostgreSQL** incluído
- **SSL automático** (HTTPS)
- **Interface web** muito intuitiva
- **Muito estável** e confiável

## 📋 Passo a Passo

### 1. Criar conta no Render

1. Acesse [render.com](https://render.com)
2. Clique em "Get Started for Free"
3. Faça login com sua conta GitHub
4. Complete o cadastro

### 2. Conectar repositório

1. No dashboard, clique em "New +"
2. Escolha "Web Service"
3. Conecte com GitHub
4. Selecione o repositório `gestao_escolar`

### 3. Configurar o serviço

**Nome:** `gestao-escolar`
**Runtime:** `Python 3`
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `gunicorn config.wsgi:application`

### 4. Configurar variáveis de ambiente

Clique em "Environment" e adicione:

```
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
```

### 5. Configurar banco de dados

1. No dashboard, clique em "New +"
2. Escolha "PostgreSQL"
3. Configure:
   - **Nome:** `gestao-escolar-db`
   - **Database:** `gestao_escolar`
   - **User:** `gestao_escolar_user`

### 6. Conectar banco ao serviço

1. No seu serviço web, vá em "Environment"
2. Adicione a variável `DATABASE_URL` que o Render fornece
3. Clique em "Save Changes"

### 7. Deploy

1. Clique em "Create Web Service"
2. Render vai fazer o deploy automaticamente
3. Aguarde alguns minutos

### 8. Executar migrações

1. No dashboard, vá em "Shell"
2. Execute os comandos:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 🔧 Configurações Automáticas

O Render vai:
- ✅ Detectar que é Django
- ✅ Instalar dependências do `requirements.txt`
- ✅ Configurar PostgreSQL automaticamente
- ✅ Executar migrações automaticamente
- ✅ Coletar arquivos estáticos
- ✅ Iniciar com Gunicorn

## 🌐 Acessar a aplicação

Após o deploy, você receberá um URL como:
`https://gestao-escolar.onrender.com`

## 🐛 Troubleshooting

### Se der erro de migração:
```bash
python manage.py migrate --run-syncdb
```

### Se der erro de arquivos estáticos:
```bash
python manage.py collectstatic --noinput --clear
```

### Se der erro de dependências:
Verifique se todas estão no `requirements.txt`

## 📊 Monitoramento

No Render você pode:
- Ver logs em tempo real
- Monitorar uso de recursos
- Configurar alertas
- Fazer rollback de versões

## 💰 Custos

- **Gratuito**: 
  - 750 horas/mês
  - 512 MB RAM
  - 1 GB storage
- **$7/mês**: Plano Starter
- **$25/mês**: Plano Standard

## 🎯 Próximos passos

1. Configure domínio personalizado
2. Configure backup automático
3. Configure monitoramento
4. Configure CI/CD

## 📞 Suporte

- [Documentação Render](https://render.com/docs)
- [Comunidade Discord](https://discord.gg/render)
- [GitHub Issues](https://github.com/render-oss/render) 