from django.shortcuts import render,redirect,get_object_or_404
from .models import Employee,Task,Machine,TaskHistory,Target,ProductionProgress,ProductionManager
from django.contrib import messages
from datetime import datetime
import json
from django.core.paginator import Paginator
import json
import random
from datetime import date, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.


#HomePage
@login_required(login_url='auth_login_minimal')
def index(request):
    Productionmanager = ProductionManager.objects.get(id=1)
    target = Target.objects.filter(manager=Productionmanager).first()
    Productionprogress = ProductionProgress.objects.filter(target=target).first()
    
    print(Productionprogress.containers_completed_count())
    

    context = {"target":target,"Productionprogress":Productionprogress,"long_short_panel":(target.target_sets)*2,
    }
    return render(request,'index.html',context)





    
    
#apps-tasksPage
@login_required(login_url='auth_login_minimal')
def apps_tasks(request,id=None):
    if request.method == "POST":
        employees = Employee.objects.all()

    
        name = request.POST.get("name")
        description = request.POST.get("description")
        start_date = request.POST.get("range-start")
        end_date = request.POST.get("range-end")
        status = request.POST.get("status")
        priority = request.POST.get("priority")
        machine = request.POST.get("machine")
        target = request.POST.get("target")
        completed = request.POST.get("completed")
        assignees = request.POST.get("assignee")
        take_machine = get_object_or_404(Machine,name=machine)
            
            
        # start_date_obj = datetime.strptime(start_date, "%m/%d/%Y").date()
        # end_date_obj = datetime.strptime(end_date, "%m/%d/%Y").date()
        # Convert IDs to Employee objects
        assignee_objs = Employee.objects.get(id=assignees)
        emp_task = Task.objects.filter(assignee=assignee_objs).count()
        print(emp_task)
        if emp_task == 0:
        
            task = Task.objects.create(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                status=status,
                priority=priority,
                machine=take_machine,
                target = target,
                completed = completed,
                assignee = assignee_objs,
                due = target
            )
            print(name,start_date,end_date,status,priority,machine,assignees)
            print(description)
            messages.success(request,f"✅ Today Task Assigned for the Employees {assignee_objs} Successfully!. Ask the Employees to check.")
            return redirect("apps_tasks")
        else:
            messages.error(request,f"✅Oops The Employee {assignee_objs} Tasks already exists.Your cannot create another task.Please modify the existing one.")
            return redirect("apps_tasks")
       
    employees = Employee.objects.all()
    all_tasks = Task.objects.all()
    
    return render(request,'apps-tasks.html',{"employees":employees,"all_tasks":all_tasks})

@login_required(login_url='auth_login_minimal')
def apps_tasks_seen(request,id):
    task = get_object_or_404(Task,id=id)
    
    time_slots = [
        "9:20 - 10:00",
        "10:00 - 11:00",
        "11:15 - 12:00",
        "12:00 - 1:00",
        "1:45 - 3:00",
        "3:00 - 4:00",
        "4:15 - 5:00",
        "5:00 - 6:00",
        "6:00 - 6:50",
    ]

    # Load completed_data from JSON
    try:
        completed_dict = json.loads(task.completed_data)
    except:
        completed_dict = {}

    completed_list = [(slot, completed_dict.get(slot, 0)) for slot in time_slots]
    return render(request,'apps-tasks-seen.html',{"task":task,"completed_list":completed_list})

@login_required(login_url='auth_login_minimal')
def apps_tasks_update(request, id):
    task = get_object_or_404(Task, id=id)
    machines = Machine.objects.all()
    
    if request.method == "POST":
        # Save the current task to TaskHistory BEFORE updating
        TaskHistory.objects.create(
            employee=task.assignee,
            machine=task.machine,
            task_name=task.name,
            target=task.target,
            completed=task.completed,
            due=task.due,
            task_date=task.start_date  # or use timezone.now() if you want actual update date
        )

        # Now update the current task
        employee = Employee.objects.get(name=request.POST.get('assignee'))
        machine = get_object_or_404(Machine, id=request.POST.get('machine'))

        task.name = request.POST.get('name')
        task.description = request.POST.get('description')
        task.start_date = request.POST.get('range-start')
        task.end_date = request.POST.get('range-end')
        task.status = request.POST.get('status')
        task.priority = request.POST.get('priority')
        task.machine = machine
        task.assignee = employee
        task.target = int(request.POST.get('target'))
        task.completed = 0
        task.completed_data = {}
        task.due = task.target
        task.save()

        messages.success(request, f"Task for the Employee {employee} updated successfully.")
        return redirect('apps_tasks')

    return render(request, 'apps-tasks-update.html', {"task": task, 'machines': machines})



