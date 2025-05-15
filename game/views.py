from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Max, Count, Avg, F
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async
from functools import wraps
from .models import Question, PlayerProgress, Hint, SubmissionHistory, QuestionProgress, HintUsage
from django.utils import timezone
from .forms import CustomUserCreationForm, AnswerForm
import json
from datetime import timedelta

@login_required
def dashboard(request):
    player_progress, created = PlayerProgress.objects.get_or_create(user=request.user)
    question_progress = QuestionProgress.objects.filter(
        player=player_progress
    ).select_related('question').prefetch_related('hintusage_set')
    submission_history = SubmissionHistory.objects.filter(
        player=request.user
    ).select_related('question').order_by('-submission_time')[:10]

    # Calculate player's rank
    rank = PlayerProgress.objects.filter(score__gt=player_progress.score).count() + 1
    player_progress.rank = rank

    context = {
        'player_progress': player_progress,
        'question_progress': question_progress,
        'submission_history': submission_history,
    }
    return render(request, 'game/dashboard.html', context)
from .discord_logger import discord_logger

@user_passes_test(lambda u: u.is_staff)
def analytics_dashboard(request):
    # Get active players (players who have made a submission in the last 30 minutes)
    active_threshold = timezone.now() - timedelta(minutes=30)
    active_players_count = PlayerProgress.objects.filter(
        user__last_login__gte=active_threshold
    ).count()

    # Clue performance statistics
    clue_stats = []
    questions = Question.objects.all().order_by('order')
    for question in questions:
        total_attempts = QuestionProgress.objects.filter(question=question).count()
        if total_attempts > 0:
            solved_count = QuestionProgress.objects.filter(question=question).exclude(completion_time=None).count()
            hint_count = HintUsage.objects.filter(question_progress__question=question).count()
            avg_time = QuestionProgress.objects.filter(
                question=question
            ).exclude(completion_time=None).aggregate(avg_time=Avg('time_taken'))['avg_time'] or timedelta()
            avg_seconds = int(avg_time.total_seconds())

            clue_stats.append({
                'title': f'Clue {question.order}',
                'solve_rate': round((solved_count / total_attempts) * 100, 1),
                'avg_time': str(timedelta(seconds=avg_seconds)),
                'hint_usage': round((hint_count / total_attempts) * 100, 1)
            })

    # Fastest solvers
    fastest_solvers = []
    for question in questions:
        fastest = QuestionProgress.objects.filter(
            question=question,
            completion_time__isnull=False
        ).order_by('time_taken').first()
        if fastest:
            fastest_solvers.append({
                'clue': f'Clue {question.order}',
                'player': fastest.player.user.username,
                'time': str(fastest.time_taken) if fastest.time_taken else 'N/A'
            })

    # Active clues
    active_clues = [{
        'title': f'Clue {q.order}',
        'active_players': PlayerProgress.objects.filter(
            current_question=q,
            user__last_login__gte=active_threshold
        ).count()
    } for q in questions]

    # Chart data
    solve_rate_data = {
        'labels': [f'Clue {q.order}' for q in questions],
        'datasets': [{
            'label': 'Solve Rate (%)',
            'data': [stat['solve_rate'] for stat in clue_stats],
            'backgroundColor': 'rgba(0, 255, 255, 0.2)',
            'borderColor': 'rgba(0, 255, 255, 1)',
            'borderWidth': 1
        }]
    }

    dropoff_data = {
        'labels': [f'Clue {q.order}' for q in questions],
        'datasets': [{
            'label': 'Active Players',
            'data': [c['active_players'] for c in active_clues],
            'borderColor': 'rgba(255, 99, 132, 1)',
            'tension': 0.1,
            'fill': False
        }]
    }

    # Activity heatmap data (simplified version)
    activity_data = {
        'datasets': [{
            'label': 'Activity',
            'data': [{
                'x': stat['solve_rate'],
                'y': stat['hint_usage'],
                'r': 10
            } for stat in clue_stats],
            'backgroundColor': 'rgba(255, 99, 132, 0.5)'
        }]
    }

    context = {
        'active_players_count': active_players_count,
        'clue_stats': clue_stats,
        'fastest_solvers': fastest_solvers,
        'active_clues': active_clues,
        'solve_rate_data': json.dumps(solve_rate_data),
        'dropoff_data': json.dumps(dropoff_data),
        'activity_data': json.dumps(activity_data)
    }
    return render(request, 'game/admin_analytics.html', context)

def home(request):
    return render(request, 'game/home.html')

