SELECT 
project,
current_analysis_key,
MAX(update_date) as update_date,

SUM(CASE WHEN type = 'CODE_SMELL' AND severity = 'BLOCKER' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_code_smell_blocker,
SUM(CASE WHEN type = 'CODE_SMELL' AND severity = 'CRITICAL' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_code_smell_critical,
SUM(CASE WHEN type = 'CODE_SMELL' AND severity = 'MAJOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_code_smell_major,
SUM(CASE WHEN type = 'CODE_SMELL' AND severity = 'MINOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_code_smell_minor,
SUM(CASE WHEN type = 'CODE_SMELL' AND severity = 'INFO' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_code_smell_info,
SUM(CASE WHEN type = 'CODE_SMELL' AND severity IS NULL AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_code_smell_null_severity,

SUM(CASE WHEN type = 'BUG' AND severity = 'BLOCKER' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_bug_blocker,
SUM(CASE WHEN type = 'BUG' AND severity = 'CRITICAL' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_bug_critical,
SUM(CASE WHEN type = 'BUG' AND severity = 'MAJOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_bug_major,
SUM(CASE WHEN type = 'BUG' AND severity = 'MINOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_bug_minor,
SUM(CASE WHEN type = 'BUG' AND severity = 'INFO' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_bug_info,
SUM(CASE WHEN type = 'BUG' AND severity IS NULL AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_bug_null_severity,

SUM(CASE WHEN type = 'VULNERABILITY' AND severity = 'BLOCKER' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_vulnerability_blocker,
SUM(CASE WHEN type = 'VULNERABILITY' AND severity = 'CRITICAL' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_vulnerability_critical,
SUM(CASE WHEN type = 'VULNERABILITY' AND severity = 'MAJOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_vulnerability_major,
SUM(CASE WHEN type = 'VULNERABILITY' AND severity = 'MINOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_vulnerability_minor,
SUM(CASE WHEN type = 'VULNERABILITY' AND severity = 'INFO' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_vulnerability_info,
SUM(CASE WHEN type = 'VULNERABILITY' AND severity IS NULL AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_vulnerability_null_severity,

SUM(CASE WHEN type = 'SECURITY_HOTSPOT' AND severity = 'BLOCKER' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_security_hotspot_blocker,
SUM(CASE WHEN type = 'SECURITY_HOTSPOT' AND severity = 'CRITICAL' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_security_hotspot_critical,
SUM(CASE WHEN type = 'SECURITY_HOTSPOT' AND severity = 'MAJOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_security_hotspot_major,
SUM(CASE WHEN type = 'SECURITY_HOTSPOT' AND severity = 'MINOR' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_security_hotspot_minor,
SUM(CASE WHEN type = 'SECURITY_HOTSPOT' AND severity = 'INFO' AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_security_hotspot_info,
SUM(CASE WHEN type = 'SECURITY_HOTSPOT' AND severity IS NULL AND status IN ('RESOLVED', 'CLOSED', 'REVIEWED') THEN 1 ELSE 0 END) AS removed_security_hotspot_null_severity

from sonar_issues GROUP BY project, current_analysis_key
) t;