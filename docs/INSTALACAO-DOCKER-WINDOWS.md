# Instalação do Docker Desktop no Windows

Este guia prepara o computador para executar o Oracle em um container. Um
container é um ambiente isolado que executa um programa sem instalar todos os
arquivos dele diretamente no Windows.

## 1. Verifique os pré-requisitos

Segundo a documentação oficial do Docker, a opção recomendada é usar o WSL 2
(Windows Subsystem for Linux 2). Em geral, são necessários:

- Windows 10 ou 11 de 64 bits em edição compatível;
- virtualização habilitada na BIOS/UEFI;
- pelo menos 8 GB de memória RAM;
- WSL 2 instalado e atualizado.

Se o computador for Windows Home, use containers Linux com WSL 2. Containers
Windows exigem edições Pro ou Enterprise.

## 2. Instale o Docker Desktop

1. Abra a documentação oficial:
   <https://docs.docker.com/desktop/setup/install/windows-install/>
2. Baixe o instalador para computadores x86_64, que é a opção comum.
3. Execute `Docker Desktop Installer.exe`.
4. Mantenha a instalação por usuário, se essa opção estiver disponível.
5. Selecione **Use WSL 2 instead of Hyper-V**.
6. Finalize a instalação e abra o Docker Desktop.
7. Aceite os termos apresentados pelo programa.

Não é necessário executar comandos de instalação como administrador se a opção
por usuário funcionar no seu computador.

## 3. Verifique a instalação

Abra o PowerShell e execute:

```powershell
docker --version
docker info
```

O primeiro comando deve mostrar a versão instalada. O segundo deve mostrar
informações do Docker sem erro de conexão com o daemon. O daemon é o serviço
que executa e gerencia os containers.

Também é possível executar um teste simples:

```powershell
docker run --rm hello-world
```

O texto final deve informar que a instalação funcionou.

## 4. Próximo passo

Depois que esses comandos funcionarem, será escolhida e documentada a imagem
Oracle adequada. Nenhuma senha ou credencial deve ser colocada no GitHub.

## 5. Arquivos do Oracle deste projeto

Na pasta da atividade existem:

- `docker-compose.yml`: descreve o container Oracle e o volume persistente;
- `.env.example`: modelo das senhas locais;
- `.gitignore`: impede o envio do `.env` real ao GitHub.

Para usar a configuração:

```powershell
Copy-Item .env.example .env
notepad .env
docker compose up -d
docker compose ps
```

O arquivo `.env` deve ser criado somente no computador local. A senha usada
deve ser pessoal e não deve ser enviada nesta conversa nem incluída em arquivos
versionados.

Fonte consultada: documentação oficial do Docker, seção de instalação no
Windows.
