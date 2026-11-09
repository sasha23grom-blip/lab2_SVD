import sys
from bson.objectid import ObjectId
from pymongo import ASCENDING, MongoClient

client = MongoClient("localhost", 27017)
db = client["dean_office_db"]

students_col = db["students"]
debts_col = db["academic_debts"]

def setup_indexes():
  students_col.create_index([("student_ticket", ASCENDING)], unique=True)
  debts_col.create_index([("student_id", ASCENDING)])
  print(" Індекси створено.")


def add_initial_data():
  s1 = students_col.insert_one({
      "student_ticket": "kv-001",
      "full_name": "Хвостик Алекс Вовович",
      "group": "CH-32",
      "study_plan": [
          {"subject": "Бази даних", "semester": 4, "credits": 4.5},
          {"subject": "Операційні системи", "semester": 4, "credits": 3.0},
      ],
  })

  s2 = students_col.insert_one({
      "student_ticket": "kv-002",
      "full_name": "Громляк Алекс Васильков",
      "group": "CH-31",
      "study_plan": [
          {"subject": "Бази даних", "semester": 4, "credits": 4.5},
          {"subject": "Комп'ютерні мережі", "semester": 4, "credits": 4.0},
      ],
  })

  debts_col.insert_many([
      {
          "student_id": s1.inserted_id,
          "subject": "Вища математика",
          "debt_type": "Іспит",
          "status": "Не складено",
      },
      {
          "student_id": s1.inserted_id,
          "subject": "Фізика",
          "debt_type": "Залік",
          "status": "Не складено",
      },
      {
          "student_id": s2.inserted_id,
          "subject": "Алгоритми",
          "debt_type": "Курсова робота",
          "status": "Не складено",
      },
      {
          "student_id": s2.inserted_id,
          "subject": "Дискретна математика",
          "debt_type": "Іспит",
          "status": "Не складено",
      },
  ])
  print(" Початкові дані додано.")


def update_debts():
  result = debts_col.update_many(
      {"status": "Не складено"},
      {"$set": {"status": "Направлено на комісію"}},
  )
  print(f" Оновлено статусів: {result.modified_count}")

def cascade_delete_student():
  ticket = input("Введіть номер студентського для видалення (kv-0024): ").strip()
  student = students_col.find_one({"student_ticket": ticket})

  if not student:
    print(" Студента не знайдено.")
    return

  student_id = student["_id"]
  del_debts = debts_col.delete_many({"student_id": student_id})
  students_col.delete_one({"_id": student_id})
  print(
      f" Студента видалено. Каскадно видалено заборгованостей:"
      f" {del_debts.deleted_count}"
  )

def show_all_sorted():
  print("\n    Студенти ")
  for s in students_col.find().sort("student_ticket", ASCENDING):
    print(
        f"Квиток: {s.get('student_ticket')} | ПІБ: {s.get('full_name')} | План:"
        f" {s.get('study_plan')}"
    )

  print("\n    Заборгованості ")
  for d in debts_col.find().sort("student_id", ASCENDING):
    print(
        f"Student_ID: {d.get('student_id')} | Предмет: {d.get('subject')} |"
        f" Статус: {d.get('status')}"
    )

def menu():
  setup_indexes()
  while True:
    print("\n ")
    print("1. Додати початкові дані")
    print("2. Оновити статуси боргів")
    print("3. Каскадно видалити студента")
    print("4. Показати всі колекції (сортування за індексами)")
    print("0. Вихід")

    choice = input("Оберіть дію: ").strip()
    if choice == "1":
      add_initial_data()
    elif choice == "2":
      update_debts()
    elif choice == "3":
      cascade_delete_student()
    elif choice == "4":
      show_all_sorted()
    elif choice == "0":
      break

if __name__ == "__main__":
  menu()