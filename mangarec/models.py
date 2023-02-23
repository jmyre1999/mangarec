from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from datetime import datetime

class UserProfileManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		"""
		Creates and saves a User with the given email and password.
		"""
		if not email:
		    raise ValueError('The given email must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_staff', True)

		if extra_fields.get('is_superuser') is not True:
		    raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(email, password, **extra_fields)

class UserProfile(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(max_length=75, db_index=True, unique=True)
	username = models.CharField(max_length=25, db_index=True, unique=True)
	image = models.ImageField(upload_to='userprofile', null=True, blank=True, max_length=500)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)

	objects = UserProfileManager()

	USERNAME_FIELD =  'email'

	# When converting to string, return user's email
	def __str__(self):
		return self.username

	def get_rec_list(self):
		# Get up to ten recommendations
		read_manga = self.get_read_manga()
		recommendation_list = []
		rating = 5
		while len(recommendation_list) < 10 and rating > 1:
			user_reviews = Review.objects.filter(user=user, rating=5)
			reviewed_mangas = Manga.objects.filter(review__in=user_reviews)
			rec_pairs = RecommendationPair.objects.filter(recommended_manga__in=manga).order_by('-score')
			for rec_pair in rec_pairs:
				for rec_manga in rec_pair.recommended_manga.all():
					if rec_manga not in read_manga and rec_manga not in recommendation_list:
						recommendation_list.append(rec_manga)
				if len(recommendation_list) == 10:
					break
			rating += 1

	def get_read_manga(self):
		return Manga.objects.filter(review__user=self).distinct()


class Manga(models.Model):
	title = models.CharField(max_length=50)
	image = models.ImageField(upload_to='manga', null=True, blank=True, max_length=500)

	def __str__(self):
		return self.title

class Review(models.Model):
	user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
	manga = models.ForeignKey('Manga', on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	comments = models.TextField()
	rating = models.IntegerField(default=0)

	def __str__(self):
		return f'Review of {self.manga} ({self.user})'

	def get_recommendations(self):
		# Get up to 5 recommendations
		read_manga = self.user.get_read_manga()
		recommendation_list = []
		rec_pairs = RecommendationPair.objects.filter(recommended_manga=self.manga).order_by('-score')
		for rec_pair in rec_pairs:
			rec_manga = rec_pair.get_recommendation(self.manga)
			if rec_manga not in read_manga and rec_manga not in recommendation_list:
				recommendation_list.append(rec_manga)
				if len(recommendation_list) == 5:
					break
		return recommendation_list

class Recommendation(models.Model):
	review = models.ForeignKey('Review', on_delete=models.CASCADE)
	recommended_manga = models.ForeignKey('Manga', on_delete=models.CASCADE)
	comments = models.TextField()
	score = models.IntegerField(default=0)

class RecommendationPair(models.Model):
	recommended_manga = models.ManyToManyField('Manga')
	score = models.IntegerField(default=0)

	def get_recommendation(self, manga):
		return self.recommended_manga.exclude(pk=manga.pk).first()