-- 全表
SELECT id, name, score, class_id FROM students;

-- 过滤+排序+限制
SELECT name,score FROM students
WHERE score >= 60
ORDER BY score DESC
LIMIT 3;


-- 聚合（按班级统计）
SELECT class_id,COUNT(*) as cnt, ROUND(AVG(score),1) AS avg_score 
FROM students
GROUP BY class_id
ORDER BY avg_score DESC;


-- JOIN(班级名字拼上来)
SELECT s.name,s.score,c.name AS class_name 
FROM students As s
JOIN classes As c ON s.class_id = c.id
ORDER BY s.score DESC;

