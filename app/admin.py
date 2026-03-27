from django.contrib import admin
from .models import ProductionManager, Target, ProductionProgress

@admin.register(ProductionManager)
class ProductionManagerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

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
    
    