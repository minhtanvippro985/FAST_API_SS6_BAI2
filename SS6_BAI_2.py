from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Model dùng để validate dữ liệu đầu vào khi thêm và sửa học viên
class StudentCreate(BaseModel):
    code: str = Field(..., min_length=1)  # Mã không được rỗng
    name: str = Field(..., min_length=1)  # Tên không được rỗng
    email: str = Field(..., min_length=1) # Email không được rỗng
    age: int = Field(..., gt=0)           # Tuổi phải lớn hơn 0


# Dữ liệu mẫu ban đầu
students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]


# 1. Lấy danh sách học viên kết hợp TÌM KIẾM và LỌC (Query Params)
@app.get("/students")
def get_students(
    keyword: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
):
    filtered_students = students
    
    # Tìm kiếm theo keyword (name, code, hoặc email)
    if keyword:
        keyword_lower = keyword.lower()
        filtered_students = [
            s for s in filtered_students
            if keyword_lower in s["name"].lower()
            or keyword_lower in s["code"].lower()
            or keyword_lower in s["email"].lower()
        ]
        
    # Lọc theo min_age (tuổi từ mức này trở lên)
    if min_age is not None:
        filtered_students = [s for s in filtered_students if s["age"] >= min_age]
        
    # Lọc theo max_age (tuổi từ mức này trở xuống)
    if max_age is not None:
        filtered_students = [s for s in filtered_students if s["age"] <= max_age]
        
    return filtered_students


# 2. Thêm học viên mới (Kiểm tra trùng code bằng vòng lặp)
@app.post("/students")
def add_student(student_ : StudentCreate):
    # Kiểm tra trùng mã code giống như cách bạn check trùng khóa học
    for student in students:
        if student["code"] == student_.code:
            raise HTTPException(status_code=400, detail="Mã học viên đã tồn tại")
        
    new_student = {
        "id": len(students) + 1,
        "code": student_.code,
        "name": student_.name,
        "email": student_.email,
        "age": student_.age
    }
    students.append(new_student)
    return {
        "message": "Thêm thành công",
        "data": students
    }


# 3. Lấy chi tiết học viên theo ID
@app.get("/students/{student_id}")
def get_student_details(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student
            
    raise HTTPException(status_code=404, detail="Student not found")


# 4. Cập nhật thông tin học viên (Kiểm tra tồn tại và check trùng code)
@app.put("/students/{student_id}")
def update_student(course_id: int, student_data: StudentCreate): # Giữ nguyên cấu trúc đặt tên tham số của bạn
    found = None
    
    # Tìm học viên xem có tồn tại không
    for student in students:
        if student['id'] == course_id:
            found = student
            break
            
    if found is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Kiểm tra trùng code với các học viên khác (trừ chính nó)
    for student_l in students:
        if student_l["code"] == student_data.code and student_l["id"] != course_id:
            raise HTTPException(status_code=400, detail="Mã học viên này đã bị trùng")
            
    # Các điều kiện validate rỗng, âm đã được Pydantic Model lo (đã tắt comment)
    found.update(student_data.model_dump())
    return found


# 5. Xóa học viên theo ID
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for student in students:
        if student_id == student["id"]:
            students.remove(student)
            return students
            
    raise HTTPException(status_code=404, detail="Student not found")
