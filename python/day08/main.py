# 路由


import crud
from fastapi import FastAPI, HTTPException, Response, status
from schemas import StudentCreate, StudentOut

app = FastAPI(title="day08 学生管理API")


@app.get("/students/{id}", response_model=StudentOut)
def get_one_student(id: int):
    student = crud.get_student(id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student


@app.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    try:
        student = crud.create_student(student)
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, body: StudentCreate):
    try:
        row = crud.update_student(
            student_id,
            name=body.name,
            score=body.score,
            class_id=body.class_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not row:
        raise HTTPException(status_code=404, detail="学生不存在")
    return row


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    ok = crud.delete_student(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="学生不存在")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/students", response_model=list[StudentOut])
def list_students(min_score: int = 0):
    return crud.list_students(min_score)
