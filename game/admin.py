from django.contrib import admin
from django.utils.html import format_html
from .models import Question, Hint, PlayerProgress, SubmissionHistory

class HintInline(admin.TabularInline):
    model = Hint
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'points', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('order',)
    inlines = [HintInline]

@admin.register(PlayerProgress)
class PlayerProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_question', 'score', 'rank_display', 'start_time', 'finish_time')
    list_filter = ('start_time', 'finish_time')
    search_fields = ('user__username',)
    readonly_fields = ('score', 'start_time')
    
    def rank_display(self, obj):
        rank = obj.calculate_rank()
        if rank == 1:
            color = 'gold'
        elif rank == 2:
            color = 'silver'
        elif rank == 3:
            color = '#CD7F32'  # bronze
        else:
            color = 'black'
        return format_html('<span style="color: {}">#{}</span>', color, rank)
    rank_display.short_description = 'Rank'

@admin.register(SubmissionHistory)
class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'submitted_answer', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'submitted_at')
    search_fields = ('player__user__username', 'question__title')
    readonly_fields = ('submitted_at',)
