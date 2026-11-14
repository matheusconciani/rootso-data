import math
import os
from datetime import timedelta

import oracledb

from importar_leituras import carregar_env_local


QUANTIDADE = 48
ORIGEM = "simulador_diversificado"


def conectar():
    senha = os.getenv("APP_USER_PASSWORD")
    if not senha:
        raise RuntimeError("Defina APP_USER_PASSWORD no arquivo .env.")
    return oracledb.connect(
        user=os.getenv("ORACLE_APP_USER", "ROOTSO"),
        password=senha,
        dsn=os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1"),
    )


def gerar_registros(inicio):
    registros = []
    for indice in range(QUANTIDADE):
        data_hora = inicio + timedelta(hours=indice + 1)
        umidade = round(44 + 12 * math.sin(indice / 5) - indice * 0.04, 1)
        ph = round(5.8 + 1.4 * math.sin(indice / 7), 1)
        fosforo = 1 if indice % 6 in (1, 2, 3, 4) else 0
        potassio = 1 if indice % 5 in (0, 1, 2) else 0
        bomba = 1 if umidade < 40 else 0
        registros.append(
            (data_hora, umidade, ph, fosforo, potassio, bomba, ORIGEM)
        )
    return registros


def main():
    carregar_env_local()
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM leituras_sensor WHERE origem = :origem",
                origem=ORIGEM,
            )
            if cursor.fetchone()[0]:
                raise RuntimeError(
                    "Os dados diversificados já foram inseridos. "
                    "Nenhum registro foi alterado."
                )

            cursor.execute("SELECT MAX(data_hora) FROM leituras_sensor")
            inicio = cursor.fetchone()[0]
            if inicio is None:
                raise RuntimeError("Não existem leituras originais para continuar.")

            registros = gerar_registros(inicio)
            cursor.executemany(
                """
                INSERT INTO leituras_sensor
                    (data_hora, umidade, ph, fosforo, potassio, bomba, origem)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
                """,
                registros,
            )
        conexao.commit()
    finally:
        conexao.close()

    print(f"{len(registros)} registros diversificados inseridos.")


if __name__ == "__main__":
    main()
