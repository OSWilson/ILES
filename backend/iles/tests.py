
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation



def make_user(username, role, **kwargs):

    return CustomUser.objects.create_user(
        username=username,
        password='testpass123',
        first_name='Test',
        last_name='User',
        email=f'{username}@test.com',
        role=role,
        **kwargs
    )


def make_placement(student, workplace=None, academic=None):
   
    today = date.today()
    return InternshipPlacement.objects.create(
        student=student,
        workplace_supervisor=workplace,
        academic_supervisor=academic,
        company_name='Test Company Ltd',
        start_date=today,
        end_date=today + timedelta(weeks=12),
    )



class CustomUserModelTest(TestCase):
    

    def test_full_name_with_both_names(self):
     
        user = make_user('alice', 'student')
        user.first_name = 'Alice'
        user.last_name = 'Banda'
        self.assertEqual(user.full_name, 'Alice Banda')

    def test_full_name_falls_back_to_username(self):
       
        user = make_user('alice', 'student')
        user.first_name = ''
        user.last_name = ''
        self.assertEqual(user.full_name, 'alice')

    def test_str_representation(self):
        
        user = make_user('bob', 'workplace')
        self.assertIn('workplace', str(user))

    def test_student_number_is_unique(self):
        
        from django.db import IntegrityError
        make_user('s1', 'student', student_number='2024/001')
        with self.assertRaises(IntegrityError):
            make_user('s2', 'student', student_number='2024/001')


class PlacementModelTest(TestCase):
    
    def setUp(self):
       
        self.student = make_user('student1', 'student')
        self.today = date.today()

    def test_valid_placement_saves(self):
     
        p = InternshipPlacement(
            student=self.student,
            company_name='Acme Corp',
            start_date=self.today,
            end_date=self.today + timedelta(weeks=8),
        )
        p.save()  # should not raise
        self.assertEqual(InternshipPlacement.objects.count(), 1)

    def test_end_before_start_raises_error(self):
        """End date before start date should raise ValidationError."""
        from django.core.exceptions import ValidationError
        p = InternshipPlacement(
            student=self.student,
            company_name='Acme',
            start_date=self.today,
            end_date=self.today - timedelta(days=1),  # end BEFORE start
        )
        with self.assertRaises(ValidationError):
            p.save()

    def test_overlapping_placements_blocked(self):
       
        from django.core.exceptions import ValidationError

     
        InternshipPlacement.objects.create(
            student=self.student,
            company_name='Company A',
            start_date=self.today,
            end_date=self.today + timedelta(weeks=12),
        )

        p2 = InternshipPlacement(
            student=self.student,
            company_name='Company B',
            start_date=self.today + timedelta(weeks=4),  # overlaps
            end_date=self.today + timedelta(weeks=16),
        )
        with self.assertRaises(ValidationError):
            p2.save()


class WeeklyLogModelTest(TestCase):
   

    def setUp(self):
        self.student = make_user('student1', 'student')
        self.supervisor = make_user('sup1', 'workplace')
        self.placement = make_placement(self.student, workplace=self.supervisor)

    def _make_log(self, week=1):
        return WeeklyLog.objects.create(
            student=self.student,
            placement=self.placement,
            week_number=week,
            week_start_date=date.today(),
            activities='Worked on Django REST API.',
        )

    def test_new_log_is_draft(self):
      
        log = self._make_log()
        self.assertEqual(log.status, 'draft')

    def test_can_edit_draft(self):
       
        log = self._make_log()
        self.assertTrue(log.can_edit())

    def test_cannot_edit_approved_log(self):
        
        log = self._make_log()
        log.approve(self.supervisor)
        self.assertFalse(log.can_edit())

    def test_submit_changes_status(self):
       
        log = self._make_log()
        log.submit()
        self.assertEqual(log.status, 'submitted')

    def test_approve_changes_status(self):
  
        log = self._make_log()
        log.submit()
        log.approve(self.supervisor)
        log.refresh_from_db()
        self.assertEqual(log.status, 'approved')
        self.assertEqual(log.reviewed_by, self.supervisor)

    def test_reject_changes_status_and_stores_comment(self):
        
        log = self._make_log()
        log.submit()
        log.reject(self.supervisor, 'Insufficient detail.')
        log.refresh_from_db()
        self.assertEqual(log.status, 'rejected')
        self.assertEqual(log.supervisor_comment, 'Insufficient detail.')

    def test_cannot_submit_already_approved_log(self):
       
        from django.core.exceptions import ValidationError
        log = self._make_log()
        log.submit()
        log.approve(self.supervisor)
        with self.assertRaises(ValidationError):
            log.submit()

    def test_duplicate_week_raises_error(self):
       
        from django.core.exceptions import ValidationError
        self._make_log(week=1)
        log2 = WeeklyLog(
            student=self.student,
            placement=self.placement,
            week_number=1,  # duplicate week
            week_start_date=date.today(),
            activities='Another entry.',
        )
        with self.assertRaises(ValidationError):
            log2.save()


