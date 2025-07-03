from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Max, Count, Avg, F
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async
from functools import wraps
from .models import Question, PlayerProgress, Hint, SubmissionHistory, QuestionProgress, HintUsage
from django.utils import timezone
from .forms import CustomUserCreationForm, AnswerForm
from .activity_log import log_activity
import json
from datetime import timedelta
import logging

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

    # Get total number of questions
    total_questions = Question.objects.filter(is_active=True).count()
    
    context = {
        'player_progress': player_progress,
        'question_progress': question_progress,
        'total_questions': total_questions,  # Add this line
        'submission_history': submission_history,
    }
    return render(request, 'game/dashboard.html', context)
from .discord_logger import DiscordLogger

# Initialize discord logger at module level
discord_logger = DiscordLogger()

@user_passes_test(lambda u: u.is_staff)
def analytics_dashboard(request):
    # Get active players (players who have made a submission in the last 30 minutes)
    active_threshold = timezone.now() - timedelta(minutes=30)
    active_players_count = PlayerProgress.objects.filter(
        user__last_login__gte=active_threshold
    ).count()

    # Clue performance statistics
    clue_stats = []
    questions = Question.objects.all().order_by('order')  # Admin analytics needs all questions
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
        is_valid = await sync_to_async(form.is_valid)()  # Wrap form validation
        if is_valid:
            user = await sync_to_async(form.save)()  # Wrap form save
            await sync_to_async(PlayerProgress.objects.create)(user=user)  # Wrap model creation
            await sync_to_async(login)(request, user)  # Wrap login
            await discord_logger.log_user_activity(user.username, 'register')
            await log_activity(user, 'register')
            return redirect('game:game_interface')
    else:
        form = CustomUserCreationForm()
    return render(request, 'game/register.html', {'form': form})

async def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Wrap authenticate in sync_to_async
        user = await sync_to_async(authenticate)(request, username=username, password=password)
        if user is not None:
            # Wrap login in sync_to_async
            await sync_to_async(login)(request, user)
            # Wrap get_or_create in sync_to_async
            await sync_to_async(PlayerProgress.objects.get_or_create)(user=user)
            # Log the login activity
            await discord_logger.log_user_activity(user.username, 'login')
            await log_activity(user, 'login')
            return redirect('game:game_interface')
    return render(request, 'game/login.html')

