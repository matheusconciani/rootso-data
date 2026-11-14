import os
from pathlib import Path

import matplotlib.pyplot as plt
import oracledb
import polars as pl

from importar_leituras import carregar_env_local


RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados" / "tratado"
IMAGENS = RAIZ / "docs" / "imagens"


def buscar_leituras():
    senha = os.getenv("APP_USER_PASSWORD")
    if not senha:
        raise RuntimeError("Defina APP_USER_PASSWORD no arquivo .env.")

    conexao = oracledb.connect(
        user=os.getenv("ORACLE_APP_USER", "ROOTSO"),
        password=senha,
        dsn=os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1"),
    )
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT data_hora, umidade, ph, fosforo, potassio, bomba, origem
                FROM leituras_sensor
                ORDER BY data_hora
                """
            )
            linhas = cursor.fetchall()
    finally:
        conexao.close()

    if not linhas:
        raise RuntimeError("A tabela LEITURAS_SENSOR não possui registros.")

    return pl.DataFrame(
        linhas,
        schema=[
            "data_hora",
            "umidade",
            "ph",
            "fosforo",
            "potassio",
            "bomba",
            "origem",
        ],
        orient="row",
    )


def gerar_resumo(df: pl.DataFrame):
    resumo = df.select(
        pl.len().alias("total_leituras"),
        pl.col("data_hora").min().alias("primeira_leitura"),
        pl.col("data_hora").max().alias("ultima_leitura"),
        pl.col("umidade").mean().round(2).alias("umidade_media"),
        pl.col("ph").mean().round(2).alias("ph_medio"),
        (pl.col("fosforo").mean() * 100).round(2).alias("fosforo_adequado_pct"),
        (pl.col("potassio").mean() * 100).round(2).alias("potassio_adequado_pct"),
        (pl.col("bomba").mean() * 100)
        .round(2)
        .alias("percentual_leituras_bomba_ligada"),
    )
    resumo.write_csv(SAIDA / "resumo_indicadores.csv")


def gerar_graficos(df: pl.DataFrame):
    datas = df["data_hora"].to_list()

    figura, eixos = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    eixos[0].plot(datas, df["umidade"].to_list(), marker="o", color="#1976D2")
    eixos[0].set_title("Umidade ao longo do tempo")
    eixos[0].set_ylabel("Umidade (%)")
    eixos[0].grid(True, alpha=0.3)

    eixos[1].plot(datas, df["ph"].to_list(), marker="o", color="#EF6C00")
    eixos[1].set_title("pH simulado ao longo do tempo")
    eixos[1].set_ylabel("pH")
    eixos[1].set_ylim(0, 14)
    eixos[1].grid(True, alpha=0.3)

    eixos[2].step(
        datas,
        df["bomba"].to_list(),
        where="post",
        color="#2E7D32",
        label="Bomba",
    )
    eixos[2].set_title("Acionamento da bomba")
    eixos[2].set_ylabel("Estado")
    eixos[2].set_yticks([0, 1], ["Desligada", "Ligada"])
    eixos[2].grid(True, alpha=0.3)

    figura.tight_layout()
    IMAGENS.mkdir(parents=True, exist_ok=True)
    figura.savefig(SAIDA / "leituras_tendencias.png", dpi=150)
    figura.savefig(IMAGENS / "leituras_tendencias.png", dpi=150)
    plt.close(figura)


def gerar_correlacoes(df: pl.DataFrame):
    colunas = ["umidade", "ph", "fosforo", "potassio", "bomba"]
    correlacoes = df.select(colunas).corr()
    correlacoes.write_csv(SAIDA / "correlacoes.csv")

    matriz = correlacoes.to_numpy()
    figura, eixo = plt.subplots(figsize=(7, 6))
    imagem = eixo.imshow(matriz, vmin=-1, vmax=1, cmap="coolwarm")
    eixo.set_xticks(range(len(colunas)), colunas, rotation=45, ha="right")
    eixo.set_yticks(range(len(colunas)), colunas)
    eixo.set_title("Correlação entre variáveis")
    figura.colorbar(imagem, ax=eixo, label="Correlação")

    for linha in range(len(colunas)):
        for coluna in range(len(colunas)):
            eixo.text(
                coluna,
                linha,
                f"{matriz[linha, coluna]:.2f}",
                ha="center",
                va="center",
                color="black",
            )

    figura.tight_layout()
    figura.savefig(SAIDA / "mapa_correlacoes.png", dpi=150)
    IMAGENS.mkdir(parents=True, exist_ok=True)
    figura.savefig(IMAGENS / "mapa_correlacoes.png", dpi=150)
    plt.close(figura)


def main():
    carregar_env_local()
    SAIDA.mkdir(parents=True, exist_ok=True)
    leituras = buscar_leituras()
    leituras.write_csv(SAIDA / "leituras_tratadas.csv")
    gerar_resumo(leituras)
    gerar_graficos(leituras)
    gerar_correlacoes(leituras)
    print(f"{leituras.height} leitura(s) analisada(s).")
    print(f"Arquivos gerados em: {SAIDA}")


if __name__ == "__main__":
    main()
