from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta

from django.db import models
from django.utils import timezone


class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True,null=True)
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
        ('New', 'New'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
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
    remark = models.TextField(blank=True, null=True)
    due = models.BigIntegerField(default=0)
    completed_data = models.TextField(default="{}")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if it's a new object

        if not is_new:
            # Fetch old record from DB
            old_task = Task.objects.get(pk=self.pk)

            # Check if status changed or relevant fields updated
            if self.status in ['pending', 'completed']:
                # Update due
                self.due = self.target - self.completed

                # Create history entry
                TaskHistory.objects.create(
                    employee=self.assignee,
                    machine=self.machine,
                    task_name=self.name,
                    target=self.target,
                    completed=self.completed,
                    due=self.due
                )

        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class TaskHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE,null=True)
    task_name = models.CharField(max_length=200)
    target = models.BigIntegerField()
    completed = models.BigIntegerField()
    due = models.BigIntegerField()
    task_date = models.DateField(auto_now_add=True)  # date task was taken
    created_at = models.DateTimeField(auto_now_add=True)
    other_work = models.TextField(null=True,help_text="Enter the other works what employee done.please mention all the other works done by the employee.")

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

    @property
    def long_panel_balance(self):
        return self.target.long_panel_expected() - self.long_panel

    @property
    def short_panel_balance(self):
        return self.target.short_panel_expected() - self.short_panel

    @property
    def mattress_balance(self):
        return self.target.mattress_expected() - self.mattress

    def containers_completed_count(self):
        # 1 container = target.target_sets
        if self.target.target_sets == 0:
            return 0
        return self.completed_sets // self.target.target_sets

    def __str__(self):
        return f"Progress - {self.target.manager}"
    





# -------------------------------------------------------
# SHEET TYPE — which sheet does this table belong to?
# -------------------------------------------------------
class Sheet(models.Model):
    name = models.CharField(max_length=100)   # e.g. LSM, Strip
    display_name = models.CharField(max_length=200)  # e.g. "L, S, M Sheet"
    slug = models.SlugField(unique=True)  # e.g. lsm-sheet
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.display_name
    




# -------------------------------------------------------
# ProcessTable — e.g. "Long Pcs 25MM Board"
# Admin can add new tables from Django admin anytime.
# -------------------------------------------------------
class ProcessTable(models.Model):
    name = models.CharField(max_length=200)  # e.g. "Long Pcs 25MM Board"
    board_spec = models.CharField(max_length=100, blank=True, null=True)  # e.g. "25MM Board"
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, related_name='tables')
    order = models.PositiveIntegerField(default=0)  # display order
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    # def __str__(self):
    #     return f"{self.name} ({self.get_sheet_display()})"


# -------------------------------------------------------
# ProcessStep — each column inside a ProcessTable
# e.g. "Cutting - Panel Saw", "Sanding - White Belt"
# Admin can add new steps from Django admin anytime.
# -------------------------------------------------------
class ProcessStep(models.Model):
    table = models.ForeignKey(ProcessTable, on_delete=models.CASCADE, related_name='steps')
    step_name = models.CharField(max_length=200)    # e.g. "Cutting"
    machine_name = models.CharField(max_length=200) # e.g. "Panel Saw"
    order = models.PositiveIntegerField(default=0)  # column order
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.table.name} → {self.step_name} ({self.machine_name})"


# -------------------------------------------------------
# DailyEntry — the number entered by production manager
# One record per (step, date)
# -------------------------------------------------------
class DailyEntry(models.Model):
    step = models.ForeignKey(ProcessStep, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    quantity = models.IntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('step', 'date')  # one entry per step per day
        ordering = ['-date']

    def __str__(self):
        return f"{self.step} | {self.date} | {self.quantity}"


# -------------------------------------------------------
# AfterAssemblyEntry — for the After Assembly Data sheet
# Tracks Mattress / Long / Short panel daily progress
# -------------------------------------------------------

# Replace AfterAssemblyEntry with these two models

class AssemblyPanel(models.Model):
    """Admin can add new panels anytime — Mattress, Long, Short, After 1st Coat, etc."""
    name = models.CharField(max_length=200)        # e.g. "After 1st Coat Painting"
    order = models.PositiveIntegerField(default=0) # display order
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class AssemblyColumn(models.Model):
    """Each column inside a panel table — also dynamic!"""
    panel = models.ForeignKey(AssemblyPanel, on_delete=models.CASCADE, related_name='columns')
    column_name = models.CharField(max_length=200)  # e.g. "Brushing / Sanding"
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.panel.name} → {self.column_name}"


class AfterAssemblyEntry(models.Model):
    """One value per (panel column, date)"""
    column = models.ForeignKey(AssemblyColumn, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    quantity = models.IntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('column', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.column} | {self.date} | {self.quantity}"