def dashboard(request, username):
    if request.session.get("username")!=None:
        employee = get_object_or_404(Employee, username=username)
        task = get_object_or_404(Task, assignee=employee)
        print(request.session.get('username'))
        time_slots = [
            "9:20 - 10:00",
            "10:00 - 11:00",
            "11:15 - 12:00",
            "12:00 - 1:00",
            "1:45 - 3:00",
            "3:00 - 4:00",
            "4:15 - 5:00",
            "5:00 - 6:00",
            "6:00 - 6:50",
        ]

        # ✅ Expected calculation
        slots_count = len(time_slots)
        target = task.target or 0
        base = target // slots_count
        remainder = target % slots_count

        expected_values = [
            base + 1 if i < remainder else base
            for i in range(slots_count)
        ]

        # ✅ Load JSON safely
        if task.completed_data:
            try:
                completed_data = json.loads(task.completed_data)
            except json.JSONDecodeError:
                completed_data = eval(task.completed_data)  # Fix old bad data
        else:
            completed_data = {}

        # ✅ Handle POST
        if request.method == "POST":
            for i, slot in enumerate(time_slots, start=1):
                value = request.POST.get(f"completed_{i}")
                completed_data[slot] = int(value) if value else 0

            # ✅ Calculate AFTER update
            total_completed = sum(completed_data.values())

            # ✅ Save JSON properly
            task.completed_data = json.dumps(completed_data)
            task.completed = total_completed

            # 🎯 Messages
            tasks_completed_words = [
                "Excellent work! Your dedication keeps Neminath Wood Industry growing strong 🌳",
                "Target achieved! Your hard work builds strength 💪",
                "Great job! Task completed on time 👏",
                "Outstanding performance! 🔥",
                "Success comes from effort 👍",
                "Well done! 🚀",
            ]

            tasks_due_words = [
                "Don’t worry — improve tomorrow 💪",
                "Try again, you can do it 👍",
                "Keep pushing forward 🔥",
                "Come back stronger!",
                "Stay focused 🚀",
            ]

            # ✅ Status logic
            last_slot = time_slots[-1]  # "6:00 - 6:50"
            print(last_slot)
            last_slot_value = completed_data.get(last_slot, 0)
            print(type(last_slot_value))
            if total_completed >= task.target:
                task.due = 0
                task.status = "Completed"
                total_completed = sum(completed_data.values())
                task.completed = total_completed
                task.completed_data = {}
                task.save()
                del request.session['username']
                messages.success(
                    request,
                    f"Hello {task.assignee}, target {task.target} completed 🎉 "
                    f"{random.choice(tasks_completed_words)}.We will get back to you soon. if any tasks are avaliable."
                )
                return redirect('employee_login')
            else:
                if last_slot_value!=0:
                    task.due = task.target - total_completed
                    task.status = "Pending"
                    task.save()
                    del request.session['username']
                    messages.error(
                        request,
                        f"Hello {task.assignee}, Thank Your for your response. we appriciate your time and effort. Your Target is {task.target} but you successgfully completed {task.completed}. {random.choice(tasks_due_words)} We will get back to you soon. if any tasks are avaliable."
                    )
                    return redirect('employee_login')

            task.save()

        # ✅ Always recalc for GET + POST
        total_completed = sum(completed_data.values())

        # ✅ Table data
        table_data = [
            {
                "time": slot,
                "expected": expected_values[i],
                "completed": completed_data.get(slot, 0),
            }
            for i, slot in enumerate(time_slots)
        ]

        context = {
            "employee": employee,
            "task": task,
            "table_data": table_data,
            "total_completed": total_completed,
        }

        return render(request, "dashboard.html", context)
    else:
        messages.error(request,'Oops you are not authorized to this Employee.Pls login')
        return redirect('employee_login')



#auth-login-minimalPage

def auth_login_minimal(request):
    if request.user.is_authenticated:
        return redirect('Home')  # Redirect if already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "NeminathProduction" and password == "nwipl_production":

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                print(True)
                messages.success(request, f'Welcome {user.username}!')
                return redirect('Home')  # Change to your dashboard view
            else:
                messages.error(request, "User not found or not active.")
                return redirect('auth_login_minimal')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('auth_login_minimal')

    
    return render(request,'auth-login-minimal.html')

def logout_view(request):
    logout(request)  # Logs out the user
    messages.success(request, "You have been logged out successfully.")
    return redirect('auth_login_minimal')  # Redirect to login page

