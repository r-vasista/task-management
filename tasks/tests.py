from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tasks.models import Project, Task

User = get_user_model()


class AuthenticationApiTests(APITestCase):
    def test_register_and_login(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'BlueCedar!4928',
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)

        response = self.client.post(
            '/api/auth/login/',
            {'username': 'newuser', 'password': 'BlueCedar!4928'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class TaskApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass12345')
        self.other_user = User.objects.create_user(username='other', password='pass12345')
        access_token = str(RefreshToken.for_user(self.owner).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_task_crud_is_limited_to_owner(self):
        other_task = Task.objects.create(owner=self.other_user, title='Private task')

        response = self.client.post('/api/tasks/', {'title': 'Write tests'})
        self.assertEqual(response.status_code, 201)
        task_id = response.data['id']

        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([task['id'] for task in response.data], [task_id])

        response = self.client.get(f'/api/tasks/{other_task.id}/')
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            f'/api/tasks/{task_id}/',
            {'title': 'Tests written', 'status': 'done'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Tests written')

        response = self.client.delete(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_task_rejects_another_users_project(self):
        project = Project.objects.create(owner=self.other_user, name='Private project')

        response = self.client.post(
            '/api/tasks/',
            {'title': "Task in another user's project", 'project': project.id},
        )
        self.assertEqual(response.status_code, 400)

    def test_tasks_require_authentication(self):
        self.client.credentials()

        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 401)