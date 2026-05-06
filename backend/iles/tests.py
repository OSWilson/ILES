


from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation



def make_user(username, role, **kwargs):
    """Utility function — avoids repeating create_user() in every test."""
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
    """Create a placement with sensible defaults."""
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
    """Tests for the CustomUser model."""

    def test_full_name_with_both_names(self):
        """full_name returns 'First Last' when both are set."""
        user = make_user('alice', 'student')
        user.first_name = 'Alice'
        user.last_name = 'Banda'
        self.assertEqual(user.full_name, 'Alice Banda')

    def test_full_name_falls_back_to_username(self):
        """full_name returns username when names are blank."""
        user = make_user('alice', 'student')
        user.first_name = ''
        user.last_name = ''
        self.assertEqual(user.full_name, 'alice')

    def test_str_representation(self):
        """__str__ shows name and role."""
        user = make_user('bob', 'workplace')
        self.assertIn('workplace', str(user))

    def test_student_number_is_unique(self):
        """Two users cannot share the same student number."""
        from django.db import IntegrityError
        make_user('s1', 'student', student_number='2024/001')
        with self.assertRaises(IntegrityError):
            make_user('s2', 'student', student_number='2024/001')


class PlacementModelTest(TestCase):
    """Tests for InternshipPlacement model validation."""

    def setUp(self):
        """setUp runs before EACH test method — fresh users every time."""
        self.student = make_user('student1', 'student')
        self.today = date.today()

    def test_valid_placement_saves(self):
        """A placement with valid dates saves without error."""
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
        """Student cannot have two placements with overlapping dates."""
        from django.core.exceptions import ValidationError

        # Create first placement
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
    """Tests for WeeklyLog model and its workflow methods."""

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
        """Freshly created log defaults to draft status."""
        log = self._make_log()
        self.assertEqual(log.status, 'draft')

    def test_can_edit_draft(self):
        """Draft logs can be edited."""
        log = self._make_log()
        self.assertTrue(log.can_edit())

    def test_cannot_edit_approved_log(self):
        """Approved logs cannot be edited."""
        log = self._make_log()
        log.approve(self.supervisor)
        self.assertFalse(log.can_edit())

    def test_submit_changes_status(self):
        """Calling submit() changes status to submitted."""
        log = self._make_log()
        log.submit()
        self.assertEqual(log.status, 'submitted')

    def test_approve_changes_status(self):
        """Calling approve() sets status to approved and records reviewer."""
        log = self._make_log()
        log.submit()
        log.approve(self.supervisor)
        log.refresh_from_db()
        self.assertEqual(log.status, 'approved')
        self.assertEqual(log.reviewed_by, self.supervisor)

    def test_reject_changes_status_and_stores_comment(self):
        """Reject sets status to rejected and stores the comment."""
        log = self._make_log()
        log.submit()
        log.reject(self.supervisor, 'Insufficient detail.')
        log.refresh_from_db()
        self.assertEqual(log.status, 'rejected')
        self.assertEqual(log.supervisor_comment, 'Insufficient detail.')

    def test_cannot_submit_already_approved_log(self):
        """Cannot re-submit an approved log."""
        from django.core.exceptions import ValidationError
        log = self._make_log()
        log.submit()
        log.approve(self.supervisor)
        with self.assertRaises(ValidationError):
            log.submit()

    def test_duplicate_week_raises_error(self):
        """Cannot have two logs for the same week in the same placement."""
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
    """Tests for authentication endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user('testuser', 'student')

    def test_login_with_valid_credentials(self):
        """Valid login returns access and refresh tokens."""
        res = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertIn('user', res.data)

    def test_login_with_wrong_password(self):
        """Wrong password returns 401."""
        res = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_creates_user(self):
        """POST /api/auth/register/ creates a new user."""
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
        """Mismatched passwords return 400."""
        res = self.client.post('/api/auth/register/', {
            'username': 'bad',
            'role': 'student',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass!',
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_requires_auth(self):
        """Profile endpoint returns 401 when not logged in."""
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_user_data(self):
        """Authenticated user gets their profile."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'testuser')


