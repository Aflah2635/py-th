from django.contrib import admin
from django.utils.html import format_html
from .models import Question, PlayerProgress, Hint, SubmissionHistory, QuestionProgress, HintUsage

class HintInline(admin.TabularInline):
    model = Hint
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'points', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    ordering = ('order',)
    inlines = [HintInline]

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
            return format_html('{:.1f} minutes', minutes)
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
