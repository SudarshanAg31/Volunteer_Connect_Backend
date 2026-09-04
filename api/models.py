from django.db import models

class User(models.Model):
    ROLE_CHOICES = (
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
    )
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='volunteer')
    profile_image = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Opportunity(models.Model):
    CATEGORY_CHOICES = (
        ('Education', 'Education'),
        ('Environment', 'Environment'),
        ('Health', 'Health'),
        ('Community', 'Community'),
        ('Animal Welfare', 'Animal Welfare'),
        ('Social Service', 'Social Service'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    ngo_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    date = models.DateField()
    time = models.CharField(max_length=100)
    volunteers_required = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_email = models.CharField(max_length=255, default='', blank=True)
    
    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'opportunity')
    
    def __str__(self):
        return f"{self.user.name} - {self.opportunity.title}"