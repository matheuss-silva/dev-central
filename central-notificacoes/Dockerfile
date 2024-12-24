# Usar uma imagem oficial do Python 3.10 slim
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para o container
COPY . .

# Instalar as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando padrão para iniciar o servidor ASGI
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "central_notificacoes.asgi:application"]
