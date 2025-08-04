from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from storages.backends.s3boto3 import S3Boto3Storage


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expertise = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_students = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructors'
    
    def __str__(self):
        return f"Instructor: {self.user.get_full_name()}"


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.TextField(max_length=300)
    
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', storage=S3Boto3Storage())
    video_preview = models.FileField(upload_to='courses/previews/', storage=S3Boto3Storage(), blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_hours = models.PositiveIntegerField(help_text="Total duration of the course in hours")
    language = models.CharField(max_length=10, default='ar')
    requirements = models.TextField(blank=True, help_text="Course requirements")
    what_you_learn = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    enrolled_students = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def __str__(self):
        return self.title
    
    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        if self.discount_price:
            return ((self.price - self.discount_price) / self.price) * 100
        return 0


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    video_file = models.FileField(upload_to='courses/videos/', storage=S3Boto3Storage())
    duration_minutes = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=0)
    
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    """Student enrollment in courses"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)  # Progress percentage
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class LessonProgress(models.Model):
    """Student progress in lessons"""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    watched_duration = models.PositiveIntegerField(default=0)  # Watched duration in seconds
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']

class Review(models.Model):
    """Course Reviews"""
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'student']
    
    def __str__(self):
        return f"{self.course.title} - {self.rating} stars"

class Comment(models.Model):
    """Comments on lessons"""
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.lesson.title}"