async def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProgress.objects.create(user=user)
            login(request, user)
            await discord_logger.log_user_activity(user.username, 'register')
            return redirect('game:game_interface')
    else:
        form = CustomUserCreationForm()
    return render(request, 'game/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Create PlayerProgress if it doesn't exist
            PlayerProgress.objects.get_or_create(user=user)
            return redirect('game:game_interface')
    return render(request, 'game/login.html')

@login_required
async def game_interface(request):
    progress, created = await sync_to_async(PlayerProgress.objects.get_or_create)(user=request.user)
    
    # If player has finished all questions, redirect to leaderboard
    if await sync_to_async(lambda: progress.finish_time)():
        return redirect('game:leaderboard')
    
    # Get current_question using sync_to_async
    current_question = await sync_to_async(lambda: progress.current_question)()
    if not current_question:
        first_question = await sync_to_async(Question.objects.filter(is_active=True).order_by('order').first)()
        if first_question:
            await sync_to_async(setattr)(progress, 'current_question', first_question)
            await sync_to_async(progress.save)()
            # Create QuestionProgress for the first question
            await sync_to_async(QuestionProgress.objects.create)(
                player=progress,
                question=first_question
            )
    
    # Get completed_questions using sync_to_async
    completed_questions = await sync_to_async(lambda: list(progress.completed_questions.all()))()    
    context = {
        'progress': progress,
        'completed_questions': completed_questions,
    }
    return await sync_to_async(render)(request, 'game/game_interface.html', context)

@login_required
async def submit_answer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        form = AnswerForm(request.POST)
        if not form.is_valid():
            return JsonResponse({
                'error': 'Invalid answer format',
                'details': form.errors.get('answer', ['Please provide a valid answer'])[0]
            }, status=400)
            
        # Get cleaned answer from the form
        normalized_answer = form.cleaned_data['answer']  # Already cleaned by form's clean_answer method
        progress = await sync_to_async(PlayerProgress.objects.get)(user=request.user)
        question = progress.current_question
        
        if not question:
            return JsonResponse({'error': 'No current question'}, status=400)
        
        # Create a form for the question's answer and clean it
        question_form = AnswerForm({'answer': question.answer})
        if not question_form.is_valid():
            return JsonResponse({'error': 'Invalid question configuration'}, status=500)
            
        normalized_question_answer = question_form.cleaned_data['answer']  # Use form's cleaning
        is_correct = normalized_answer == normalized_question_answer
        await sync_to_async(SubmissionHistory.objects.create)(
            player=progress.user,
            question=question,
            submitted_answer=normalized_answer,
            is_correct=is_correct
        )
        
        if is_correct:
            # Update QuestionProgress
            question_progress = await sync_to_async(QuestionProgress.objects.get)(player=progress, question=question)
            question_progress.completion_time = timezone.now()
            question_progress.score_earned = question.points
            await sync_to_async(question_progress.save)()
            
            # Update PlayerProgress
            progress.score += question.points
            await sync_to_async(progress.completed_questions.add)(question)
            progress.total_time_spent = await sync_to_async(lambda: sum(
                (qp.time_taken for qp in QuestionProgress.objects.filter(player=progress) if qp.time_taken),
                timezone.timedelta()
            ))()
            
            next_question = await sync_to_async(Question.objects.filter(
                is_active=True,
                order__gt=question.order
            ).first)()
            
            if next_question:
                progress.current_question = next_question
                await sync_to_async(progress.save)()
                # Create QuestionProgress for the next question
                await sync_to_async(QuestionProgress.objects.create)(
                    player=progress,
                    question=next_question
                )
                await discord_logger.log_game_progress(request.user.username, next_question.order, progress.score)
                return JsonResponse({'success': True, 'points': question.points})
            else:
                # No more questions - game completed
                progress.current_question = None
                progress.finish_time = timezone.now()
                await sync_to_async(progress.save)()
                await discord_logger.log_high_score(request.user.username, progress.score)
                return JsonResponse({
                    'success': True,
                    'points': question.points,
                    'completed': True,
                    'redirect_url': reverse('game:leaderboard')
                })
        
        return JsonResponse({'success': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
async def get_hint(request):
    if request.method == 'POST':
        progress = await sync_to_async(PlayerProgress.objects.get)(user=request.user)
        question = progress.current_question
        
        if not question:
            return JsonResponse({'error': 'No current question'}, status=400)
        
        hint = await sync_to_async(Hint.objects.filter(question=question).first)()
        if hint:
            # Create HintUsage record
            question_progress = await sync_to_async(QuestionProgress.objects.get)(player=progress, question=question)
            await sync_to_async(HintUsage.objects.create)(
                question_progress=question_progress,
                hint=hint,
                points_deducted=hint.penalty_points
            )
            
            # Update progress
            progress.score = max(0, progress.score - hint.penalty_points)
            progress.total_hints_used += 1
            await sync_to_async(progress.save)()
            
            return JsonResponse({
                'hint': hint.content,
                'penalty': hint.penalty_points
            })
        
        return JsonResponse({'error': 'No hint available'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def leaderboard(request):
    top_players = PlayerProgress.objects.order_by('-score')[:10]
    context = {'top_players': top_players}
    return render(request, 'game/leaderboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('game:home')
