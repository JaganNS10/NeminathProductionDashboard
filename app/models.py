from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta


class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    designation = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name





class Machine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Task(models.Model):

    STATUS_CHOICES = [
        ('inprogress', 'Inprogress'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    assignee = models.ForeignKey('Employee', on_delete=models.CASCADE)

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    target = models.BigIntegerField()
    completed = models.BigIntegerField(default=0)
    due = models.BigIntegerField(default=0)
    completed_data = models.TextField(default="{}")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
   



class TaskHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=200)
    target = models.BigIntegerField()
    completed = models.BigIntegerField()
    due = models.BigIntegerField()
    task_date = models.DateField(auto_now_add=True)  # date task was taken
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        if self.target > 0:
            return round((self.completed / self.target) * 100, 2)
        return 0

    @property
    def stars(self):
        p = self.percentage
        if p >= 95: return 5
        elif p >= 85: return 4
        elif p >= 70: return 3
        elif p >= 50: return 2
        return 1
    
class ProductionManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


class Target(models.Model):
    manager = models.ForeignKey(ProductionManager, on_delete=models.CASCADE)
    target_sets = models.IntegerField()
    deadline = models.DateField()

    def long_panel_expected(self):
        return self.target_sets * 2

    def short_panel_expected(self):
        return self.target_sets * 2

    def mattress_expected(self):
        return self.target_sets

    def __str__(self):
        return f"{self.manager} - {self.target_sets} sets"




class ProductionProgress(models.Model):
    target = models.OneToOneField(Target, on_delete=models.CASCADE)
    
    long_panel = models.IntegerField(default=0)
    short_panel = models.IntegerField(default=0)
    mattress = models.IntegerField(default=0)

    @property
    def completed_sets(self):
        return min(
            self.long_panel // 2,
            self.short_panel // 2,
            self.mattress
        )

    # def container_completed(self):
    #     return self.completed_sets >= self.target.target_sets
    def containers_completed_count(self):
        # 1 container = target.target_sets
        if self.target.target_sets == 0:
            return 0
        return self.completed_sets // self.target.target_sets

    def __str__(self):
        return f"Progress - {self.target.manager}"