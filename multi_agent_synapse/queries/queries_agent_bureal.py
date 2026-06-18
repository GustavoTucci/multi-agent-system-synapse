import pandas as pd
import pandas_gbq


QUERY_CREDITOS_ATIVOS = """
    SELECT
        app.SK_ID_CURR,
        b.SK_ID_BUREAU,
        b.CREDIT_ACTIVE,
        b.CREDIT_TYPE,
        IFNULL(b.AMT_CREDIT_SUM, 0.0)       AS valor_credito,
        IFNULL(b.AMT_CREDIT_SUM_DEBT, 0.0)  AS valor_divida,
        IFNULL(b.AMT_CREDIT_SUM_LIMIT, 0.0) AS limite_credito,
        b.DAYS_CREDIT,
        b.DAYS_CREDIT_ENDDATE,
        bb.STATUS                            AS status_mensal
    FROM `prj-data-ps-us.home_credit_default_risk.application_train` app
    LEFT JOIN `prj-data-ps-us.home_credit_default_risk.bureau` b
        ON app.SK_ID_CURR = b.SK_ID_CURR
    LEFT JOIN `prj-data-ps-us.home_credit_default_risk.bureau_balance` bb
        ON b.SK_ID_BUREAU = bb.SK_ID_BUREAU
    WHERE app.SK_ID_CURR = {sk_id_curr}
      AND b.CREDIT_ACTIVE = 'Active'
    ORDER BY b.DAYS_CREDIT DESC
"""


QUERY_DEBT_SUMMARY = """
    SELECT
        b.CREDIT_TYPE                           AS tipo_credito,
        COUNT(b.SK_ID_BUREAU)                   AS quantidade_creditos,
        ROUND(SUM(IFNULL(b.AMT_CREDIT_SUM, 0)), 2)      AS total_valor_credito,
        ROUND(SUM(IFNULL(b.AMT_CREDIT_SUM_DEBT, 0)), 2) AS total_divida,
        ROUND(SUM(IFNULL(b.AMT_CREDIT_SUM_LIMIT, 0)), 2) AS total_limite,
        COUNTIF(b.CREDIT_ACTIVE = 'Active')     AS creditos_ativos,
        COUNTIF(b.CREDIT_ACTIVE = 'Closed')     AS creditos_fechados
    FROM `prj-data-ps-us.home_credit_default_risk.application_train` app
    LEFT JOIN `prj-data-ps-us.home_credit_default_risk.bureau` b
        ON app.SK_ID_CURR = b.SK_ID_CURR
    WHERE app.SK_ID_CURR = {sk_id_curr}
      AND b.CREDIT_TYPE IS NOT NULL
    GROUP BY b.CREDIT_TYPE
    ORDER BY total_divida DESC
"""

QUERY_STATUS_TREND = """
WITH historico AS (

    SELECT
        app.SK_ID_CURR,
        bb.MONTHS_BALANCE,

        CASE bb.STATUS
            WHEN 'X' THEN NULL
            WHEN 'C' THEN 0
            WHEN '0' THEN 0
            WHEN '1' THEN 1
            WHEN '2' THEN 2
            WHEN '3' THEN 3
            WHEN '4' THEN 4
            WHEN '5' THEN 5
        END AS score_status

    FROM `prj-data-ps-us.home_credit_default_risk.application_train` app

    LEFT JOIN `prj-data-ps-us.home_credit_default_risk.bureau` b
        ON app.SK_ID_CURR = b.SK_ID_CURR

    LEFT JOIN `prj-data-ps-us.home_credit_default_risk.bureau_balance` bb
        ON b.SK_ID_BUREAU = bb.SK_ID_BUREAU

    WHERE app.SK_ID_CURR = {sk_id_curr}

)

SELECT
    AVG(
        CASE
            WHEN MONTHS_BALANCE >= -6
            THEN score_status
        END
    ) AS media_recente,

    AVG(
        CASE
            WHEN MONTHS_BALANCE < -6
            THEN score_status
        END
    ) AS media_antiga
FROM historico
"""