class AuthAPITest(TestCase):
 
    def setUp(self):
        self.client = APIClient()
        self.user = make_user('testuser', 'student')

    def test_login_with_valid_credentials(self):

        res = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertIn('user', res.data)

    def test_login_with_wrong_password(self):
       
        res = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_creates_user(self):
      
        res = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_register_mismatched_passwords(self):
     
        res = self.client.post('/api/auth/register/', {
            'username': 'bad',
            'role': 'student',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass!',
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_requires_auth(self):
        
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_user_data(self):
       
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'testuser')


class PlacementAPITest(TestCase):
   
    def setUp(self):
        self.client = APIClient()
        self.student = make_user('student1', 'student')
        self.admin = make_user('admin1', 'admin')
        self.today = date.today()

    def test_student_sees_only_own_placements(self):
     
        
        make_placement(self.student)

        other = make_user('other', 'student')
        make_placement(other)

        self.client.force_authenticate(user=self.student)
        res = self.client.get('/api/placements/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)  # only sees own placement

    def test_admin_creates_placement(self):
     
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/placements/', {
            'student': self.student.id,
            'company_name': 'Google Uganda',
            'start_date': str(self.today),
            'end_date': str(self.today + timedelta(weeks=12)),
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_cannot_access(self):

        res = self.client.get('/api/placements/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class WeeklyLogAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.student = make_user('student1', 'student')
        self.supervisor = make_user('sup1', 'workplace')
        self.placement = make_placement(self.student, workplace=self.supervisor)

    def test_student_can_create_log(self):
     
        self.client.force_authenticate(user=self.student)
        res = self.client.post('/api/logs/', {
            'week_number': 1,
            'week_start_date': str(date.today()),
            'activities': 'Attended team standup and wrote unit tests.',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WeeklyLog.objects.count(), 1)

    def test_student_cannot_see_other_students_logs(self):
  
        other = make_user('other', 'student')
        other_placement = make_placement(other)

        WeeklyLog.objects.create(
            student=other,
            placement=other_placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Other student activities.',
        )

        self.client.force_authenticate(user=self.student)
        res = self.client.get('/api/logs/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)  

    def test_supervisor_cannot_see_draft_logs(self):
        
        
        WeeklyLog.objects.create(
            student=self.student,
            placement=self.placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Draft log.',
            status='draft',
        )
        self.client.force_authenticate(user=self.supervisor)
        res = self.client.get('/api/logs/')
        self.assertEqual(len(res.data), 0)  # drafts excluded

    def test_submit_log(self):
       
        log = WeeklyLog.objects.create(
            student=self.student,
            placement=self.placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Test activities.',
        )
        self.client.force_authenticate(user=self.student)
        res = self.client.post(f'/api/logs/{log.id}/submit/')
        self.assertEqual(res.status_code, 200)
        log.refresh_from_db()
        self.assertEqual(log.status, 'submitted')

    def test_supervisor_approves_log(self):
        
        log = WeeklyLog.objects.create(
            student=self.student,
            placement=self.placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Activities.',
            status='submitted',
        )
        self.client.force_authenticate(user=self.supervisor)
        res = self.client.post(f'/api/logs/{log.id}/review/', {
            'action': 'approve',
        })
        self.assertEqual(res.status_code, 200)
        log.refresh_from_db()
        self.assertEqual(log.status, 'approved')

    def test_supervisor_reject_requires_comment(self):
       
        log = WeeklyLog.objects.create(
            student=self.student,
            placement=self.placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Activities.',
            status='submitted',
        )
        self.client.force_authenticate(user=self.supervisor)
        res = self.client.post(f'/api/logs/{log.id}/review/', {
            'action': 'reject',
       
        })
        self.assertEqual(res.status_code, 400)

    def test_cannot_edit_approved_log(self):
      
        log = WeeklyLog.objects.create(
            student=self.student,
            placement=self.placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Activities.',
            status='approved',
        )
        self.client.force_authenticate(user=self.student)
        res = self.client.patch(f'/api/logs/{log.id}/', {
            'activities': 'Changed content.'
        })
        self.assertEqual(res.status_code, 400)


class EvaluationAPITest(TestCase):
    

    def setUp(self):
        self.client = APIClient()
        self.student = make_user('student1', 'student')
        self.academic = make_user('academic1', 'academic')
        self.placement = make_placement(self.student, academic=self.academic)

        self.criteria = EvaluationCriteria.objects.create(
            name='Technical Skills',
            weight=50,
        )
        self.evaluation = Evaluation.objects.create(
            placement=self.placement,
            academic_supervisor=self.academic,
        )

    def test_add_score(self):
      
        self.client.force_authenticate(user=self.academic)
        res = self.client.post(f'/api/evaluations/{self.evaluation.id}/scores/', {
            'criteria': self.criteria.id,
            'score': '8.5',
        })
        self.assertEqual(res.status_code, 201)

    def test_total_computed_after_score(self):
       
        self.client.force_authenticate(user=self.academic)
        self.client.post(f'/api/evaluations/{self.evaluation.id}/scores/', {
            'criteria': self.criteria.id,
            'score': '8',
        })
        self.evaluation.refresh_from_db()
        # (8/10) * 50 = 40.00
        self.assertEqual(float(self.evaluation.total_score), 40.0)

    def test_finalize_evaluation(self):
     
        self.client.force_authenticate(user=self.academic)
        res = self.client.post(f'/api/evaluations/{self.evaluation.id}/finalize/')
        self.assertEqual(res.status_code, 200)
        self.evaluation.refresh_from_db()
        self.assertEqual(self.evaluation.status, 'finalized')

    def test_student_can_view_own_evaluation(self):
     
        self.client.force_authenticate(user=self.student)
        res = self.client.get('/api/evaluations/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


