from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount, ChatLog
from itertools import chain
import random
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import os, threading
from pathlib import Path
# import speech_recognition as sr
import numpy as np
import librosa
from .apps import whisper_model, speech_emotion_model, label_encoder, text_emotion_model, cv
from django.shortcuts import get_object_or_404


# Create your views here.
@login_required(login_url="signin")
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)
    
    for users in user_following:
        user_following_list.append(users.user)
    for usernames in user_following_list:
        feed_list = Post.objects.filter(user=usernames)
        feed.append(feed_list)

    feed_list = list(chain(*feed))

    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestion_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestion_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 
                  "index.html", 
                  {
                      'user_profile': user_profile, 
                      'posts': feed_list, 
                      "suggestions_username_profile_list": suggestions_username_profile_list[:4],
                    })

@login_required(login_url="signin")
def settings_view(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        image = request.FILES.get('image', user_profile.profileimg)
        bio = request.POST.get("bio", "")
        location = request.POST.get("location", "")
        disability = request.POST.get("disability", None)

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        if disability == "blind":
            user_profile.is_blind = True
            user_profile.is_deaf = False
            user_profile.is_mute = False
        elif disability == "deaf":
            user_profile.is_blind = False
            user_profile.is_deaf = True
            user_profile.is_mute = False
        elif disability == "mute":
            user_profile.is_blind = False
            user_profile.is_deaf = False
            user_profile.is_mute = True
        else:
            user_profile.is_blind = False
            user_profile.is_deaf = False
            user_profile.is_mute = False
        user_profile.save()

        return redirect("/")
    return render(request, "setting.html", {'user_profile': user_profile})

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Taken")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, "Password Not Matching...!")
            return redirect("signup")
    else:
        return render(request, "signup.html")
    
def signin(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Invalid Credentials...!")
            return redirect("signin")
    else:
        return render(request, "signin.html")

@login_required(login_url="signin")    
def logout(request):

    auth.logout(request)
    return redirect("signin")

@login_required(login_url="signin")    
def upload(request):

    if request.method == "POST":
        if request.FILES.get("image_upload") is not None:
            user = request.user.username
            image = request.FILES.get("image_upload")
            caption = request.POST["caption"]
            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()
            return redirect("/")
        return redirect("/")
    else:
        return redirect("/")
    

@login_required(login_url='signin')
def like_post(request):

    username = request.user.username
    post_id = request.GET.get("post_id")

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect("/")
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect("/")
    
@login_required(login_url='signin')
def profile(request, pk):

    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    follower_username = []
    follower_object = FollowersCount.objects.filter(user=pk)
    for name in follower_object:
        follower_username.append(name.follower)
    # print(follower_username)
    follower_list = []
    for username in follower_username:
        follower_user = User.objects.get(username=username)
        follower_profile = Profile.objects.get(user=follower_user)
        follower_list.append(follower_profile)

    following_list = []
    following_username = []
    following_object = FollowersCount.objects.filter(follower=pk)
    for name in following_object:
        following_username.append(name.user)
    for username in following_username:
        following_user = User.objects.get(username=username)
        following_profile = Profile.objects.get(user=following_user)
        following_list.append(following_profile)
    # print(following_username)
    # print(follower_list)
    # print(following_list)
    # print(user_followers)
    # print(user_following)
    # for users in follower_list:
    #     print(users.user.username)

    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_post_length": user_post_length,
        "button_text": button_text,
        "user_followers": user_followers,
        "user_following": user_following,
        "follower_list": follower_list,
        "following_list": following_list,
    }
    return render(request, "profile.html", context)

@login_required(login_url='signin')
def follow(request):

    if request.method == "POST":
        follower = request.POST["follower"]
        user = request.POST["user"]

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect("/profile/"+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect("/profile/"+user)
    else:
        return redirect("/")
    
@login_required(login_url='signin')
def search(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    username_profile_list = []
    if request.method == "POST":
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, "search.html", {"user_profile": user_profile, "username_profile_list": username_profile_list})

@login_required(login_url='signin')
def delete_post(request, pk, post_id):

    post = Post.objects.get(id=post_id)

    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == 'yes':
            # Check if the post has an associated image
            if post.image:
                # Delete the associated image file from the server
                post.image.delete()

            # Delete the post from the database
            post.delete()

            return JsonResponse({'message': 'Post deleted successfully'})
        else:
            return JsonResponse({'message': 'Deletion not confirmed'})

    return JsonResponse({'message': 'Invalid request'})

# def transcribe_audio(audio_file_path):
#     """
#     Transcribes the audio from a WAV file and returns the text.

#     Args:
#         audio_file_path (str): Path to the WAV audio file.

#     Returns:
#         str: The transcribed text from the audio, or an error message if recognition fails.
#     """

#     try:
#         # Create a recognizer instance
#         recognizer = sr.Recognizer()

#         # Open the audio file using with statement for proper resource management
#         with sr.AudioFile(audio_file_path) as source:
#             # Listen to the audio data
#             audio_data = recognizer.record(source)

#         # Use Google Speech Recognition for accurate transcription
#         text = recognizer.recognize_google(audio_data)

#         return text

#     except Exception as e:
#         # Handle exceptions gracefully, informing the user about the issue
#         return f"Error transcribing audio: {e}"

# Function to predict emotion
def predict_text_emotion(chat_id, text):
    print(f"Started text emotion detection for chat_id: {chat_id}")
    try:
        chat_log = ChatLog.objects.filter(chat_id=chat_id).first()
        
        # Preprocess the text
        # Remove punctuation using for loop and if condition
        clean_text = ''
        for char in text:
            if char not in '''!()-[]{};:'"\,<>./?@#$%^&*_~''':
                clean_text += char
        # Convert text to lowercase
        clean_text_new = clean_text.lower()
        # print(clean_text_new)
        # Transform the text using the loaded CountVectorizer
        message = np.array([clean_text_new])
        vect = cv.transform(message).toarray()
        # print(vect)
        # Predict emotion
        prediction = text_emotion_model.predict(vect)
        # print("Prediction array:", prediction)  # Debugging print statement
        # Get the index of the predicted class label
        class_index = np.where(text_emotion_model.classes_ == prediction[0])[0][0]
        
        # Get the predicted class label
        predicted_class = text_emotion_model.classes_[class_index]
        print(f"Predicted Emotion: {predicted_class}")
        chat_log.emotion_class = predicted_class
        chat_log.save()
        # print(chat_log.transcript)
        print(f"Saved emotion_class for chat_id: {chat_id}")
    except Exception as e:
        print(f"Error during text emotion recognition: {e}")

    
def get_transcript(chat_id, audio_file_path):
    print(f"Started transcription for chat_id: {chat_id}")

    # Ensure whisper_model is loaded (potentially using a global variable)
    if not whisper_model:
        print("Whisper model is not loaded.")
        return

    try:
        result = whisper_model.transcribe(audio_file_path)
        # print(result["text"])
        chat_log = ChatLog.objects.filter(chat_id=chat_id).first()
        chat_log.transcript = result["text"]
        chat_log.save()
        # print(chat_log.transcript)
        print(f"Saved transcription for chat_id: {chat_id}")
    except Exception as e:
        print(f"Error during transcription: {e}")

# Define a function to extract MFCC, Mel, and Chroma features from an audio file
def extract_audio_features(filename):
    y, sr = librosa.load(filename, duration=3, offset=0.5)
    mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
    return np.concatenate((mfcc, mel, chroma))

def speech_emotion_prediction(chat_id, audio_file_path):
    print(f"Started emotion prediction for chat_id: {chat_id}")
    try:
        # Extract features from the audio file
        features = extract_audio_features(audio_file_path)
        # Reshape the features for model input
        features = np.expand_dims(features, axis=0)
        features = np.expand_dims(features, axis=-1)
        # Predict the emotion using the loaded model
        predicted_probabilities = speech_emotion_model.predict(features)
        # Get the predicted emotion label index
        predicted_emotion_index = np.argmax(predicted_probabilities)
        # Decode the predicted emotion label
        predicted_emotion_label = label_encoder.classes_[predicted_emotion_index]
        print("Predicted Emotion:", predicted_emotion_label)
        chat_log = ChatLog.objects.filter(chat_id=chat_id).first()
        chat_log.emotion_class = predicted_emotion_label
        chat_log.save()
        # print(chat_log.emotion_class)
        print(f"Saved emotion class for chat_id: {chat_id}")
    except Exception as e:
        print(f"Error during emotion recognition: {e}")

@csrf_exempt  # Use csrf_exempt decorator if CSRF protection is enabled and you're not using CSRF token in the fetch request
@login_required(login_url='signin')
def chat(request):

    if request.method == 'POST':
        try:
            chat_text = request.POST.get('message')
            friend_username = request.POST.get('friend_username')
            # print(chat_text)
            # Handle the audio file
            audio_file = request.FILES.get('audio')
            created_at = datetime.now()
            print(created_at)
            
            # Check for empty chat_text
            if not chat_text and not audio_file:
                return JsonResponse({'status': 'error', 'message': 'No message contents'})


            # Get the sender (chat_from) from the request user
            chat_from = request.user

            # Get the receiver (chat_to) based on the friend_username
            try:
                chat_to = User.objects.get(username=friend_username)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'})
            BASE_DIR = Path(__file__).resolve().parent.parent
            if chat_text:
                # Create a new ChatLog entry
                chat_log = ChatLog.objects.create(chat_from=chat_from, chat_to=chat_to, chat_text=chat_text, created_at=created_at)
                print("Started subprocess for text emotion recognition...")

                ter = threading.Thread(target=predict_text_emotion, args=(str(chat_log.chat_id), chat_log.chat_text))
                ter.start()
            
            # Process audio file
            if audio_file:
                # Get the filename directly from the string representation
                audio_filename = str(audio_file)  # Extract filename from the string

                
                # Save the converted audio to ChatLog
                chat_log = ChatLog.objects.create(
                    chat_from=chat_from,
                    chat_to=chat_to,
                    chat_audio=audio_file,
                    created_at=created_at
                )

                # # Convert webm to wav using ffmpeg
                
                webm_path = os.path.join(BASE_DIR, "media", "chat_audios", audio_filename)
                
                print("Started subprocess for transcription...")

                t = threading.Thread(target=get_transcript, args=(str(chat_log.chat_id), webm_path))
                t.start()
                
                print("Starting Thread for Speech Emotion Recognition...")
                ser = threading.Thread(target=speech_emotion_prediction, args=(str(chat_log.chat_id), webm_path))
                ser.start()
                # # Generate a unique UUID for the wav filename
                # wav_filename = f"{uuid.uuid4()}.wav"
                # wav_path = os.path.join(BASE_DIR, "media", "chat_audios", wav_filename)
                # print(webm_path)
                # command = ["ffmpeg", "-i", webm_path, wav_path]
                # subprocess.run(command)

                # Delete the webm file
                # os.remove(wav_path)
            # print('Received message to', friend_username, ':', chat_text, 'from', chat_from)
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required(login_url='signin')    
def get_chat_log(request, currentUser):

    chat_log = ChatLog.objects.filter(Q(chat_from__username=currentUser) | Q(chat_to__username=currentUser)).select_related('chat_from', 'chat_to').order_by('created_at')
    chat_data = []
    for message in chat_log:
        message_created_at = message.created_at.astimezone(timezone.get_current_timezone())
        chat_item = {
            'chat_id': str(message.chat_id),  # Convert chat_id to string
            'chat_from': message.chat_from.username,
            'chat_to': message.chat_to.username,
            'chat_text': message.chat_text,
            'transcript': message.transcript,
            'emotion_class': message.emotion_class,
            'created_at': message_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            # Add other relevant fields as required
        }
        # print(message.created_at)

        # print(settings.MEDIA_URL)
        # Check if the message has an audio file associated with it
        if message.chat_audio:
            audio_url = settings.MEDIA_URL + str(message.chat_audio)  # Assuming chat_audio is a FileField
            chat_item['audio_url'] = audio_url

        chat_data.append(chat_item)
    # print(chat_data)
    return JsonResponse({'chat_history': chat_data})

@csrf_exempt
@login_required(login_url='signin')
def delete_chat(request, chat_id):
    # Get the chat message object by chat_id
    chat_message = get_object_or_404(ChatLog, chat_id=chat_id)

    # Delete the associated files from the server (if any)
    if chat_message.chat_audio:
        # Construct the file path
        file_path = os.path.join(settings.MEDIA_ROOT, str(chat_message.chat_audio))
        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)  # Delete the file from the server


    # Delete the chat message
    chat_message.delete()

    # Return a JSON response indicating successful deletion
    return JsonResponse({'message': f'Chat: {chat_id} - Deleted Successfully.'})

@login_required(login_url='signin')
def message_view(request):
    user_following_list = []
    user_followers_list = []
    friends = []
    friends_list = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    user_followers = FollowersCount.objects.filter(user=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for follower in user_followers:
        user_followers_list.append(follower.follower)

    # Find common usernames
    friends_username = [username for username in user_following_list if username in user_followers_list]

    for usernames in friends_username:
        user = User.objects.get(username=usernames)  # Assuming username is unique
        friend_profile = Profile.objects.get(user=user)
        friends_list.append(friend_profile)

    chat_log = ChatLog.objects.filter(Q(chat_from__username=request.user) | Q(chat_to__username=request.user)).select_related('chat_from', 'chat_to').order_by('-created_at')
    # print(chat_log)
    if chat_log != None:
        friend_usernames = []
        for chat in chat_log:
            if chat.chat_from != request.user:
                friend_usernames.append(chat.chat_from)
            elif chat.chat_to != request.user:
                friend_usernames.append(chat.chat_to)
        # print(friend_usernames)
        # Create a mapping between usernames and profiles
        username_profile_mapping = {profile.user.username: profile for profile in friends_list}

        processed_usernames = set()

        # Initialize the sorted list
        sorted_friends_list = []

        # Iterate through friend_usernames
        for user in friend_usernames:
            # Check if the profile corresponding to the username is in user_follower_list and not already processed
            if user.username in username_profile_mapping and user.username not in processed_usernames:
                # Append the profile to sorted_user_follower_list
                sorted_friends_list.append(username_profile_mapping[user.username])
                # Add the username to the processed set
                processed_usernames.add(user.username)

        # Append profiles from user_follower_list that are not present in friend_usernames
        for profile in friends_list:
            if profile.user.username not in processed_usernames:
                sorted_friends_list.append(profile)
                processed_usernames.add(profile.user.username)


    # print(friends_list)
    # print(sorted_friends_list)
    # print(friends_username)
    # print(user_followers_list)
    # print(user_following_list)
    return render(request, "chat.html", { "friends_list": sorted_friends_list})