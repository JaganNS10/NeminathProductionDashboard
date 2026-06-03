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
# #@login_required(login_url='auth_login_minimal')
# def index(request):
#     return render(request,'index.html')

    
#apps-tasksPage
#@login_required(login_url='auth_login_minimal')
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
        take_machine = get_object_or_404(Machine,id=machine)
            
            
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
    all_mech = Machine.objects.all()
    print(all_mech)
    return render(request,'apps-tasks.html',{"employees":employees,"all_tasks":all_tasks,"all_mech":all_mech})

# @login_required(login_url='auth_login_minim0al')
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

#@login_required(login_url='auth_login_minimal')
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
        task.remark = ""
        task.save()

        messages.success(request, f"Task for the Employee {employee} updated successfully.")
        return redirect('apps_tasks')

    return render(request, 'apps-tasks-update.html', {"task": task, 'machines': machines})


def dashboard(request, username):
    print(request.session.get("username"))
    if request.session.get("username")!=None:
        print(True)
        employee = get_object_or_404(Employee, username=username)
        print(True)
        task = Task.objects.filter(assignee=employee)
        print(task)
        if task:
            print(True)
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
                task.due = abs(task.target-task.completed)

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
                remark = request.POST.get("remark")
                print("Remark:",remark)
                if remark != "":
                    task.status = "Completed"
                    total_completed = sum(completed_data.values())
                    task.completed = total_completed
                    task.remark = remark
                    task.due = abs(task.target - total_completed)
                    task.save()
                    del request.session['username']
                    messages.success(
                    request,
                            f"Hello {task.assignee}, Please wait for another task when the manager is assigned"
                    )
                    return redirect('employee_login')
                
                if total_completed >= task.target:
                        task.status = "Completed"
                        total_completed = sum(completed_data.values())
                        task.completed = total_completed
                        task.due = 0
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
                        task.due = abs(task.target - total_completed)
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
            context = {"task_status":"Completed"}
            return render(request,"dashboard.html",context)
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
# #@login_required(login_url='auth_login_minimal')
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

#@login_required(login_url='auth_login_minimal')
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
#@login_required(login_url='auth_login_minimal')
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

#@login_required(login_url='auth_login_minimal')
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

#@login_required(login_url='auth_login_minimal')
def leads_delete(request,employee_id):
    get = get_object_or_404(Employee,id=employee_id)
    if request.method == "POST":
        get.delete()
        messages.success(request,"Employee Deleted Successfully.")
        return redirect('leads')
    
    return render(request,'leads-delete.html',{'get':get})


def leaderboard_view(request):

    def get_performers(designation):
        employees = Employee.objects.filter(designation=designation)
        data = []

        for emp in employees:
            tasks = TaskHistory.objects.filter(employee=emp)

            total_target = sum(t.target for t in tasks)
            total_completed = sum(t.completed for t in tasks)

            percent = (total_completed / total_target * 100) if total_target > 0 else 0

            data.append({
                'employee': emp,
                'percent': round(percent, 2)
            })

        # sort highest first
        data.sort(key=lambda x: x['percent'], reverse=True)

        return data

    context = {
        'machine_operators': get_performers('Machine Operator'),
        'helpers': get_performers('Helper'),
    }

    return render(request, 'leaderboard.html', context)



from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import DailyEntry,ProcessStep,ProcessTable,AssemblyPanel,AfterAssemblyEntry,Sheet, ProcessTable



def base(request):
    return render(request,'base.html')




def production_update(request):
    """
    Summary of all After Assembly data (totals).
    Fully dynamic based on panels & columns from admin.
    """
    panels = AssemblyPanel.objects.filter(is_active=True).prefetch_related('columns')

    summary = []

    for panel in panels:
        columns_summary = []

        for column in panel.columns.filter(is_active=True):
            total = AfterAssemblyEntry.objects.filter(
                column=column
            ).aggregate(total=Sum('quantity'))['total'] or 0

            columns_summary.append({
                'column_name': column.column_name,
                'total': total,
            })

        summary.append({
            'panel_name': panel.name,
            'columns': columns_summary,
            'grand_total': sum(c['total'] for c in columns_summary),
        })

    return render(request, 'production_update.html', {
        'summary': summary
    })




# -------------------------------------------------------
# AFTER ASSEMBLY DATA SHEET — entry form for manager
# -------------------------------------------------------

