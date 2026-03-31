from django.contrib import admin
from .models import ProductionManager, Target, ProductionProgress,Task,TaskHistory,Machine,Employee





# Change admin site header, title, and index title
admin.site.site_header = "NeminathProduction Admin Panel"        # Top-left header
admin.site.site_title = "Production Admin Portal"        # Browser tab title
admin.site.index_title = "Welcome to NeminathProduction Admin Dashboard"  # Dashboard main page



@admin.register(ProductionManager)
class ProductionManagerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone','email']

class ProductionProgressInline(admin.StackedInline):
    model = ProductionProgress
    extra = 0
    readonly_fields = ['completed_sets']


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = [
        'manager',
        'target_sets',
        'completed_sets_display',
        'deadline',
        'long_panel_input',
        'short_panel_input',
        'mattress_input',
        'container_status',
    ]

    inlines = [ProductionProgressInline]

    def long_panel_input(self, obj):
        return getattr(obj.productionprogress, 'long_panel', 0)

    def short_panel_input(self, obj):
        return getattr(obj.productionprogress, 'short_panel', 0)

    def mattress_input(self, obj):
        return getattr(obj.productionprogress, 'mattress', 0)

    def completed_sets_display(self, obj):
        if hasattr(obj, 'productionprogress'):
            return obj.productionprogress.completed_sets
        return 0

    completed_sets_display.short_description = "Completed Sets"

    completed_sets_display.short_description = "Completed Sets"

    # def container_status(self, obj):
    #     if hasattr(obj, 'productionprogress'):
    #         count = obj.productionprogress.containers_completed_count()
    #         if count > 0:
    #             return f"✅ Completed ({count} Container{'s' if count > 1 else ''})"
    #     return "⏳ In Progress"

    def container_status(self, obj):
        if hasattr(obj, 'productionprogress'):
            pp = obj.productionprogress
            full_containers = pp.completed_sets // pp.target.target_sets
            remaining_sets = pp.completed_sets % pp.target.target_sets
            status = ""
            if full_containers > 0:
                status += f"✅ Completed ({full_containers} Container{'s' if full_containers>1 else ''})"
            if remaining_sets > 0:
                status += f" + {remaining_sets} sets"
            if not status:
                status = "⏳ In Progress"
            return status
    



class EmployeeAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('name', 'phone', 'email', 'designation', 'status', 'created')

class TaskAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('name','assignee','machine','target','completed','due','remark')
    def save_model(self, request, obj, form, change):
        # Save the Task first
        super().save_model(request, obj, form, change)

        # Check if status changed to 'completed'
        if change and 'status' in form.changed_data and obj.status == 'Completed':
            TaskHistory.objects.create(
                employee=obj.assignee,
                machine=obj.machine,
                task_name=obj.name,
                target=obj.target,
                completed=obj.completed,
                due=obj.due,
                task_date=obj.start_date
            )

class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee','machine','task_name','target','completed','due','task_date')



class ProductionProgressAdmin(admin.ModelAdmin):
    list_display = ('target', 'long_panel', 'long_panel_balance',
                    'short_panel', 'short_panel_balance',
                    'mattress', 'mattress_balance',
                    'completed_sets', 'containers_completed_count')



# Register the model with the custom admin
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Machine)
admin.site.register(Task,TaskAdmin)
admin.site.register(TaskHistory,TaskHistoryAdmin)
admin.site.register(ProductionProgress,ProductionProgressAdmin)
