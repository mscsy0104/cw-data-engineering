SELECT 
    table_catalog AS project_id,
    table_schema  AS dataset_id,
    table_name,
    creation_time
FROM 
    `{project}.{ods}.INFORMATION_SCHEMA.TABLES` -- 프로젝트ID와 데이터셋명 수정
WHERE 
    table_name LIKE '%_cdc'
ORDER BY 
    table_name ASC;