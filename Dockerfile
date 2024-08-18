# Usar la imagen base pública de AWS Lambda para Python 3.9
FROM public.ecr.aws/lambda/python:3.9

# Copiar el archivo requirements.txt al directorio de trabajo
COPY src/requirements.txt .

# Instalar las dependencias en el directorio raíz (que es la ruta por defecto en Lambda)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación al directorio raíz
COPY src/ .

# Comando para iniciar la Lambda localmente
CMD ["app.lambda_handler"]