# #@login_required(login_url='auth_login_minimal')
def after_assembly(request):
    today = date.today()
    selected_date_str = request.GET.get('date', str(today))

    try:
        from datetime import datetime
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    # Get all active panels with their columns — fully dynamic
    panels = AssemblyPanel.objects.filter(is_active=True).prefetch_related('columns')

    # Load existing entries for selected date
    panel_data = []
    for panel in panels:
        columns_data = []
        for column in panel.columns.filter(is_active=True):
            try:
                entry = AfterAssemblyEntry.objects.get(column=column, date=selected_date)
                quantity = entry.quantity
                remarks = entry.remarks
            except AfterAssemblyEntry.DoesNotExist:
                quantity = 0
                remarks = ''
            columns_data.append({
                'column': column,
                'quantity': quantity,
                'remarks': remarks,
            })
        panel_data.append({
            'panel': panel,
            'columns': columns_data,
        })

    if request.method == 'POST':
        selected_date_str = request.POST.get('date')
        try:
            from datetime import datetime
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today

        for panel in panels:
            for column in panel.columns.filter(is_active=True):
                qty = request.POST.get(f'column_{column.id}', 0)
                qty = int(qty) if qty else 0
                AfterAssemblyEntry.objects.update_or_create(
                    column=column,
                    date=selected_date,
                    defaults={'quantity': qty}
                )

        messages.success(request, f'After Assembly data saved for {selected_date}.')
        return redirect(f'/after-assembly/?date={selected_date}')

    context = {
        'panel_data': panel_data,
        'selected_date': selected_date,
    }
    return render(request, 'after_assembly.html', context)

def process_sheet(request, slug):
    today = date.today()
    selected_date_str = request.GET.get('date', str(today))

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    # Get sheet
    sheet = get_object_or_404(Sheet, slug=slug)

    # ✅ FIXED HERE
    tables = ProcessTable.objects.filter(
        sheet=sheet,
        is_active=True
    ).prefetch_related('steps')

    # Load existing entries
    table_data = []
    for table in tables:
        steps_data = []
        for step in table.steps.filter(is_active=True):
            entry = DailyEntry.objects.filter(step=step, date=selected_date).first()
            quantity = entry.quantity if entry else 0

            steps_data.append({
                'step': step,
                'quantity': quantity
            })

        table_data.append({
            'table': table,
            'steps': steps_data
        })

    # Save
    if request.method == 'POST':
        selected_date_str = request.POST.get('date')
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today

        for table in tables:
            for step in table.steps.filter(is_active=True):
                qty = request.POST.get(f'step_{step.id}', 0)
                qty = int(qty) if qty else 0

                DailyEntry.objects.update_or_create(
                    step=step,
                    date=selected_date,
                    defaults={'quantity': qty}
                )

        messages.success(request, f'{sheet.display_name} data saved for {selected_date}.')
        return redirect(f'/sheet/{sheet.slug}/?date={selected_date}')

    return render(request, 'process_sheet.html', {
        'table_data': table_data,
        'selected_date': selected_date,
        'sheet_title': sheet.display_name,
        'sheet': sheet
    })
# WORK DONE TODAY — summary of all entries for today



def work_done_today(request):
    today = date.today()
    selected_date_str = request.GET.get('date', str(today))

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    # 🔥 ALL SHEETS
    tables = ProcessTable.objects.filter(is_active=True).select_related('sheet').prefetch_related('steps')

    process_summary = []

    for table in tables:
        steps_today = []

        for step in table.steps.filter(is_active=True):
            entry = step.entries.filter(date=selected_date).first()

            if entry and entry.quantity > 0:
                steps_today.append({
                    'step_name': step.step_name,
                    'machine_name': step.machine_name,
                    'quantity': entry.quantity,
                })

        if steps_today:
            process_summary.append({
                'table_name': table.name,
                'sheet': table.sheet.display_name,
                'steps': steps_today,
                'total': sum(s['quantity'] for s in steps_today),
            })

    # 🔥 ASSEMBLY
    panels = AssemblyPanel.objects.filter(is_active=True).prefetch_related('columns')

    assembly_summary = []

    for panel in panels:
        columns_today = []

        for column in panel.columns.filter(is_active=True):
            entry = column.entries.filter(date=selected_date).first()

            if entry and entry.quantity > 0:
                columns_today.append({
                    'column_name': column.column_name,
                    'quantity': entry.quantity,
                    'remarks': entry.remarks,
                })

        if columns_today:
            assembly_summary.append({
                'panel': panel.name,
                'columns': columns_today,
                'total': sum(c['quantity'] for c in columns_today),
            })

    return render(request, 'work_done_today.html', {
        'selected_date': selected_date,
        'today': today,
        'process_summary': process_summary,
        'assembly_summary': assembly_summary,
        'has_data': bool(process_summary or assembly_summary),
    })