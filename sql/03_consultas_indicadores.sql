SET PAGESIZE 50
SET LINESIZE 140

PROMPT === RESUMO DAS LEITURAS ===
SELECT
    COUNT(*) AS total_leituras,
    TO_CHAR(MIN(data_hora), 'YYYY-MM-DD HH24:MI:SS') AS primeira_leitura,
    TO_CHAR(MAX(data_hora), 'YYYY-MM-DD HH24:MI:SS') AS ultima_leitura
FROM leituras_sensor;

PROMPT === MEDIAS DOS SENSORES ===
SELECT
    ROUND(AVG(umidade), 2) AS umidade_media,
    ROUND(AVG(ph), 2) AS ph_medio,
    ROUND(AVG(CASE WHEN fosforo = 1 THEN 1 ELSE 0 END) * 100, 2)
        AS percentual_fosforo_adequado,
    ROUND(AVG(CASE WHEN potassio = 1 THEN 1 ELSE 0 END) * 100, 2)
        AS percentual_potassio_adequado
FROM leituras_sensor;

PROMPT === IRRIGACAO ===
SELECT
    SUM(CASE WHEN bomba = 1 THEN 1 ELSE 0 END) AS leituras_com_bomba_ligada,
    ROUND(AVG(CASE WHEN bomba = 1 THEN 1 ELSE 0 END) * 100, 2)
        AS percentual_leituras_bomba_ligada
FROM leituras_sensor;

PROMPT === ULTIMAS 10 LEITURAS ===
SELECT
    TO_CHAR(data_hora, 'YYYY-MM-DD HH24:MI:SS') AS data_hora,
    umidade,
    ph,
    fosforo,
    potassio,
    bomba,
    origem
FROM leituras_sensor
ORDER BY data_hora DESC
FETCH FIRST 10 ROWS ONLY;

EXIT;
