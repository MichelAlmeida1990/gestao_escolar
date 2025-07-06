# 🚀 Deploy Rápido no Render - Checklist

## ✅ Variáveis de Ambiente Obrigatórias

No Render, vá em **Configurações > Variáveis de ambiente** e adicione:

### 1. **DJANGO_SETTINGS_MODULE** (CRÍTICO!)
```
config.settings_production
```

### 2. **SECRET_KEY**
```
*pt*8xfmm&nxhrcisr&3_1=acm^@%7vrx9+%isf35q^=@va5yz
```

### 3. **DEBUG**
```
False
```

### 4. **ALLOWED_HOSTS**
```
gestao-escolar-6tfz.onrender.com,.onrender.com
```

### 5. **DATABASE_URL**
```
(copie do seu banco PostgreSQL do Render)
```

## 🔒 Variáveis de Segurança (Opcionais mas recomendadas)

### 6. **SECURE_SSL_REDIRECT**
```
True
```

### 7. **CSRF_COOKIE_SECURE**
```
True
```

### 8. **SESSION_COOKIE_SECURE**
```
True
```

### 9. **CSRF_TRUSTED_ORIGINS**
```
https://gestao-escolar-6tfz.onrender.com
```

---

## 📋 Passo a Passo:

1. ✅ **Criar banco PostgreSQL** no Render
2. ✅ **Criar serviço web** conectado ao GitHub
3. ✅ **Adicionar todas as variáveis** acima
4. ✅ **Reiniciar o serviço** 
5. ✅ **Acessar a aplicação**
6. ✅ **Rodar migrações** no Shell do Render:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

---

## 🐛 Se der erro:

- **Host não permitido**: Verifique `ALLOWED_HOSTS` e `DJANGO_SETTINGS_MODULE`
- **Erro de banco**: Verifique `DATABASE_URL`
- **Erro de static files**: Execute `python manage.py collectstatic --noinput`
- **Erro 500**: Verifique `SECRET_KEY` e `DEBUG=False`

---

## 🎯 URL Final:
```
https://gestao-escolar-6tfz.onrender.com
``` 