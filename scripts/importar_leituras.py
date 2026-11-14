import argparse
import csv
import os
from pathlib import Path

import oracledb


def carregar_env_local():
    caminho_env = Path(__file__).resolve().parents[1] / ".env"
    if not caminho_env.exists():
        return

    for linha in caminho_env.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        os.environ.setdefault(nome.strip(), valor.strip())


def ler_registros(caminho: Path):
    registros = []

    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha.startswith("ROOTSO_CSV;"):
                continue

            campos = next(csv.reader([linha], delimiter=";"))
            if len(campos) != 8:
                raise ValueError(
                    f"Linha {numero_linha}: esperado 8 campos, recebido {len(campos)}."
                )
            if campos[1] == "data_hora":
                continue

            data_hora, umidade, ph, fosforo, potassio, bomba, origem = campos[1:]
            registros.append(
                (
                    data_hora,
                    None if umidade == "-1" else float(umidade),
                    float(ph),
                    int(fosforo),
                    int(potassio),
                    int(bomba),
                    origem,
                )
            )

    if not registros:
        raise ValueError("Nenhum registro ROOTSO_CSV foi encontrado no arquivo.")

    return registros


def carregar(registros):
    senha = os.getenv("APP_USER_PASSWORD")
    if not senha:
        raise RuntimeError("Defina a variável de ambiente APP_USER_PASSWORD.")

    conexao = oracledb.connect(
        user=os.getenv("ORACLE_APP_USER", "ROOTSO"),
        password=senha,
        dsn=os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1"),
    )
    try:
        with conexao.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO leituras_sensor
                    (data_hora, umidade, ph, fosforo, potassio, bomba, origem)
                VALUES
                    (TO_TIMESTAMP(:1, 'YYYY-MM-DD HH24:MI:SS'),
                     :2, :3, :4, :5, :6, :7)
                """,
                registros,
            )
        conexao.commit()
    finally:
        conexao.close()


def main():
    carregar_env_local()
    parser = argparse.ArgumentParser(
        description="Importa registros ROOTSO_CSV para o Oracle."
    )
    parser.add_argument("arquivo", type=Path, help="Arquivo bruto do Monitor Serial.")
    argumentos = parser.parse_args()

    registros = ler_registros(argumentos.arquivo)
    carregar(registros)
    print(f"{len(registros)} registro(s) importado(s) com sucesso.")


if __name__ == "__main__":
    main()
