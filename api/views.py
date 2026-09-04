import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, models
from .models import User, Opportunity, Application

def json_response(success, message, data=None, status=200):
    response = {'success': success, 'message': message}
    if data is not None:
        response['data'] = data
    return JsonResponse(response, status=status)

def get_user_data(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'role': user.role,
        'profile_image': user.profile_image
    }

def get_opportunity_data(opp):
        # Fix: Date ko safely handle karo (String ho ya DateField)
    if hasattr(opp.date, 'strftime'):
        date_str = opp.date.strftime('%Y-%m-%d')
    else:
        date_str = opp.date  # Agar pehle se string hai
    return {
        'id': opp.id,
        'title': opp.title,
        'description': opp.description,
        'ngo_name': opp.ngo_name,
        'category': opp.category,
        'location': opp.location,
        'latitude': opp.latitude,
        'longitude': opp.longitude,
        'date': date_str,  # Fix: Direct string, strftime nahi
        'time': opp.time,
        'volunteers_required': opp.volunteers_required,
        'created_at': opp.created_at.strftime('%Y-%m-%d %H:%M:%S') if opp.created_at else '',
        'created_by_email': opp.created_by_email
    }

@csrf_exempt
def register(request):
    if request.method != 'POST':
        return json_response(False, 'Method not allowed', status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'volunteer')
        if role == 'admin':
            return json_response(False, 'SuperAdmin cannot be registered from app', status=403)
        if not all([name, email, phone, password]):
            return json_response(False, 'All fields are required', status=400)
        
        if User.objects.filter(email=email).exists():
            return json_response(False, 'Email already registered', status=400)
        
        user = User.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role
        )
        
        return json_response(True, 'Registration successful', get_user_data(user), status=201)
    
    except json.JSONDecodeError:
        return json_response(False, 'Invalid JSON', status=400)
    except Exception as e:
        return json_response(False, str(e), status=500)

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return json_response(False, 'Method not allowed', status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return json_response(False, 'Email and password required', status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return json_response(False, 'Invalid email or password', status=401)
        
        if user.password != password:
            return json_response(False, 'Invalid email or password', status=401)
        
        return json_response(True, 'Login successful', get_user_data(user))
    
    except json.JSONDecodeError:
        return json_response(False, 'Invalid JSON', status=400)
    except Exception as e:
        return json_response(False, str(e), status=500)

@csrf_exempt
def user_detail(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return json_response(False, 'User not found', status=404)
    
    if request.method == 'GET':
        return json_response(True, 'User found', get_user_data(user))
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user.name = data.get('name', user.name)
            user.phone = data.get('phone', user.phone)
            user.profile_image = data.get('profile_image', user.profile_image)
            user.save()
            return json_response(True, 'Profile updated successfully', get_user_data(user))
        except json.JSONDecodeError:
            return json_response(False, 'Invalid JSON', status=400)
        except Exception as e:
            return json_response(False, str(e), status=500)
    
    return json_response(False, 'Method not allowed', status=405)

@csrf_exempt
def opportunity_list(request):
    if request.method == 'GET':
        opportunities = Opportunity.objects.all().order_by('-created_at')
        
        # NGO ko sirf apni opportunities dikhni hain
        role = request.GET.get('role', '')
        email = request.GET.get('email', '')
        
        if role == 'ngo':
            opportunities = opportunities.filter(created_by_email=email)
        
        search = request.GET.get('search', '')
        if search:
            opportunities = opportunities.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(ngo_name__icontains=search) |
                models.Q(location__icontains=search)
            )
        
        category = request.GET.get('category', '')
        if category:
            opportunities = opportunities.filter(category=category)
        
        data = [get_opportunity_data(opp) for opp in opportunities]
        return json_response(True, 'Opportunities fetched', data)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Admin ya NGO create kar sakta hai
            role = data.get('role', 'volunteer')
            if role not in ['admin', 'ngo']:
                return json_response(False, 'Only Admin or NGO can create opportunities', status=403)
            
            opportunity = Opportunity.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                ngo_name=data.get('ngo_name'),
                category=data.get('category'),
                location=data.get('location'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                date=data.get('date'),
                time=data.get('time'),
                volunteers_required=data.get('volunteers_required'),
                created_by_email=data.get('email', '')  # <--- YEH LINE IMPORTANT HAI
            )
            
            return json_response(True, 'Opportunity created', get_opportunity_data(opportunity), status=201)
        
        except json.JSONDecodeError:
            return json_response(False, 'Invalid JSON', status=400)
        except Exception as e:
            return json_response(False, str(e), status=500)
    
    return json_response(False, 'Method not allowed', status=405)

@csrf_exempt
def opportunity_detail(request, opportunity_id):
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return json_response(False, 'Opportunity not found', status=404)
    
    if request.method == 'GET':
        return json_response(True, 'Opportunity found', get_opportunity_data(opportunity))
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            role = data.get('role', 'volunteer')
            email = data.get('email', '')
            
            # Admin ya owner NGO update kar sakta hai
            if role != 'admin' and (role != 'ngo' or email != opportunity.created_by_email):
                return json_response(False, 'Not authorized to update this opportunity', status=403)
            
            opportunity.title = data.get('title', opportunity.title)
            opportunity.description = data.get('description', opportunity.description)
            opportunity.ngo_name = data.get('ngo_name', opportunity.ngo_name)
            opportunity.category = data.get('category', opportunity.category)
            opportunity.location = data.get('location', opportunity.location)
            opportunity.latitude = data.get('latitude', opportunity.latitude)
            opportunity.longitude = data.get('longitude', opportunity.longitude)
            opportunity.date = data.get('date', opportunity.date)
            opportunity.time = data.get('time', opportunity.time)
            opportunity.volunteers_required = data.get('volunteers_required', opportunity.volunteers_required)
            opportunity.save()
            
            return json_response(True, 'Opportunity updated', get_opportunity_data(opportunity))
        
        except json.JSONDecodeError:
            return json_response(False, 'Invalid JSON', status=400)
        except Exception as e:
            return json_response(False, str(e), status=500)
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            role = data.get('role', 'volunteer')
            email = data.get('email', '')
            
            # Admin ya owner NGO delete kar sakta hai
            if role != 'admin' and (role != 'ngo' or email != opportunity.created_by_email):
                return json_response(False, 'Not authorized to delete this opportunity', status=403)
            
            opportunity.delete()
            return json_response(True, 'Opportunity deleted')
        except json.JSONDecodeError:
            return json_response(False, 'Invalid JSON', status=400)
        except Exception as e:
            return json_response(False, str(e), status=500)
    
    return json_response(False, 'Method not allowed', status=405)

@csrf_exempt
def create_application(request):
    if request.method != 'POST':
        return json_response(False, 'Method not allowed', status=405)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        opportunity_id = data.get('opportunity_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return json_response(False, 'User not found', status=404)
        
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return json_response(False, 'Opportunity not found', status=404)
        
        if Application.objects.filter(user=user, opportunity=opportunity).exists():
            return json_response(False, 'You have already applied for this opportunity', status=400)
        
        application = Application.objects.create(
            user=user,
            opportunity=opportunity,
            status='Applied'
        )
        
        return json_response(True, 'Application submitted successfully', {
            'application_id': application.id,
            'status': application.status
        }, status=201)
    
    except json.JSONDecodeError:
        return json_response(False, 'Invalid JSON', status=400)
    except Exception as e:
        return json_response(False, str(e), status=500)

def get_user_applications(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return json_response(False, 'User not found', status=404)
    
    applications = Application.objects.filter(user=user).order_by('-applied_date')
    
    data = []
    for app in applications:
        data.append({
            'application_id': app.id,
            'opportunity_id': app.opportunity.id,
            'title': app.opportunity.title,
            'ngo_name': app.opportunity.ngo_name,
            'category': app.opportunity.category,
            'location': app.opportunity.location,
            'date': app.opportunity.date.strftime('%Y-%m-%d'),
            'time': app.opportunity.time,
            'status': app.status,
            'applied_date': app.applied_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return json_response(True, 'Applications fetched', data)

@csrf_exempt
def cancel_application(request, application_id):
    if request.method != 'DELETE':
        return json_response(False, 'Method not allowed', status=405)
    
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return json_response(False, 'Application not found', status=404)
    
    if application.status == 'Approved':
        return json_response(False, 'Cannot cancel an approved application', status=400)
    
    application.status = 'Cancelled'
    application.save()
    
    return json_response(True, 'Application cancelled')

@csrf_exempt
def update_application_status(request, application_id):
    if request.method != 'PUT':
        return json_response(False, 'Method not allowed', status=405)
    
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return json_response(False, 'Application not found', status=404)
    
    try:
        data = json.loads(request.body)
        role = data.get('role', 'volunteer')
        email = data.get('email', '')
        
        # Admin ya owner NGO status update kar sakta hai
        if role != 'admin' and (role != 'ngo' or email != application.opportunity.created_by_email):
            return json_response(False, 'Not authorized to update application status', status=403)
        
        new_status = data.get('status')
        valid_statuses = ['Applied', 'Approved', 'Rejected', 'Cancelled']
        
        if new_status not in valid_statuses:
            return json_response(False, 'Invalid status', status=400)
        
        application.status = new_status
        application.save()
        
        return json_response(True, 'Application status updated', {'status': application.status})
    
    except json.JSONDecodeError:
        return json_response(False, 'Invalid JSON', status=400)
    except Exception as e:
        return json_response(False, str(e), status=500)

@csrf_exempt
def get_applicants(request, opportunity_id):
    if request.method != 'GET':
        return json_response(False, 'Method not allowed', status=405)
    
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return json_response(False, 'Opportunity not found', status=404)
    
    # Admin ya Owner NGO applicants dekh sakta hai
    role = request.GET.get('role', 'volunteer')
    email = request.GET.get('email', '')
    
    if role != 'admin' and (role != 'ngo' or email != opportunity.created_by_email):
        return json_response(False, 'Only Admin or Owner NGO can view applicants', status=403)
    
    applications = Application.objects.filter(opportunity=opportunity).order_by('-applied_date')
    
    data = []
    for app in applications:
        data.append({
            'application_id': app.id,
            'volunteer_name': app.user.name,
            'email': app.user.email,
            'phone': app.user.phone,
            'status': app.status,
            'applied_date': app.applied_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return json_response(True, 'Applicants fetched', data)

@csrf_exempt
def admin_dashboard_stats(request):
    if request.method != 'GET':
        return json_response(False, 'Method not allowed', status=405)
    role = request.GET.get('role', 'volunteer')
    if role != 'admin':
        return json_response(False, 'Only admin can access dashboard', status=403)
    total_users = User.objects.count()
    total_volunteers = User.objects.filter(role='volunteer').count()
    total_opportunities = Opportunity.objects.count()
    total_applications = Application.objects.count()
    pending_applications = Application.objects.filter(status='Applied').count()
    return json_response(True, 'Dashboard stats fetched', {
        'total_users': total_users, 'total_volunteers': total_volunteers,
        'total_opportunities': total_opportunities, 'total_applications': total_applications,
        'pending_applications': pending_applications
    })

@csrf_exempt
def get_all_applications_admin(request):
    if request.method != 'GET':
        return json_response(False, 'Method not allowed', status=405)
    role = request.GET.get('role', 'volunteer')
    if role != 'admin':
        return json_response(False, 'Only admin can view all applications', status=403)
    applications = Application.objects.all().order_by('-applied_date')
    data = [{'application_id': a.id, 'volunteer_name': a.user.name, 'opportunity_title': a.opportunity.title, 'status': a.status, 'applied_date': a.applied_date.strftime('%Y-%m-%d %H:%M:%S')} for a in applications]
    return json_response(True, 'All applications fetched', data)