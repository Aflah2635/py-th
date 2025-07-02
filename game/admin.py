from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Question, PlayerProgress, Hint, SubmissionHistory, QuestionProgress, HintUsage
from .activity_log import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'display_meta_info', 'time_taken')
    list_filter = ('activity_type', 'timestamp', 'user')
    search_fields = ('user__username', 'activity_type', 'meta_info')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'time_taken')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_staff:
            return qs.none()
        return qs
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of logs
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing of logs
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
    
    def display_meta_info(self, obj):
        if obj.activity_type == 'clue_solved' and obj.meta_info:
            try:
                info = eval(obj.meta_info)
                return format_html('Clue: <strong>{}</strong>', info.get('clue_title', 'Unknown'))
            except:
                return obj.meta_info
        return obj.meta_info
    display_meta_info.short_description = 'Details'
    
    def time_taken(self, obj):
        if obj.activity_type == 'clue_solved' and obj.meta_info:
            try:
                info = eval(obj.meta_info)
                seconds = info.get('time_taken', 0)
                minutes = seconds / 60
                return format_html('{:.1f} minutes', minutes)
            except:
                return '-'
        return '-'
    time_taken.short_description = 'Time Taken'
    
    def get_list_display(self, request):
        if request.GET.get('activity_type') == 'clue_solved':
            return ('user', 'timestamp', 'display_meta_info', 'time_taken')
        return ('user', 'activity_type', 'timestamp', 'display_meta_info')
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.GET.get('activity_type') == 'clue_solved':
            extra_context['title'] = 'Clue Completion Logs'
        return super().changelist_view(request, extra_context)

class HintInline(admin.TabularInline):
    model = Hint
    extra = 1

def activate_selected(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_selected.short_description = "✅ Activate selected questions"

def deactivate_selected(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_selected.short_description = "🚫 Deactivate selected questions"

def activate_all(modeladmin, request, queryset):
    Question.objects.update(is_active=True)
activate_all.short_description = "☑️ Activate all questions"

def deactivate_all(modeladmin, request, queryset):
    Question.objects.update(is_active=False)
deactivate_all.short_description = "❎ Deactivate all questions"

def activate_selected(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_selected.short_description = "✅ Activate selected questions"

def deactivate_selected(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_selected.short_description = "❌ Deactivate selected questions"

def activate_all(modeladmin, request, queryset):
    Question.objects.update(is_active=True)
activate_all.short_description = "☑️ Activate all questions"

def deactivate_all(modeladmin, request, queryset):
    Question.objects.update(is_active=False)
deactivate_all.short_description = "❎ Deactivate all questions"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'points', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    ordering = ('order',)
    inlines = [HintInline]
    actions = [activate_selected, deactivate_selected, activate_all, deactivate_all]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            return {}  # Clear all actions for non-superusers
        return actions

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['is_active']
        return super().get_readonly_fields(request, obj)
    actions = [activate_selected, deactivate_selected, activate_all, deactivate_all]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            return {}  # Clear all actions for non-superusers
        return actions

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['is_active']
        return super().get_readonly_fields(request, obj)

@admin.register(PlayerProgress)
class PlayerProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_question', 'score', 'total_hints_used', 'total_time_spent', 'start_time', 'finish_time')
    list_filter = ('start_time', 'finish_time')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'current_question')

@admin.register(QuestionProgress)
class QuestionProgressAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'score_earned', 'display_time_taken', 'start_time', 'completion_time')
    list_filter = ('start_time', 'completion_time')
    search_fields = ('player__user__username', 'question__title')

    def display_time_taken(self, obj):
        if obj.time_taken:
            minutes = obj.time_taken.total_seconds() / 60
            return format_html('{} minutes', str(round(minutes, 1)))
        return '-'
    display_time_taken.short_description = 'Time Taken'

@admin.register(HintUsage)
class HintUsageAdmin(admin.ModelAdmin):
    list_display = ('question_progress', 'hint', 'used_time', 'points_deducted')
    list_filter = ('used_time',)
    search_fields = ('question_progress__player__user__username', 'question_progress__question__title')
    raw_id_fields = ('question_progress', 'hint')


@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    list_display = ('question', 'penalty_points')
    list_filter = ('question',)
    search_fields = ('content',)

@admin.register(SubmissionHistory)
class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'submitted_answer', 'is_correct', 'submission_time')
    list_filter = ('is_correct', 'submission_time')
    search_fields = ('player__username', 'question__title')
    raw_id_fields = ('player', 'question')
