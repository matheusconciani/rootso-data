# Análise dos dados agrícolas

## Metodologia

As leituras foram armazenadas no Oracle na tabela `LEITURAS_SENSOR` e
analisadas com Python, usando Polars para a manipulação dos dados. Os
registros originais do Wokwi foram mantidos e receberam dados adicionais
simulados para ampliar a variação temporal.

Todos os registros adicionados artificialmente estão identificados com a
origem `simulador_diversificado`. Portanto, eles não devem ser interpretados
como medições físicas reais.

## Resultados atuais

O conjunto possui 76 leituras horárias:

| Indicador | Resultado |
|---|---:|
| Umidade média | 45,52% |
| pH médio | 4,93 |
| Fósforo adequado | 44,74% das leituras |
| Potássio adequado | 43,42% das leituras |
| Leituras com a bomba ligada | 39,47% |

O campo `bomba` é binário: `1` representa bomba ligada e `0` representa bomba
desligada. O percentual apresentado é uma métrica derivada: indica em quantas
leituras a bomba estava ligada. Como cada leitura representa uma hora, ele pode
ser interpretado como uma aproximação do percentual de horas com irrigação.

## Correlações

O maior resultado observado foi a correlação negativa entre umidade e bomba
(`-0,87`). Isso é coerente com a regra simulada: a bomba tende a ligar quando a
umidade diminui. Também foi observada correlação positiva moderada entre pH e
fósforo (`0,48`) e entre pH e potássio (`0,43`).

Correlação não significa causalidade. Como parte dos dados foi gerada por
regras artificiais, esses valores demonstram o funcionamento da análise e não
representam uma conclusão agronômica.

## Limitações

Os dados são didáticos e combinam registros do simulador com registros
gerados artificialmente. O pH, a umidade e os nutrientes não representam uma
medição agronômica real. Os resultados demonstram o fluxo de coleta,
persistência, tratamento e geração de indicadores.
