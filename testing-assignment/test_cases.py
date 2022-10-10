import pytest
import System
import json

valid_user = "akend3"
valid_pass = "123454321"

professor_login = "goggins"
professor_pass = "augurrox"


add_user_name = "testAddUser" #will be used for add_user test function

@pytest.fixture
def grading_system():
    gradingSystem = System.System()
    gradingSystem.load_data()
    return gradingSystem

@pytest.fixture
def professor_user(grading_system):
    grading_system.login(professor_login, professor_pass)
    return grading_system.usr

@pytest.fixture
def student_user(grading_system):
    grading_system.login(valid_user, valid_pass)
    return grading_system.usr

def test_login(grading_system):
    grading_system.login(valid_user, valid_pass)

    if grading_system.usr.name != valid_user:
        assert False

    with open("Data/users.json") as f:
        users = json.load(f)
        if users != grading_system.usr.users:
            assert False
        
    with open("Data/courses.json") as f:
        courses = json.load(f)
        if courses != grading_system.usr.all_courses:
            assert False
    
    

def test_check_password(grading_system):
    check1 = grading_system.check_password("hdjsr7", "pass1234")
    check2 = grading_system.check_password("hdjsr7", "pass1234")
    check3 = grading_system.check_password("hdjsr7", "PASS1234")

    if check1 != check2 or check1 == check3 or check2 == check3:
        assert False

def test_change_grade(professor_user):
    professor_user.change_grade("akend3", "databases", "assignment1", 3)

    with open("Data/users.json") as f:
        users = json.load(f)
        if users["akend3"]["courses"]["databases"]["assignment1"]["grade"] != 3:
            assert False

def test_create_assignment(professor_user):
    professor_user.create_assignment("assignment3", "2/6/20", "databases")

    with open("Data/courses.json") as f:
        courses = json.load(f)
        if "assignment3" not in courses["databases"]["assignments"]:
            assert False
        if courses["databases"]["assignments"]["assignment3"]["due_date"] != "2/6/20":
            assert False

def test_add_student(professor_user):
    professor_user.add_student(add_user_name, 'databases')

    with open("Data/users.json") as f:
        users = json.load(f)

        if add_user_name not in users:
            assert False
        
        if 'databases' not in users[add_user_name]['courses']:
            assert False

def test_drop_student(professor_user):
    lenPreDrop: int
    lenPostDrop: int

    #remembering how many courses this student was enrolled in before runing any functions
    with open("Data/users.json") as f:
        users = json.load(f)
        lenPreDrop = len(users['yted91']['courses'])

    
    professor_user.add_student("yted91", 'comp_sci')

    professor_user.drop_student("yted91", 'comp_sci')


    with open("Data/users.json") as f:
        users = json.load(f)

        #test fails if the number of courses this student is enrolled in now is not equal to what it was in the beginning
        #either add_student or drop_student fail to update the course list
        lenPostDrop = len(users['yted91']['courses']) 
        if lenPreDrop != lenPostDrop:
            assert False

        if 'comp_sci' in users["yted91"]['courses']:
            assert False

def test_submit_assignment(student_user):
    student_user.submit_assignment('databases', 'assignment1', 'assignment sunbmission test', '10/10/22')

    with open("Data/users.json") as f:
        users = json.load(f)
        
        if 'assignment1' not in users[valid_user]['courses']['databases']:
            assert False 
        
        if users[valid_user]['courses']['databases']['assignment1']['submission_date'] != "10/10/22":
            assert False
        
        if users[valid_user]['courses']['databases']['assignment1']['submission'] != "assignment sunbmission test":
            assert False

def test_check_ontime(student_user):  
    checkVal = student_user.check_ontime("01/01/23", "10/10/22") #submission date > due date – supposed to be false
    
    if checkVal:
        assert False

def test_check_grades(student_user):
    testGrades = student_user.check_grades('comp_sci')

    with open("Data/users.json") as f:
        users = json.load(f)
        count = 0
        for key in users[valid_user]['courses']['comp_sci']:
            if testGrades[count][1] != users[valid_user]['courses']['comp_sci'][key]['grade']:
                assert False
            else: count += 1

def test_view_assignments(student_user):
    testRes = student_user.view_assignments('cloud_computing')

    with open("Data/courses.json") as f:
        courses = json.load(f)
        
        count = 0
        for key in courses['cloud_computing']['assignments']:
            if testRes[count][0] != key:
                assert False
            if testRes[count][1] != courses['cloud_computing']['assignments'][key]['due_date']:
                assert False
            count += 1

#making sure that an assignment is created by a staff member who is listed as a teacher/ta for this course
def test_create_assignment_permission(professor_user):

    #professor_user that we use here is not listed as a teacher for this course, therefore the assignment shouldn't be added
    professor_user.create_assignment("assignment3", "2/6/20", "comp_sci")

    with open("Data/courses.json") as f:
        courses = json.load(f)
        if "assignment3" in courses["comp_sci"]["assignments"]:
            assert False

#making sure that a student is added by a staff member who is listed as a teacher for this course
def test_add_student_permission(professor_user):

    #professor_user that we use here is not listed as a teacher for this course, therefore the student shouldn't be added
    professor_user.add_student('yted91', 'comp_sci')

    with open("Data/users.json") as f:
        users = json.load(f)
        if "comp_sci" in users['yted91']["courses"]:
            assert False

#same deal as test_add_student_permission but for drop_student
def test_drop_student_permission(professor_user):

    studentToRemove = ""
    courseToRemoveFrom = "comp_sci" #professor user is not assigned as a teacher for this course so we'll use it for the purposes of this test

    with open("Data/users.json") as f:
        users = json.load(f)
        for student in users:
            if "comp_sci" in users[student]["courses"]:
                studentToRemove = student
                break

    professor_user.drop_student(studentToRemove, courseToRemoveFrom)

    #the test fails if the student was dropped from the course
    #because the professor user used in this test case doesn't have the permission to drop students
    #for this course
    with open("Data/users.json") as f:
        users = json.load(f)
        if "comp_sci" not in users[student]['courses']:
            assert False

def test_change_grade_permission(professor_user):
    preChangeValue = professor_user.users["akend3"]["courses"]["comp_sci"]["assignment1"]["grade"]
    #user goggins is not listed as a teacher for this course, therefore shouldn't be able to change the grade
    professor_user.change_grade('akend3', "comp_sci", "assignment1", 0)
    
    #we know that current behavior of change_grade always sets the grade to 0
    #but that's enough to show that the staff member was able to update the value
    if professor_user.users["akend3"]["courses"]["comp_sci"]["assignment1"]["grade"] != preChangeValue:
        assert False

def test_password_safety(grading_system):
    user = "akend3"
    password = "123454321"
    grading_system.login(user, password)
    if grading_system.usr.name == "akend3": #login was successful and we are now good to check the safety level of the password the they used to register
        if password.isnumeric():
            assert False #needs to have at least some letters
        if not any(char.isdigit() for char in password):
            assert False #needs to have at least some numbers
        if not any((char == char.toUpperCase() and not char == char.toLowerCase()) for char in password):
            assert False #needs to have at least one upper case letter