def employee_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            employee = Employee.objects.get(username=username)
            if employee.password == password:  # plain text check
                # Login successful
                request.session['username'] = employee.username  # store session
                return redirect('dashboard', username=employee.username)
            else:
                messages.error(request, "Invalid password")
        except Employee.DoesNotExist:
            messages.error(request, "Employee not found")

    return render(request, "Employeelogin.html")


#leads-createPage
@login_required(login_url='auth_login_minimal')
def leads_create(request):
    print("View Called")
    if request.method == "POST":
        print(request.POST)
        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']
        designation = request.POST['designation']
        description = request.POST['textarea']
        status = request.POST['status']
        try:
                
            Employee.objects.create(
                name = name,
                email = email,
                username = username,
                password = password,
                phone = phone,
                status = status,
                designation = designation,
                description = description
            )
            messages.success(request,f'Hii Production Manager.Nice to See you. Employee {name} saved successfully.check out!.')
            return redirect('leads')
        except Exception as e:
            messages.warning(request, "Email already exists!")
            return redirect('leads_create')
    return render(request,'leads-create.html')

@login_required(login_url='auth_login_minimal')
def leads_update(request, employee_id):
    # Fetch the employee object or return 404 if not found
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == "POST":
        # Get data from form
        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']
        designation = request.POST['designation']
        description = request.POST['textarea']
        status = request.POST['status']

        try:
            # Update the employee object
            employee.name = name
            employee.email = email
            employee.username = username
            employee.password = password
            employee.phone = phone
            employee.designation = designation
            employee.description = description
            employee.status = status
            employee.save()

            messages.success(request, f'Employee {name} updated successfully!')
            return redirect('leads')  # Redirect to a list or detail view
        except Exception as e:
            messages.warning(request, f'Error updating employee: {str(e)}')
            return redirect('leads_update', employee_id=employee.id)
    
    # GET request → pre-fill form with existing data
    context = {
        'employee': employee
    }
    return render(request, 'leads-update.html', context)

#leads-viewPage
@login_required(login_url='auth_login_minimal')
def leads_view(request,id=None):
    if id:
        employee = Employee.objects.get(id=id)
        print(employee.status)
        

        tasks = TaskHistory.objects.filter(employee=employee).order_by('-created_at')
        
        print(tasks)
        for t in tasks:
            t.stars_str = "⭐" * t.stars  # create the star string
        # Pagination
        paginator = Paginator(tasks, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Overall performance
        total_target = sum(t.target for t in tasks)
        total_completed = sum(t.completed for t in tasks)
        
        overall_percent = (total_completed / total_target * 100) if total_target > 0 else 0
        overall_percent = round(overall_percent, 2)  # e.g., 29.58
        print(overall_percent)

        if overall_percent >= 95:
            overall_stars = 5
        elif overall_percent >= 85:
            overall_stars = 4
        elif overall_percent >= 70:
            overall_stars = 3
        elif overall_percent >= 50:
            overall_stars = 2
        else:
            overall_stars = 1  # ✅ here 29.58 will correctly be 1 star
        
        print(overall_stars*"⭐")
        context = {
            'employee': employee,
            'page_obj': page_obj,
            'overall_percent': overall_percent,
            'overall_stars': overall_stars*"⭐",
            'tasks':tasks
        }
        return render(request,'leads-view.html',{"employee":employee,'context':context})
    else:
        return render(request,'leads-view.html')

@login_required(login_url='auth_login_minimal')
def leads(request):
    import random
    employee = Employee.objects.all()
    Working = Employee.objects.filter(status="Working").count()
    
    New = Employee.objects.filter(status="New").count()
    total = employee.count()


    percentage_working = 0
    percentage_New = 0
    if Working>0:
        percentage_working = (Working/total)*100
    if New>0:
        percentage_New = (New/total)*100

    colors = ["bg-teal","bg-orange","bg-blue","bg-warning","bg-success","bg-primary","bg-secondary","bg-danger","bg-info","bg-dark"]
    image = ["feather-github","feather-facebook"]

    paginator = Paginator(employee, 5)  # 👈 5 rows per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    employee_data = []
    for emp in page_obj:
        employee_data.append({
            'employee': emp,
            'color': random.choice(colors),
            'image': random.choice(image)
        })
    print(employee_data)
    return render(request, 'leads.html', {
        'employee_data': employee_data,
        'page_obj': page_obj,
        'Working':Working,
        'New':New,
        'total':total,
        'percentage_working':percentage_working,
        'percentage_New':percentage_New
    })

@login_required(login_url='auth_login_minimal')
def leads_delete(request,employee_id):
    get = get_object_or_404(Employee,id=employee_id)
    if request.method == "POST":
        get.delete()
        messages.success(request,"Employee Deleted Successfully.")
        return redirect('leads')
    
    return render(request,'leads-delete.html',{'get':get})