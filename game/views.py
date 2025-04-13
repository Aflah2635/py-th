from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Question, PlayerProgress, SubmissionHistory, Hint
from .forms import CustomUserCreationForm, AnswerForm
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProgress.objects.create(user=user)
            login(request, user)
            return redirect('game_home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'game/register.html', {'form': form})

@login_required
def game_home(request):
    player, created = PlayerProgress.objects.get_or_create(
        user=request.user,
        defaults={
            'start_time': timezone.now()
        }
    )
    
    if not player.current_question and not player.is_game_completed():
        first_question = Question.objects.filter(is_active=True).order_by('order').first()
        if first_question:
            player.current_question = first_question
            player.save()
    
    context = {
        'player': player,
        'form': AnswerForm() if player.current_question else None
    }
    return render(request, 'game/home.html', context)

@login_required
def submit_answer(request):
    if request.method != "POST":
        return redirect('game_home')
    
    player = get_object_or_404(PlayerProgress, user=request.user)
    if not player.current_question or player.is_game_completed():
        return redirect('game_home')
    
    form = AnswerForm(request.POST)
    if form.is_valid():
        submitted_answer = form.cleaned_data['answer']
        is_correct = submitted_answer == player.current_question.answer.lower()
        
        SubmissionHistory.objects.create(
            player=player,
            question=player.current_question,
            submitted_answer=submitted_answer,
            is_correct=is_correct
        )
        
        if is_correct:
            # Calculate points considering hint penalties
            points = player.current_question.points
            hint_penalties = sum(hint.penalty_points for hint in player.hints_used.filter(question=player.current_question))
            points = max(points - hint_penalties, 0)
            
            player.score += points
            player.completed_questions.add(player.current_question)
            
            # Find next question
            next_question = Question.objects.filter(
                is_active=True,
                order__gt=player.current_question.order
            ).first()
            
            if next_question:
                player.current_question = next_question
            else:
                player.current_question = None
                player.finish_time = timezone.now()
            
            player.save()
            
            # Send leaderboard update
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "leaderboard",
                {
                    "type": "leaderboard_update",
                    "leaderboard": get_leaderboard_data()
                }
            )
            
            messages.success(request, "Correct answer! Moving to next question.")
        else:
            messages.error(request, "Incorrect answer. Try again!")
    
    return redirect('game_home')

@login_required
def get_hint(request, question_id):
    player = get_object_or_404(PlayerProgress, user=request.user)
    question = get_object_or_404(Question, id=question_id)
    
    if question != player.current_question:
        messages.error(request, "You can only get hints for your current question!")
        return redirect('game_home')
    
    unused_hints = Hint.objects.filter(question=question).exclude(id__in=player.hints_used.all())
    if unused_hints.exists():
        hint = unused_hints.first()
        player.hints_used.add(hint)
        messages.info(request, f"Hint: {hint.content}")
    else:
        messages.warning(request, "No more hints available for this question!")
    
    return redirect('game_home')

@login_required
def leaderboard(request):
    # Get all users and their points, ordered by points descending
    players = User.objects.annotate(
        points=Sum('player__points')
    ).order_by('-points')
    
    return render(request, 'game/leaderboard.html', {'players': players})

def get_leaderboard_data():
    players = PlayerProgress.objects.select_related('user').order_by('-score')
    return [
        {
            'username': player.user.username,
            'score': player.score,
            'rank': idx + 1,
            'completed': player.is_game_completed()
        }
        for idx, player in enumerate(players)
    ]
