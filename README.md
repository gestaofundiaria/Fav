# Gestão Fundiária

Aplicação web para gestão fundiária com autenticação segura.

## Instalação

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure o arquivo `.env` com suas variáveis sensíveis:
   ```
   USER_SECRET_KEY=your_super_secret_key_here
   USER_COOKIE_SECURE=1  # 1 para produção HTTPS
   SUPABASE_URL=https://ozsdqkpiozhbrpoztldb.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
   ```

3. Execute a aplicação:
   ```bash
   python app.py
   ```

## Gerenciamento de Usuários

Use o script `manage_users.py` para gerenciar usuários:

- Adicionar usuário: `python manage_users.py add <login> <senha> [email]`
- Listar usuários: `python manage_users.py list`
- Deletar usuário: `python manage_users.py delete <login>`
- Atualizar senha: `python manage_users.py update <login> <nova_senha>`

## Deploy no Render

O projeto está configurado para deploy no Render via `render.yaml`. As variáveis de ambiente são geradas automaticamente.

## Migração para Supabase

Para migrar os usuários existentes do SQLite para Supabase, execute:

```bash
python migrate_sqlite_to_supabase.py
```

Certifique-se de que `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` estejam definidos no `.env`.

## Segurança

- Senhas hashed com bcrypt
- Sessões seguras com HttpOnly cookies
- Controle de tentativas de login
- Autenticação de usuários armazenada no Supabase
- Separação frontend/backend

## Arquivos Importantes

- `app.py`: Aplicação principal
- `auth.py`: Funções de autenticação usando Supabase
- `manage_users.py`: Gerenciamento de usuários no Supabase
- `.env`: Variáveis de ambiente (não versionado)