@login_required
async def game_interface(request):
    # Check if any active questions exist
    active_questions_exist = await sync_to_async(Question.objects.filter(is_active=True).exists)()
    if not active_questions_exist:
        return await sync_to_async(render)(request, 'game/no_questions.html')

    progress, created = await sync_to_async(PlayerProgress.objects.get_or_create)(user=request.user)
    
    # If player has finished all questions, redirect to leaderboard
    if await sync_to_async(lambda: progress.finish_time)():
        return redirect('game:leaderboard')
    
    # Get current_question using sync_to_async
    current_question = await sync_to_async(lambda: progress.current_question)()
    
    # Check if current question is inactive
    if current_question and not current_question.is_active:
        # Find next active question
        next_question = await sync_to_async(
            Question.objects.filter(
                is_active=True,
                order__gte=current_question.order
            ).order_by('order').first
        )()
        
        if not next_question:
            # Fallback to first active question if none found after current
            next_question = await sync_to_async(
                Question.objects.filter(is_active=True).order_by('order').first
            )()
        
        if next_question:
            progress.current_question = next_question
            await sync_to_async(progress.save)()
            # Create QuestionProgress for new question
            await sync_to_async(QuestionProgress.objects.get_or_create)(
                player=progress,
                question=next_question
            )
            current_question = next_question
        else:
            # No active questions remaining
            progress.finish_time = timezone.now()
            await sync_to_async(progress.save)()
            return redirect('game:leaderboard')
    
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
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            progress = await sync_to_async(PlayerProgress.objects.get)(user=request.user)
            current_question = await sync_to_async(lambda: progress.current_question)()
            
            if not current_question:
                return JsonResponse({'error': 'No current question'}, status=400)
            
            # Get or create QuestionProgress
            question_progress = await sync_to_async(QuestionProgress.objects.get_or_create)(
                player=progress,
                question=current_question
            )
            question_progress = question_progress[0]  # get_or_create returns a tuple
            
            # Create submission history
            is_correct = answer.lower().strip() == current_question.answer.lower().strip()
            await sync_to_async(SubmissionHistory.objects.create)(
                player=request.user,
                question=current_question,
                submitted_answer=answer,
                is_correct=is_correct
            )
            
            if is_correct:
                # Update question progress
                question_progress.completion_time = timezone.now()
                question_progress.score_earned = current_question.points
                await sync_to_async(question_progress.save)()
                
                # Update player progress
                progress.score += current_question.points
                await sync_to_async(progress.completed_questions.add)(current_question)
                
                # Log successful clue solve
                await log_activity(request.user, 'clue_solved', meta_info=json.dumps({
                    'clue_number': current_question.order,
                    'score_earned': current_question.points,
                    'time_taken': str(question_progress.time_taken)
                }))
                
                # Get next question
                next_question = await sync_to_async(
                    Question.objects.filter(order__gt=current_question.order, is_active=True).order_by('order').first
                )()
                
                if next_question:
                    progress.current_question = next_question
                    # Create QuestionProgress for next question
                    await sync_to_async(QuestionProgress.objects.create)(
                        player=progress,
                        question=next_question
                    )
                else:
                    progress.finish_time = timezone.now()
                    progress.total_time_spent = progress.finish_time - progress.start_time
                    # Log completion when player finishes all questions
                    await discord_logger.log_completion(
                        request.user.username,
                        progress.total_time_spent.total_seconds(),
                        progress.score,
                        progress.total_hints_used
                    )
                    
                    # Log game completion in activity log
                    await log_activity(request.user, 'game_completed', meta_info=json.dumps({
                        'total_time': progress.total_time_spent.total_seconds(),
                        'final_score': progress.score,
                        'total_hints_used': progress.total_hints_used
                    }))
                
                await sync_to_async(progress.save)()
                
                # Log the success
                await discord_logger.log_clue_solved(
                    request.user.username,
                    current_question.order,
                    question_progress.time_taken.total_seconds() if question_progress.time_taken else 0
                )
                
                return JsonResponse({
                    'correct': True,
                    'message': 'Correct answer!',
                    'next_question': bool(next_question),
                    'score': progress.score
                })
            
            # Get attempt count from submission history
            attempt_count = await (await sync_to_async(SubmissionHistory.objects.filter)(
                player=request.user,
                question=current_question,
                is_correct=False
            )).acount()
            
            # Log wrong answer with attempt count
            await discord_logger.log_wrong_answer(request.user.username, current_question.order, answer, attempt_count + 1)
            
            # Record the wrong attempt
            await sync_to_async(SubmissionHistory.objects.create)(
                player=request.user,
                question=current_question,
                submitted_answer=answer,
                is_correct=False
            )
            
            # Log wrong answer
            await log_activity(request.user, 'wrong_answer', meta_info=json.dumps({
                'clue_number': current_question.order,
                'submitted_answer': answer
            }))
            return JsonResponse({
                'correct': False,
                'message': 'Incorrect answer. Try again!'
            })
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
async def get_hint(request):
    if request.method == 'POST':
        progress = await sync_to_async(PlayerProgress.objects.get)(user=request.user)
        current_question = await sync_to_async(lambda: progress.current_question)()
        
        if not current_question:
            return JsonResponse({'error': 'No current question'}, status=400)
        
        hint = await sync_to_async(lambda: Hint.objects.filter(question=current_question).first())()
        if hint:
            # Check if player has enough points for the hint
            if progress.score < hint.penalty_points:
                return JsonResponse({'error': '🛑 You dont have enough points to unlock this hint'}, status=400)
                
            question_progress = await sync_to_async(QuestionProgress.objects.get)(
                player=progress, 
                question=current_question
            )
            
            await sync_to_async(HintUsage.objects.create)(
                question_progress=question_progress,
                hint=hint,
                points_deducted=hint.penalty_points
            )
            
            # Update player's score
            progress.score = max(0, progress.score - hint.penalty_points)
            await sync_to_async(progress.save)()
            
            # Log the hint usage
            discord_logger = DiscordLogger()
            await discord_logger.log_hint_used(
                player=request.user.username,
                clue=current_question.title,
                hint_number=1,
                points_deducted=hint.penalty_points
            )
            
            return JsonResponse({
                'hint': hint.content,
                'points_deducted': hint.penalty_points,
                'penalty': hint.penalty_points
            })
        
        return JsonResponse({'error': 'No hint available'}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def help_view(request):
    return render(request, 'game/help.html')

@login_required
async def chrome_devtools_stub(request):
    return JsonResponse({}, status=200)

def leaderboard(request):
    # Get top players sorted by score (primary) and completion time (secondary)
    top_players = PlayerProgress.objects.filter(
        finish_time__isnull=False  # Only show players who have completed the game
    ).order_by('-score', 'total_time_spent')[:10]
    
    # Get total number of questions for progress calculation
    total_questions = Question.objects.filter(is_active=True).count()
    
    # Enhance player data with formatted duration
    for player in top_players:
        player.duration = str(player.total_time_spent).split('.')[0]  # Format as HH:MM:SS
        player.completed_count = player.completed_questions.count()  # Store count in a temporary attribute
        player.total_questions = total_questions
        if player.current_question:
            player.last_clue = f'Clue {player.current_question.order}'
    
    context = {
        'top_players': top_players,
        'total_questions': total_questions
    }
    return render(request, 'game/leaderboard.html', context)

@login_required
async def logout_view(request):
    try:
        # Get username before logout since we need it for logging
        username = await sync_to_async(lambda: request.user.username)()
        user = request.user
        
        # Log the activity before logout
        await log_activity(user, 'logout')
        
        # Use sync_to_async for logout
        await sync_to_async(logout)(request)
        
        # Log the logout activity
        await discord_logger.log_user_activity(username, 'logout')
        
        return redirect('game:home')
    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
        return redirect('game:home')


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add this to any view function where you want to test
async def test_discord_webhook(request):
    try:
        # Test user activity logging
        success = await discord_logger.log_user_activity("test_user", "login")
        if not success:
            logging.error("Failed to send Discord webhook for user activity")
            return HttpResponse("Webhook test failed - check logs")

        # Test clue solved logging
        success = await discord_logger.log_clue_solved("test_user", 1, 60.5)
        if not success:
            logging.error("Failed to send Discord webhook for clue solved")
            return HttpResponse("Webhook test failed - check logs")

        # Test hint used logging
        success = await discord_logger.log_hint_used("test_user", 1, 1)
        if not success:
            logging.error("Failed to send Discord webhook for hint used")
            return HttpResponse("Webhook test failed - check logs")

        return HttpResponse("Webhook tests completed - check Discord channels")
        
    except Exception as e:
        logging.error(f"Error during webhook test: {str(e)}")
        return HttpResponse(f"Error during test: {str(e)}")