class PlacementAPITest(TestCase):
    """Tests for placement endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.student = make_user('student1', 'student')
        self.admin = make_user('admin1', 'admin')
        self.today = date.today()

    def test_student_sees_only_own_placements(self):
        """Student can only list their own placements."""
        
        make_placement(self.student)

        # Create another student with their own placement
        other = make_user('other', 'student')
        make_placement(other)

        self.client.force_authenticate(user=self.student)
        res = self.client.get('/api/placements/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)  # only sees own placement

    def test_admin_creates_placement(self):
        """Admin can create a placement."""
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/placements/', {
            'student': self.student.id,
            'company_name': 'Google Uganda',
            'start_date': str(self.today),
            'end_date': str(self.today + timedelta(weeks=12)),
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_cannot_access(self):
        """Unauthenticated request to placements returns 401."""
        res = self.client.get('/api/placements/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class WeeklyLogAPITest(TestCase):
    """Tests for weekly log endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.student = make_user('student1', 'student')
        self.supervisor = make_user('sup1', 'workplace')
        self.placement = make_placement(self.student, workplace=self.supervisor)

    def test_student_can_create_log(self):
        """
        Reproduces exam Question 8b:
        Student creates a log via POST → expects 201.
        """
        self.client.force_authenticate(user=self.student)
        res = self.client.post('/api/logs/', {
            'week_number': 1,
            'week_start_date': str(date.today()),
            'activities': 'Attended team standup and wrote unit tests.',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WeeklyLog.objects.count(), 1)

    def test_student_cannot_see_other_students_logs(self):
        """
        Reproduces exam Question 8c:
        Student should NOT be able to see all logs — only their own.
        """
        other = make_user('other', 'student')
        other_placement = make_placement(other)

        # Create a log for 'other' student
        WeeklyLog.objects.create(
            student=other,
            placement=other_placement,
            week_number=1,
            week_start_date=date.today(),
            activities='Other student activities.',
        )

        # Log in as our student (not 'other')
        self.client.force_authenticate(user=self.student)
        res = self.client.get('/api/logs/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)  # sees nothing — they have no logs

    def test_supervisor_cannot_see_draft_logs(self):
        """Supervisors should not see logs in draft state."""
        # Create a draft log
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
        """POST to /logs/<id>/submit/ changes status to submitted."""
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
        """Supervisor can approve a submitted log."""
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
        """Rejecting without a comment returns 400."""
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
            # no comment provided
        })
        self.assertEqual(res.status_code, 400)

    def test_cannot_edit_approved_log(self):
        """PATCH on an approved log returns 400."""
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
    """Tests for evaluation endpoints."""

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
        """Academic supervisor can add a score for a criteria."""
        self.client.force_authenticate(user=self.academic)
        res = self.client.post(f'/api/evaluations/{self.evaluation.id}/scores/', {
            'criteria': self.criteria.id,
            'score': '8.5',
        })
        self.assertEqual(res.status_code, 201)

    def test_total_computed_after_score(self):
        """Total score is computed when a score is added."""
        self.client.force_authenticate(user=self.academic)
        self.client.post(f'/api/evaluations/{self.evaluation.id}/scores/', {
            'criteria': self.criteria.id,
            'score': '8',
        })
        self.evaluation.refresh_from_db()
        # (8/10) * 50 = 40.00
        self.assertEqual(float(self.evaluation.total_score), 40.0)

    def test_finalize_evaluation(self):
        """Finalizing evaluation changes status to finalized."""
        self.client.force_authenticate(user=self.academic)
        res = self.client.post(f'/api/evaluations/{self.evaluation.id}/finalize/')
        self.assertEqual(res.status_code, 200)
        self.evaluation.refresh_from_db()
        self.assertEqual(self.evaluation.status, 'finalized')

    def test_student_can_view_own_evaluation(self):
        """Student can read their evaluation but not create/edit."""
        self.client.force_authenticate(user=self.student)
        res = self.client.get('/api/evaluations/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


